# petal_leafsdk/mission_step_executor.py

import numpy as np
import time
import json
import traceback
import uuid
from typing import Dict, Any, List, Optional, Tuple, Union, Sequence, Literal, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pymavlink import mavutil
from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV

from petal_app_manager.proxies.redis import RedisProxy
from petal_app_manager.proxies.external import MavLinkExternalProxy

from petal_leafsdk.redis_helpers import setup_redis_subscriptions, unsetup_redis_subscriptions
from petal_leafsdk.mavlink_helpers import setup_mavlink_subscriptions, unsetup_mavlink_subscriptions

from leafsdk.core.mission.trajectory import WaypointTrajectory #, TrajectorySampler
from leafsdk import logger
from leafsdk.utils.logstyle import LogIcons
from leafsdk.core.mission.mission_step import (
    Tuple3D, MissionStep, _GotoBase, GotoGPSWaypoint, GotoLocalPosition,
    YawAbsolute, GotoRelative, YawRelative, Takeoff, Wait, Land
)


@dataclass
class StepState:
    completed: bool = False
    paused: bool = False
    canceled: bool = False
    exec_count: int = 0

    def reset(self):
        self.completed = False
        self.paused = False
        self.canceled = False
        self.exec_count = 0


@dataclass
class StepMemory:
    yaw_offset: float = 0.0
    waypoint_offset: Tuple3D = (0.0, 0.0, 0.0)


class MissionStepExecutor(ABC):
    def __init__(self, step: MissionStep):
        self.state = StepState() # Holds the current state of the step
        self.setpoint_offset = StepMemory()
        self.step: MissionStep = step
        self.output = True # Indicates the logical output of the step (mostly used for conditional steps)

        def handler_setpoint(msg: mavutil.mavlink.MAVLink_message) -> bool:
            self.setpoint_offset = StepMemory(yaw_offset=msg.yaw, waypoint_offset=(msg.x, msg.y, msg.z))
            logger.debug(f"{LogIcons.SUCCESS} Received setpoint position: {self.setpoint_offset}")
            return True

        self._handler_setpoint = handler_setpoint

    def reset(self):
        """Reset the executor state for re-execution."""
        self.state.reset()

    def first_exec(self) -> bool:
        """Returns True if this is the first execution of the step logic."""
        return self.state.exec_count == 0
    
    def description(self) -> str:
        """Returns a string description of the step for logging purposes."""
        return self.step.description()
    
    def is_pausable(self) -> bool:
        """Returns True if the step is pausable."""
        return self.step.is_pausable()

    def is_cancelable(self) -> bool:
        """Returns True if the step can be cancelled."""
        return self.step.is_cancelable()
    
    def log_info(self):
        """Log information about the step."""
        self.step.log_info()

    @abstractmethod
    def execute_step_logic(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Execute the logic for the mission step - this is called repeatedly until the step is completed."""
        pass

    def setup(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Setup any resources needed for the step prior to mission plan execution."""
        self.reset()

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Execute one time operations at the start of the step."""
        pass

    def terminate(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Execute one time operations at the end of the step."""
        pass

    def execute_step(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None) -> Tuple[bool, bool]:
        # Check cancellation before executing
        if self.state.canceled or self.state.paused:
            return self.output, self.state.completed

        if self.first_exec():
            self.start(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
            self.log_info()
            self.state.exec_count += 1
        elif not self.state.completed:
            self.execute_step_logic(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
            self.state.exec_count += 1
            if self.state.completed:
                self.terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
                logger.info(f"{LogIcons.SUCCESS} Done: {self.description()} completed!")

        return self.output, self.state.completed

    def pause(self, mission_id, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Pause the step if it is pausable."""
        if self.is_pausable() and not self.state.canceled:
            self.state.paused = True
            self.stop_trajectory(redis_proxy)
            logger.info(f"{LogIcons.PAUSE} Step paused: {self.description()}")
        else:
            logger.warning(f"{LogIcons.WARNING} Step cannot be paused: {self.description()}")

    def stop_trajectory(self, redis_proxy):
        redis_proxy.publish(
                channel="/traj_sys/clear_queue_and_abort_current_trajectory_ori",
                message=json.dumps({"payload": 1})  #TODO this number is used in FC as boolean not int, better to pass True or false
            )
        redis_proxy.publish(
                channel="/traj_sys/generate_stop_traj_on_xyz_plane_from_states_by_deceleration",
                message=json.dumps({"payload": self.step.average_deceleration})
            )

    def resume(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Resume the step if it was paused."""
        if self.state.paused and not self.state.canceled:
            self.state.paused = False
            logger.info(f"{LogIcons.RUN} Step resumed: {self.description()}")
        else:
            logger.warning(f"{LogIcons.WARNING} Step is not paused or has been canceled, cannot resume: {self.description()}")

    def cancel(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """Cancel the step."""
        self.state.canceled = True
        self.terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        logger.info(f"{LogIcons.CANCEL} Step canceled: {self.description()}")


class _GotoExecutor(MissionStepExecutor):
    def __init__(self, step: MissionStep):
        super().__init__(step=step)

        # ---- Internal state ----
        self.yaw_offset = 0.0  # Default yaw offset
        self.waypoint_offset = [0.0, 0.0, 0.0]  # Default position offset
        self.trajectory = None
        self.uuid_str = str(uuid.uuid4())
        self.queued_traj_ids: Dict[str, bool] = {}   # trajectories waiting for completion, value indicates if completed
        self.current_traj_segment: int = 0           # index of segment being processed

    def _handle_notify_trajectory_completed(self, channel: str, message: str) -> None:
        """
        Handle notification messages for trajectory completion.
        This function is triggered asynchronously by the Redis subscriber.

        It parses the message, extracts the trajectory_id, and stores it
        in an internal queue or list for later processing. This function
        must not block.

        Parameters
        ----------
        channel : str
            The Redis channel from which the message was received.
        message : str
            The message content, expected to be a JSON string with trajectory details.
        """
        logger.info(f"{LogIcons.SUCCESS} Received notification on {channel}: {message}")

        try:
            command_data = json.loads(message)
            traj_id = command_data.get("trajectory_id")

            if traj_id:
                self.queued_traj_ids[traj_id] = True
                logger.info(f"{LogIcons.SUCCESS} Trajectory completed: {traj_id}")
            else:
                logger.warning(f"{LogIcons.WARNING} Received notification without trajectory_id: {message}")
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error parsing completion notification: {e}")

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        setup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_SETPOINT_OFFSET),
            callback=self._handler_setpoint,
            duplicate_filter_interval=0.7,
            mav_proxy=mav_proxy
        )
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        try:
            logger.info(f"{LogIcons.WARNING} setpoint data:  {self.__class__.__name__}: {self.setpoint_offset}")

            # Compute trajectory once
            self.pos_traj_ids, self.pos_traj_json, self.yaw_traj_ids, self.yaw_traj_json = self._compute_trajectory(
                                                                                                self.step.waypoints,
                                                                                                self.step.yaws_deg,
                                                                                                self.step.speed,
                                                                                                self.step.yaw_speed,
                                                                                                home=self.setpoint_offset.waypoint_offset,
                                                                                                home_yaw=self.setpoint_offset.yaw_offset,
                                                                                                cartesian=self.step.cartesian,
                                                                                            )
            
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error computing trajectory: {e}")
            logger.error(traceback.format_exc())
            raise e

    def execute_step_logic(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        """
        Execute mission step logic for sequential trajectory publishing.
        This function is designed to be called periodically (non-blocking).
        """
        total_segments = len(self.pos_traj_json)

        # If there are no uncompleted trajectories, publish next segment
        if all(list(self.queued_traj_ids.values())) and self.current_traj_segment < total_segments:
            self._publish_trajectory_segment(
                idx=self.current_traj_segment,
                pos_traj_seg=self.pos_traj_json[self.current_traj_segment],
                yaw_traj_seg=self.yaw_traj_json[self.current_traj_segment],
                pos_traj_id=self.pos_traj_ids[self.current_traj_segment],
                yaw_traj_id=self.yaw_traj_ids[self.current_traj_segment],
                redis_proxy=redis_proxy
            )
            self.current_traj_segment += 1
        elif all(list(self.queued_traj_ids.values())) and self.current_traj_segment >= total_segments:
            self.state.completed = True

    def terminate(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        unsetup_mavlink_subscriptions(
            key=str(leafMAV.MAVLINK_MSG_ID_LEAF_SETPOINT_OFFSET),
            callback=self._handler_setpoint,
            mav_proxy=mav_proxy
        )
        unsetup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", redis_proxy=redis_proxy)

    def _compute_trajectory(    # TODO make all parameters either degree or radians
        self,
        waypoints: Sequence[Tuple[float, float, float]],
        yaws_deg: Sequence[float],
        speed: Sequence[float],
        yaw_speed: Union[Sequence[float], Literal["sync"]],
        home: Tuple[float, float, float],
        home_yaw: float,
        cartesian: bool,
        is_yaw_relative: Optional[bool] = False,
    ) ->  Tuple[List[str], List[Optional[str]], List[str], List[Optional[str]]]:
        """
        Compute the trajectory for the given waypoints and yaws.
        This function generates trajectory JSON files for each segment
        and returns their identifiers.
        
        Parameters
        ----------
        waypoints : Sequence[Tuple[float, float, float]]
            List of waypoints as (lat, lon, alt) or (x, y, z).
        yaws_deg : Sequence[float]
            List of yaw commands in degrees at each waypoint.
        speed : Sequence[float]
            List of speeds (m/s) for each segment.
        yaw_speed : Sequence[float] or str
            List of yaw speeds (deg/s) for each segment, or 'sync' to match position trajectory.
        home : Tuple[float, float, float]
            Home position reference (lat, lon, alt) or (x, y, z).
        home_yaw : float
            Home yaw reference in radians.
        cartesian : bool
            If True, waypoints are in Cartesian coordinates; if False, GPS coordinates.
        is_yaw_relative : bool
            If True, interpret yaws as relative changes; otherwise absolute.

        Returns
        -------
        pos_traj_ids : List[str]
            List of position trajectory segment identifiers.
        pos_traj_json : List[Optional[str]]
            List of position trajectory JSON strings (None if static).
        yaw_traj_ids : List[str]
            List of yaw trajectory segment identifiers.
        yaw_traj_json : List[Optional[str]]
            List of yaw trajectory JSON strings (None if static).
        """

        # Create trajectory json files for each segment based on the waypoints and yaws
        self.trajectory = WaypointTrajectory(
            waypoints=waypoints,
            yaws_deg=yaws_deg,
            speed=speed,
            yaw_speed=yaw_speed,
            home=home,
            home_yaw=home_yaw,
            cartesian=cartesian,
            is_yaw_relative=is_yaw_relative
        )
        
        pos_traj_ids, pos_traj_json = self.trajectory.build_pos_polynomial_trajectory_json(self.uuid_str)
        yaw_traj_ids, yaw_traj_json = self.trajectory.build_yaw_polynomial_trajectory_json(self.uuid_str)

        return pos_traj_ids, pos_traj_json, yaw_traj_ids, yaw_traj_json

    def _publish_trajectory_segment(
        self,
        idx: int,
        pos_traj_seg: str,
        yaw_traj_seg: str,
        pos_traj_id: str,
        yaw_traj_id: str,
        redis_proxy: RedisProxy = None
    ) -> None:
        """
        Publish a single trajectory segment (position and/or yaw) to Redis.

        This function does not block or wait for completion. Completion is
        handled asynchronously via `_handle_notify_trajectory_completed`.

        Parameters
        ----------
        idx : int
            Segment index (0-based).
        pos_traj_seg : str or None
            JSON string for the position trajectory segment, or None if static.
        yaw_traj_seg : str or None
            JSON string for the yaw trajectory segment, or None if static.
        pos_traj_id : str or None
            Identifier for the position trajectory segment.
        yaw_traj_id : str or None
            Identifier for the yaw trajectory segment.
        """
        try:
            if redis_proxy is None:
                logger.warning(f"{LogIcons.WARNING} Redis proxy not available, skipping trajectory publication")
                return

            # Skip publishing if both are None
            if pos_traj_seg is None and yaw_traj_seg is None:
                logger.warning(
                    f"{LogIcons.WARNING} Both position and yaw trajectory segments are static, "
                    f"skipping publication for segment {idx+1}"
                )
                return

            # Publish position trajectory
            if pos_traj_seg is not None:
                redis_proxy.publish(
                    channel="/traj_sys/queue_traj_primitive_pos",
                    message=pos_traj_seg,
                )
                self.queued_traj_ids[pos_traj_id] = False
                logger.info(f"{LogIcons.SUCCESS} Position trajectory segment {idx+1} published to Redis successfully")

            # Publish yaw trajectory
            if yaw_traj_seg is not None:
                redis_proxy.publish(
                    channel="/traj_sys/queue_traj_primitive_ori",
                    message=yaw_traj_seg,
                )
                self.queued_traj_ids[yaw_traj_id] = False
                logger.info(f"{LogIcons.SUCCESS} Yaw trajectory segment {idx+1} published to Redis successfully")

        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error publishing trajectory segment {idx+1}: {e}")


class GotoGPSWaypointExecutor(_GotoExecutor):
    def __init__(self, step: GotoGPSWaypoint):
        super().__init__(step=step)


class GotoLocalPositionExecutor(_GotoExecutor):
    def __init__(self, step: GotoLocalPosition):
        super().__init__(step=step)


class GotoRelativeExecutor(_GotoExecutor):
    def __init__(self, step: GotoRelative):
        super().__init__(step=step)

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        try:
            # Cumulative sum the relative points to get absolute waypoints
            waypoints = np.cumsum(self.step.waypoints, axis=0) + self.setpoint_offset.waypoint_offset

            logger.debug(f"{LogIcons.WARNING} Using waypoint offset: {self.setpoint_offset.waypoint_offset} and yaw offset: {self.setpoint_offset.yaw_offset}")

            # Compute trajectory once
            self.pos_traj_ids, self.pos_traj_json, self.yaw_traj_ids, self.yaw_traj_json = self._compute_trajectory(
                                                                                                waypoints,
                                                                                                self.step.yaws_deg,
                                                                                                self.step.speed,
                                                                                                self.step.yaw_speed,
                                                                                                home=self.setpoint_offset.waypoint_offset,
                                                                                                home_yaw=self.setpoint_offset.yaw_offset,
                                                                                                cartesian=self.step.cartesian,
                                                                                                is_yaw_relative=True,
                                                                                            )
            
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error computing trajectory: {e}")
            logger.error(traceback.format_exc())
            raise e
        

class YawAbsoluteExecutor(_GotoExecutor):
    def __init__(self, step: YawAbsolute):
        super().__init__(step=step)

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        try:
            logger.debug(f"{LogIcons.WARNING} Using waypoint offset: {self.setpoint_offset.waypoint_offset} and yaw offset: {self.setpoint_offset.yaw_offset}")

            waypoints = self.step.waypoints + np.asarray(self.setpoint_offset.waypoint_offset)

            # Compute trajectory once
            self.pos_traj_ids, self.pos_traj_json, self.yaw_traj_ids, self.yaw_traj_json = self._compute_trajectory(
                                                                                                waypoints,
                                                                                                self.step.yaws_deg,
                                                                                                self.step.speed,
                                                                                                self.step.yaw_speed,
                                                                                                home=self.setpoint_offset.waypoint_offset,
                                                                                                home_yaw=self.setpoint_offset.yaw_offset,
                                                                                                cartesian=self.step.cartesian,
                                                                                            )

        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error computing trajectory: {e}")
            logger.error(traceback.format_exc())
            raise e


class YawRelativeExecutor(_GotoExecutor):
    def __init__(self, step: YawRelative):
        super().__init__(step=step)

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        try:            
            logger.debug(f"{LogIcons.WARNING} Using waypoint offset: {self.setpoint_offset.waypoint_offset} and yaw offset: {self.setpoint_offset.yaw_offset}")

            waypoints = self.step.waypoints + np.asarray(self.setpoint_offset.waypoint_offset)
            # Compute trajectory once
            self.pos_traj_ids, self.pos_traj_json, self.yaw_traj_ids, self.yaw_traj_json = self._compute_trajectory(
                                                                                                waypoints,
                                                                                                self.step.yaws_deg,
                                                                                                self.step.speed,
                                                                                                self.step.yaw_speed,
                                                                                                home=self.setpoint_offset.waypoint_offset,
                                                                                                home_yaw=self.setpoint_offset.yaw_offset,
                                                                                                cartesian=self.step.cartesian,
                                                                                                is_yaw_relative=True
                                                                                            )
            
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error computing trajectory: {e}")
            logger.error(traceback.format_exc())
            raise e


class TakeoffExecutor(MissionStepExecutor):
    def __init__(self, step: Takeoff):
        super().__init__(step=step)

    def setup(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        super().setup(mav_proxy=mav_proxy, redis_proxy=redis_proxy)

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_takeoff_message(
                target_system=mav_proxy.target_system,
                altitude=self.step.alt
            )
            mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        else:
            logger.warning(f"{LogIcons.WARNING} MavLinkExternalProxy is not provided, cannot send takeoff message.")

    def execute_step_logic(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None) -> None:
        logger.info(f"{LogIcons.SUCCESS} setpoint data:  {self.__class__.__name__}: {self.setpoint_offset}")
        logger.info(f"{LogIcons.WARNING} Takeoff with waypoint offset: {self.setpoint_offset.waypoint_offset} and yaw offset: {self.setpoint_offset.yaw_offset}")
        self.state.completed = True


class WaitExecutor(MissionStepExecutor):
    def __init__(self, step: Wait):
        super().__init__(step=step)

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        self.tick = time.time()

    def execute_step_logic(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        elapsed_time = time.time() - self.tick
        if elapsed_time >= self.step.duration:
            self.state.completed = True
    

class LandExecutor(MissionStepExecutor):
    def __init__(self, step: Land):
        super().__init__(step=step)
        self._landed = False

    def _handle_notify_trajectory_completed(self, channel: str, message: str) -> None:
        """
        Handle notification messages for landing trajectory completion.

        Parameters
        ----------
        channel : str
            The Redis channel from which the message was received.
        message : str
            The message content, expected to be a JSON string with trajectory details.
        """
        logger.info(f"{LogIcons.SUCCESS} Received notification on {channel}: {message}")

        try:
            command_data = json.loads(message)
            traj_id = command_data.get("trajectory_id")

            if "land" in traj_id:
                # For Land step, we can directly mark completed on any trajectory completion
                self._landed = True
                logger.info(f"{LogIcons.SUCCESS} Trajectory completed: {traj_id}")
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Error parsing completion notification: {e}")

    def start(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        super().start(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        setup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", callback=self._handle_notify_trajectory_completed, redis_proxy=redis_proxy)
        if mav_proxy is not None:
            msg = leafMAV.MAVLink_leaf_do_land_message(
                target_system=mav_proxy.target_system,
            )
            mav_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
        else:
            logger.warning(f"{LogIcons.WARNING} MavLinkExternalProxy is not provided, cannot send land message.")

    def execute_step_logic(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None) -> None:
        if self._landed:
            self.state.completed = True

    def terminate(self, mav_proxy: MavLinkExternalProxy = None, redis_proxy: RedisProxy = None):
        super().terminate(mav_proxy=mav_proxy, redis_proxy=redis_proxy)
        unsetup_redis_subscriptions(pattern="/petal-leafsdk/notify_trajectory_completed", redis_proxy=redis_proxy)
        self._landed = False
    

def get_mission_step_executor(step: MissionStep) -> MissionStepExecutor:
    """Factory method to get the appropriate MissionStepExecutor for a given MissionStep."""
    if isinstance(step, GotoGPSWaypoint):
        return GotoGPSWaypointExecutor(step=step)
    elif isinstance(step, GotoLocalPosition):
        return GotoLocalPositionExecutor(step=step)
    elif isinstance(step, GotoRelative):
        return GotoRelativeExecutor(step=step)
    elif isinstance(step, YawAbsolute):
        return YawAbsoluteExecutor(step=step)
    elif isinstance(step, YawRelative):
        return YawRelativeExecutor(step=step)
    elif isinstance(step, Takeoff):
        return TakeoffExecutor(step=step)
    elif isinstance(step, Wait):
        return WaitExecutor(step=step)
    elif isinstance(step, Land):
        return LandExecutor(step=step)
    else:
        raise ValueError(f"Unsupported MissionStep type: {type(step)}")