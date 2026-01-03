# petal_leafsdk/mission_plan_executor.py
import json
import json
from typing import Optional, Literal
import traceback
from dataclasses import dataclass
import networkx as nx
from enum import Enum, auto

from leafsdk.core.mission.mission_plan import MissionPlan
from leafsdk.utils.logstyle import LogIcons
from leafsdk import logger

from petal_leafsdk.mission_step_executor import get_mission_step_executor
from petal_leafsdk.mission_step_executor import get_mission_step_executor

from petal_app_manager.proxies.external import MavLinkExternalProxy
from petal_app_manager.proxies.redis import RedisProxy
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV



class MissionPlanExecutor:
    def __init__(self, plan: MissionPlan, mav_proxy: MavLinkExternalProxy, redis_proxy: RedisProxy):
        self.plan = plan
        self.execution_graph = self.get_execution_graph(plan)
        self.mav_proxy = mav_proxy
        self.redis_proxy = redis_proxy

        self._mission_status = MissionStatus()
        self._current_step = None
        self._current_node = None
        self._mission_control_cmd: MissionControlCommand = MissionControlCommand.NONE

    def get_execution_graph(self, plan: MissionPlan) -> nx.MultiDiGraph:
        """Generate the execution graph from the mission plan."""
        graph = plan.mission_graph.copy()
        # Traverse and replace steps with their executors
        for name, data in graph.nodes(data=True):
            step = data['step']
            executor = get_mission_step_executor(step)
            graph.nodes[name]['step'] = executor
        return graph
    

    def load_plan(self, data: dict | str):
        """Load a new mission plan."""
        self.plan.load(data)
        self.execution_graph = self.get_execution_graph(self.plan)
        logger.info(f"{LogIcons.SUCCESS} Mission plan loaded successfully.")


    def run_step(self):
        """Execute the current mission step.
        
        Returns:
            dict: Current mission status after executing the step.
            Keys include:
                - step_id
                - step_description
                - next_step_id
                - next_step_description
                - step_completed
                - state
        """
        if self._mission_status.state == MissionState.CANCELLED:
            return self._mission_status.as_dict()
        elif self._mission_control_cmd == MissionControlCommand.CANCEL:
            if self._mission_status.state in [MissionState.RUNNING, MissionState.PAUSED]:
                self._canceled()
                return self._mission_status.as_dict()

        elif self._mission_control_cmd == MissionControlCommand.RESUME:
            if self._mission_status.state == MissionState.PAUSED:
                self._mission_status.state = MissionState.RUNNING
                self._mission_control_cmd = MissionControlCommand.NONE

        elif self._mission_status.state == MissionState.PAUSED:
            return self._mission_status.as_dict()
        elif self._mission_control_cmd == MissionControlCommand.PAUSE_NOW:
            if self._mission_status.state == MissionState.RUNNING:
                self._paused()
                return self._mission_status.as_dict()

        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot run step: no current step available")
            self._mission_status.reset()
            return self._mission_status.as_dict()

        if self._current_step.first_exec():
            logger.info(f"{LogIcons.RUN} Executing step: {self._current_node}")

        try:
            result, completed = self._current_step.execute_step(mav_proxy=self.mav_proxy, redis_proxy=self.redis_proxy)
        except Exception as e:
            self._failed(e)
            return self._mission_status.as_dict()

        if completed:
            logger.info(f"Step {self._current_step.description()} Completed")
            prev_node = self._current_node
            self._current_node = self._get_next_node(result)

            if self._current_node is None:
                self._completed(prev_node)
                return self._mission_status.as_dict()
            else:
                if self._mission_control_cmd == MissionControlCommand.PAUSE_LATER:
                    self._paused()
                    logger.info(f"Mission paused after completetion of step: {self._current_node}")
                    return self._mission_status.as_dict()

                # Update current step to the next node immediately
                self._current_step = self.execution_graph.nodes[self._current_node]['step']
                self._mission_status.step_transition(prev_node, self._current_node, self.execution_graph)
                return self._mission_status.as_dict()

        self._mission_status.running(self._current_node, self.execution_graph)
        return self._mission_status.as_dict()


    def _get_next_node(self, result) -> Optional[str]:
        """Determine the next node based on current node and conditions."""
        next_node = None
        for successor in self.execution_graph.successors(self._current_node):
            condition = self.execution_graph.edges[self._current_node, successor, 0].get("condition")
            if condition is None or condition == result:
                next_node = successor
                break
        return next_node


    def prepare(self) -> bool:
        """Prepare the mission plan for execution."""
        try:
            self.plan.validate()
            self._current_node = self.plan._head_node
            self._current_step = self.execution_graph.nodes[self._current_node]['step']
            for name, _ in self.plan._get_steps():
                step = self.execution_graph.nodes[name]['step']
                step.setup(mav_proxy=self.mav_proxy, redis_proxy=self.redis_proxy)
            self._mission_control_cmd = MissionState.RUNNING

            # Send joystick enable/disable command
            joystick_mode_map = {
                "disabled": 0,
                "enabled": 1,
                "enabled_on_pause": 2
            }
            joystick_cmd = joystick_mode_map.get(self.plan.config.joystick_mode.value, 1) # Default to ENABLED if unknown
            self.redis_proxy.publish(
                channel="/FlightLogic/joystick_mode",
                message=json.dumps({"payload": joystick_cmd})
            )
            logger.info(f"{LogIcons.SUCCESS} Joystick control set to {self.plan.config.joystick_mode.value.upper()}.")
            logger.info(f"{LogIcons.SUCCESS} Mission plan has been prepared and ready for execution.")
            return True
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Mission plan preparation failed: {e}")
            logger.error(traceback.format_exc())
            return False
    

    def pause(self, action: Optional[Literal["NONE"]] = "NONE"):
        """Pause the mission execution."""
        logger.info(f"{LogIcons.RUN} Mission pause commanded.")

        if self._mission_status.state != MissionState.RUNNING:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be paused, current state: {self._mission_status.state.name}.")
            return False

        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot pause, no current step to pause.")
            return False

        if self.mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot pause, MAVLink proxy is required.")
            return False

        if self._current_step.is_pausable():
            self._mission_control_cmd = MissionControlCommand.PAUSE_NOW
            logger.info(f"{LogIcons.RUN} Mission will be paused Immediately")
        else:
            self._mission_control_cmd = MissionControlCommand.PAUSE_LATER
            logger.info(f"{LogIcons.RUN} Mission will pause after the step is completed.")

        return True


    def resume(self):
        """Resume the mission execution."""
        if self._mission_status.state != MissionState.PAUSED:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be resumed, current state: {self._mission_status.state.name}.")
            return False
        
        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot resume, no current step to resume.")
            return False

        if self.mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot resume, MAVLink proxy is required.")
            return False
        
        self._current_step.resume()
        self._mission_control_cmd = MissionControlCommand.RESUME

        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=self.mav_proxy.target_system,
                            cmd=1,
                            action=0,
                            mission_id=self.plan.id.encode('ascii')  # Use unique mission ID for tracking
                        )
        self.mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        logger.info(f"{LogIcons.RUN} Mission resume commanded.")
        
        return True
    

    def cancel(self, action: Optional[Literal["NONE", "HOVER", "RETURN_TO_HOME", "LAND_IMMEDIATELY"]] = "HOVER"):
        # Map action strings to command codes
        action_map = {
            "NONE": 0,
            "HOVER": 1,
            "RETURN_TO_HOME": 2,
            "LAND_IMMEDIATELY": 3
        }
        action_code = action_map.get(action, 1)  # Default to HOVER if invalid action

        """Cancel the mission execution completely."""
        if self._mission_status.state != MissionState.RUNNING and self._mission_status.state != MissionState.PAUSED:
            logger.warning(f"{LogIcons.WARNING} Mission cannot be canceled, current state: {self._mission_status.state.name}.")
            return False
        
        if self._current_step is None:
            logger.warning(f"{LogIcons.WARNING} Cannot cancel, no current step to cancel.")
            return False
        
        if self._current_step.is_cancelable() is False:
            logger.warning(f"{LogIcons.WARNING} Current step does not support cancellation: {self._current_node}.")
            return False

        if self.mav_proxy is None:
            logger.warning(f"{LogIcons.WARNING} Cannot cancel, MAVLink proxy is required.")
            return False

        self._mission_control_cmd = MissionControlCommand.CANCEL
        
        # Send MAVLink cancel command
        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                            target_system=self.mav_proxy.target_system,
                            cmd=2,
                            action=action_code,
                            mission_id=self.plan.id.encode('ascii')  # Use unique mission ID for tracking
                        )
        self.mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        logger.info(f"{LogIcons.RUN} Mission cancel commanded with action: {action}.")

        return True


    def abort(self):
        """Abort the mission immediately without any graceful shutdown."""
        self._mission_control_cmd = MissionControlCommand.CANCEL

        logger.info(f"{LogIcons.CANCEL} Mission aborted immediately.")


    def _completed(self, prev_node: str=None):
        """Handle mission completion procedures."""
        state_change_flag = self._mission_status.completed(prev_node, self.execution_graph)
        self._mission_control_cmd = MissionState.COMPLETED
        self._current_step = None
        if state_change_flag:
            logger.info(f"{LogIcons.SUCCESS} Mission complete.")

    def _failed(self, e: Exception):
        """Handle mission failure procedures."""
        state_change_flag = self._mission_status.failed(self._current_node, self.execution_graph)
        self._mission_control_cmd = MissionState.FAILED
        self._current_node = None
        self._current_step = None
        if state_change_flag:
            logger.error(f"{LogIcons.ERROR} Step {self._current_node} failed: {e}\n{traceback.format_exc()}")

    def _send_pause_to_FC(self) -> None:
        action_map = {
            "NONE": 0
        }
        action_code = action_map.get("NONE", 0)  # Default to HOVER if invalid action
        msg = leafMAV.MAVLink_leaf_control_cmd_message(
                                        target_system=self.mav_proxy.target_system,
                                        cmd=0,
                                        action=action_code,
                                        mission_id=self.plan.id.encode('ascii')
                                    )
        self.mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)

    def _paused(self):
        """Internal method to perform pause procedures."""
        state_change_flag = self._mission_status.paused(self._current_node, self.execution_graph)
        if state_change_flag:
            self._current_step.pause(self.plan.id.encode('ascii'), mav_proxy=self.mav_proxy, redis_proxy=self.redis_proxy)
            self._send_pause_to_FC()
            logger.info(f"{LogIcons.PAUSE} Mission paused at step: {self._current_node}")

    def _canceled(self):
        """Internal method to perform cancellation procedures."""
        state_change_flag = self._mission_status.canceled(self._current_node, self.execution_graph)
        if state_change_flag:
            self._current_step.cancel(mav_proxy=self.mav_proxy, redis_proxy=self.redis_proxy)
            logger.info(f"{LogIcons.CANCEL} Mission cancelled at step: {self._current_node}")
            self._current_node = None
            self._current_step = None


    def reset(self):
        """Reset the mission plan executor to its initial state."""
        self.plan.reset()
        self._mission_status.reset()
        self._current_step = None
        self._current_node = None
        self._mission_control_cmd = None
        logger.info(f"{LogIcons.SUCCESS} MissionPlanExecutor has been reset.")


class MissionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    CANCELLED = auto()
    COMPLETED = auto()
    FAILED = auto()

    def __str__(self):
        return self.name


class MissionControlCommand(Enum):
    NONE = auto()
    PAUSE_NOW = auto()
    PAUSE_LATER = auto()
    RESUME = auto()
    CANCEL = auto()

    def __str__(self):
        return self.name


@dataclass
class MissionStatus:
    step_id: Optional[str] = None
    step_description: Optional[str] = None
    next_step_id: Optional[str] = None
    next_step_description: Optional[str] = None
    step_completed: bool = False
    state: MissionState = MissionState.IDLE


    def as_dict(self) -> dict:
        """Return a serializable dictionary for external systems."""
        data = self.__dict__.copy()
        data["state"] = str(self.state)  # convert enum to string
        return data

    def reset(self):
        self.step_id = None
        self.step_description = None
        self.next_step_id = None
        self.next_step_description = None
        self.step_completed = False
        self.state = MissionState.IDLE


    def set_step(self, node: str, graph: nx.MultiDiGraph):
        self.step_id = str(node)
        self.step_description = graph.nodes[node]['step'].description()
    

    def set_next_step(self, node: str, graph: nx.MultiDiGraph):
        self.next_step_id = str(node)
        self.next_step_description = graph.nodes[node]['step'].description()


    def completed(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.COMPLETED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state
    

    def step_transition(self, prev_node: str, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.RUNNING
        self.step_completed = True
        self.set_step(prev_node, graph)
        self.set_next_step(node, graph)
        return _state != self.state


    def running(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.RUNNING
        self.set_step(node, graph)
        return _state != self.state


    def paused(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.PAUSED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state


    def canceled(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.CANCELLED
        self.step_completed = True
        self.set_step(node, graph)
        return _state != self.state


    def failed(self, node: str, graph: nx.MultiDiGraph) -> bool:
        _state = self.state
        self.reset()
        self.state = MissionState.FAILED
        self.set_step(node, graph)
        return _state != self.state