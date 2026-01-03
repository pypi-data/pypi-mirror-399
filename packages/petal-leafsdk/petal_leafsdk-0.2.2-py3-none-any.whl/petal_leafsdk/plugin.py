# petal-leafsdk/plugin.py
# Petal plugin for Leaf SDK integration and mission planning

import time
from . import logger

from typing import Any, Dict
import asyncio, httpx
import traceback

from pymavlink.dialects.v20 import droneleaf_mav_msgs as leafMAV
from pymavlink import mavutil

from petal_app_manager.plugins.base import Petal
from petal_app_manager.plugins.decorators import http_action
from petal_app_manager.proxies import (
    MQTTProxy,
    MavLinkExternalProxy,
    RedisProxy
)

from petal_leafsdk.data_model import CancelMissionRequest, MissionGraph, ProgressUpdateSubscription, SafeReturnPlanRequestAddress
from petal_leafsdk.mission_plan_executor import MissionPlanExecutor, MissionState

# Mission imports
from leafsdk.core.mission.mission_clock import MissionClock
from leafsdk.core.mission.mission_plan import MissionPlan
from leafsdk.utils.logstyle import LogIcons


class PetalMissionPlanner(Petal):
    name = "petal-mission-planner"
    version = "v0.1.0"
    use_mqtt_proxy = True  # Enable MQTT-aware startup

    def startup(self):
        super().startup()
        self.running = False
        self.mission_ready = False
        self.mission_clock = None
        self.mission_plan = None
        self.subscriber_address = None # For progress updates
        self.safe_return_waypoint_request_address = None # For safe return waypoint requests
        self.redis_proxy: RedisProxy = self._proxies.get("redis")  # Get the Redis proxy instance
        self.mqtt_proxy: MQTTProxy = self._proxies.get("mqtt") # Get the MQTT proxy instance
        self.mqtt_subscription_id = None

        self._setup_mavlink_handlers()
        self._init_mavlink_and_mission()
        self.mission_executor = MissionPlanExecutor(self.mission_plan, self.mavlink_proxy, self.redis_proxy)

        self.loop = asyncio.get_event_loop()  # store loop reference

    def _setup_mavlink_handlers(self):
        self._mavlink_handlers = {}

        def _handler_mavlink_mission_run_ack(msg: mavutil.mavlink.MAVLink_message) -> bool:
            """Called when the FC acknowledges mission start."""
            if self.running:
                logger.warning(f"{LogIcons.WARNING} Mission already running — ignoring duplicate run ACK.")
                return True
            elif not self.mission_ready:
                logger.warning(f"{LogIcons.WARNING} There is no mission ready to start.")
                return True
            try:
                logger.info(f"{LogIcons.SUCCESS} Received MAVLink mission run acknowledgment from flight controller.")
                self.running = True

                # Schedule on stored event loop safely, even from another thread
                self.loop.call_soon_threadsafe(lambda: asyncio.create_task(self.mission_loop()))
            except Exception as e:
                logger.error(f"{LogIcons.ERROR} Failed to start mission loop: {e}, trace: {traceback.format_exc()}")
            
            return True
        
        def _handler_mavlink_qgc_control_cmd(msg: mavutil.mavlink.MAVLink_message) -> bool:
            control_cmd_name = leafMAV.enums['LEAF_CONTROL_COMMAND'][msg.cmd].name
            logger.info(f"{LogIcons.SUCCESS} Received QGC control command: {control_cmd_name}")

            if control_cmd_name == "LEAF_CONTROL_PAUSE":
                self.pause()
            elif control_cmd_name == "LEAF_CONTROL_RESUME":
                self.resume()
            elif control_cmd_name == "LEAF_CONTROL_CANCEL":
                self.cancel(action="HOVER")
            
            return True
        
        def _handler_mavlink_ack_mission_abort(msg: mavutil.mavlink.MAVLink_message) -> bool:
            """Handle abort acknowledgment."""
            logger.info(f"{LogIcons.SUCCESS} Received MAVLink mission abort acknowledgment from flight controller.")
            if self.running:
                self.abort()
            else:
                logger.info(f"{LogIcons.RUN} No active mission — resetting mission plan.")
            self._reset_mission()

            return True
        
        def _handler_mavlink_ack_mission_resume(msg: mavutil.mavlink.MAVLink_message) -> bool:
            """Handle resume acknowledgment."""
            logger.info(f"{LogIcons.SUCCESS} Received MAVLink mission resume acknowledgment from flight controller.")
            return True
        
        self._mavlink_handlers[str(leafMAV.MAVLINK_MSG_ID_LEAF_ACK_MISSION_RUN)] = _handler_mavlink_mission_run_ack
        self._mavlink_handlers[str(leafMAV.MAVLINK_MSG_ID_LEAF_QGC_CONTROL_CMD)] = _handler_mavlink_qgc_control_cmd
        self._mavlink_handlers[str(leafMAV.MAVLINK_MSG_ID_LEAF_ACK_MISSION_ABORT)] = _handler_mavlink_ack_mission_abort
        self._mavlink_handlers[str(leafMAV.MAVLINK_MSG_ID_LEAF_ACK_MISSION_RESUME)] = _handler_mavlink_ack_mission_resume

    def _init_mavlink_and_mission(self):
        logger.info(f"{LogIcons.RUN} Initializing MAVLink connection via proxy...")
        # Use the external MAVLink proxy if available
        self.mavlink_proxy: MavLinkExternalProxy = self._proxies.get("ext_mavlink")
        self.mission_clock = MissionClock(rate_hz=50)
        self.mission_plan = MissionPlan(name="main")
        logger.info(f"{LogIcons.SUCCESS} MAVLink initialized and mission plan ready.")
        
        for key, handler in self._mavlink_handlers.items():
            self.mavlink_proxy.register_handler(
                key=key,
                fn=handler,
                duplicate_filter_interval=0.7
            )

    async def async_startup(self):
        """
        Called after startup to handle async operations like MQTT subscriptions.
        
        Note: The MQTT-aware startup logic (organization ID monitoring, event loop setup)
        is handled by the main application's _mqtt_aware_petal_startup function.
        This method will be called by that function after organization ID is available.
        """
        # This method is intentionally simple - the main app handles:
        # 1. Setting self._loop
        # 2. Waiting for organization ID
        # 3. Calling self._setup_mqtt_topics() when ready
        # 4. Starting organization ID monitoring if needed
        
        logger.info("{LogIcons.RUN} Performing MQTT-aware async startup...")
        pass     

    async def _setup_mqtt_topics(self):
        logger.info(f"{LogIcons.RUN} Setting up MQTT topics...")
        await self._mqtt_subscribe_to_mission_plan()
        logger.info(f"{LogIcons.SUCCESS} All MQTT topics active")

    async def run_mission(self, mission_graph: dict):
        try:
            self.mission_executor.reset()
            self.mission_executor.load_plan(mission_graph)
            logger.info(f"{LogIcons.RUN} Loading mission: {self.mission_plan.name}")
            self.mission_ready = self.mission_executor.prepare()

            if self.mission_ready:
                logger.info(f"{LogIcons.SUCCESS} Mission '{self.mission_plan.name}' loaded and ready.")
                # Send mission run message
                msg = leafMAV.MAVLink_leaf_do_mission_run_message(
                    target_system=self.mavlink_proxy.target_system,
                    mission_id=self.mission_plan.id.encode("ascii"),
                    forced=0
                )
                self.mavlink_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
                # Wait for MAVLink ACK (non-blocking)
                logger.info(f"{LogIcons.RUN} Sent mission run request — awaiting ACK to start execution...")
            else:
                logger.error(f"{LogIcons.ERROR} Mission '{self.mission_plan.name}' failed to prepare.")
                return

        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Mission run request error: {e}")
            logger.error(traceback.format_exc())

    async def _wait_for_mission_ack(self, timeout: float = 20.0):
        start = time.monotonic()
        while not self.running and (time.monotonic() - start < timeout):
            await asyncio.sleep(0.1)

    async def mission_loop(self):
        """Main mission execution loop — started when ACK is received."""
        logger.info(f"{LogIcons.RUN} Mission loop started.")
        try:
            while self.running:
                self.mission_clock.tick()
                status = self.mission_executor.run_step()
                self.running = status["state"] in (str(MissionState.RUNNING), str(MissionState.PAUSED))

                if status["step_completed"]:
                    await self.publish_status_update(status)

                await self.mission_clock.tock(blocking=False)
            self.mission_ready = False
        except Exception as e:
            self.cancel(action="HOVER")
            logger.error(f"{LogIcons.ERROR} Mission execution error: {e}, trace: {traceback.format_exc()}")

        logger.info(f"{LogIcons.SUCCESS} Mission completed with final status: {status['state'].name}")

        # Send mission done message when loop exits
        msg = leafMAV.MAVLink_leaf_done_mission_run_message(
            target_system=self.mavlink_proxy.target_system,
            mission_id=self.mission_plan.id.encode("ascii"),
        )
        self.mavlink_proxy.send(key='mav', msg=msg, burst_count=4, burst_interval=0.1)
    
    async def publish_status_update(self, status: dict):
        if self.subscriber_address:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        self.subscriber_address,
                        json=status,
                        headers={"Content-Type": "application/json"},
                    )
            except Exception as e:
                logger.warning(f"{LogIcons.WARNING} Failed to report progress: {e}")
    
    def pause(self):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to pause")

        try:
            self.mission_executor.pause()
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to pause mission: {e}, trace: {traceback.format_exc()}")
    
    def resume(self):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to resume")

        try:
            self.mission_executor.resume()
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to resume mission: {e}")
    
    def cancel(self, action: str = "NONE"):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to cancel")

        try:
            self.mission_executor.cancel(action)
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to cancel mission: {e}")
    
    def abort(self):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to abort")

        try:
            self.mission_executor.abort()
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to abort mission: {e}")

    def _reset_mission(self):
        """Safely clear mission state."""
        self.running = False
        self.mission_ready = False
        self.mission_executor.reset()
        logger.info(f"{LogIcons.SUCCESS} Mission state reset successfully.")

    @http_action(
        method="POST",
        path="/mission/plan",
        description="Receives a mission graph and runs it in the background",
        summary="Execute Mission Plan",
        tags=["mission"]
    )
    async def receive_mission(self, data: MissionGraph):
        if self.running or self.mission_ready:
            logger.warning(f"{LogIcons.WARNING} A mission is already loaded.")
            return {"status": f"{LogIcons.WARNING} A mission is already loaded", "error": "Mission in progress"}

        mission_graph = data.model_dump(by_alias=True)

        # ✅ Run in background (non-blocking)
        asyncio.create_task(self.run_mission(mission_graph))

        return {"status": "⏳ Mission is running in background"}

    @http_action(
        method="POST",
        path="/mission/subscribe_to_progress_updates",
        description="Receives an address where mission progress updates will be posted"
    )
    async def subscribe_to_progress_updates(self, data: ProgressUpdateSubscription):
        self.subscriber_address = data.address.rstrip("/")  # remove trailing slash if present
        logger.info(f"{LogIcons.SUCCESS} Subscribed to mission progress updates at: {self.subscriber_address}")
        return {"status": f"{LogIcons.SUCCESS} Subscribed"}
    
    # Not used in the current implementation, but can be used to set a safe return waypoint request address
    @http_action(
        method="POST",
        path="/mission/set_safe_return_plan_request_address",
        description="Sets the address for safe return plan requests"
    )
    async def set_safe_return_plan_request_address(self, data: SafeReturnPlanRequestAddress):
        self.safe_return_plan_request_address = data.address.rstrip("/")  # remove trailing slash if present
        logger.info(f"{LogIcons.SUCCESS} Set safe return plan request address to: {self.safe_return_plan_request_address}")
        return {"status": f"{LogIcons.SUCCESS} Safe return plan request address set"}

    # Not used in the current implementation, but can be used to handle safe return plan requests
    @http_action(
        method="GET",
        path="/mission/safe_return_plan_request",
        description="Receives a safe return plan request and feeds it to the mission planner"
    )
    async def safe_return_plan_request(self):
        if not self.safe_return_plan_request_address:
            logger.warning(f"{LogIcons.WARNING} No safe return plan request address set")
            return {"status": f"{LogIcons.WARNING} No safe return plan request address set", "error": "Address not initialized"}

        pass

    @http_action(
        method="POST",
        path="/mission/pause",
        description="Pauses the currently running mission"
    )
    async def pause_mission(self):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to pause")
            return {"status": f"{LogIcons.WARNING} No mission plan available", "error": "Mission plan not initialized"}

        try:
            self.mission_executor.pause()

            return {"status": f"{LogIcons.PAUSE} Mission pause command received successfully!"}
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to pause mission: {e}")
            return {"status": f"{LogIcons.ERROR} Failed to pause mission", "error": str(e)}

    @http_action(
        method="POST",
        path="/mission/resume",
        description="Resumes a paused mission"
    )
    async def resume_mission(self):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to resume")
            return {"status": f"{LogIcons.WARNING} No mission plan available", "error": "Mission plan not initialized"}

        try:
            self.mission_executor.resume()

            return {"status": f"{LogIcons.RESUME} Mission resume command received successfully!"}
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to resume mission: {e}")
            return {"status": f"{LogIcons.ERROR} Failed to resume mission", "error": str(e)}

    @http_action(
        method="POST",
        path="/mission/cancel",
        description="Cancels the currently running mission"
    )
    async def cancel_mission(self, data: CancelMissionRequest):
        if self.mission_plan is None:
            logger.warning(f"{LogIcons.WARNING} No mission plan available to cancel")
            return {"status": f"{LogIcons.WARNING} No mission plan available", "error": "Mission plan not initialized"}

        try:
            self.mission_executor.cancel(data.action)

            return {"status": f"{LogIcons.CANCEL} Mission cancel command received successfully!"}
        except Exception as e:
            logger.error(f"{LogIcons.ERROR} Failed to cancel mission: {e}")
            return {"status": f"{LogIcons.ERROR} Failed to cancel mission", "error": str(e)}

    async def _mqtt_subscribe_to_mission_plan(self):
        if self.mqtt_proxy is None:
            logger.warning(f"{LogIcons.WARNING} MQTT proxy not available. MQTT functionalities will be disabled.")
            return
        self.mqtt_subscription_id = self.mqtt_proxy.register_handler(self._mqtt_command_handler_master)
        logger.info(f"{LogIcons.SUCCESS} registered MQTT command handler with subscription ID: {self.mqtt_subscription_id}")

    async def _mqtt_command_handler_master(self, topic: str, payload: Dict[str, Any]):
        command = payload.get('command')
        message_id = payload.get('messageId')
        
        if command is None or message_id is None:
            logger.warning(f"{LogIcons.WARNING} Invalid command payload received via MQTT.")
            return
        
        if command == "petal-leafsdk/mission_plan":
            data_recvd: MissionGraph = payload.get("payload")["mission_plan_json"]
            asyncio.create_task(self._mqtt_command_handler_mission_plan(message_id, data_recvd))

    async def _mqtt_command_handler_mission_plan(self, msg_id: str, data: Dict[str, Any]):
        if self.running or self.mission_ready:
            logger.warning(f"{LogIcons.WARNING} A mission is already loaded.")
            await self.mqtt_proxy.publish_message({
                'messageId': msg_id,
                'status': 'error',
                'error': 'A mission is already loaded'
            })
            return

        logger.info(f"{LogIcons.SUCCESS} Received mission plan via MQTT.")
        data_model = MissionGraph.model_validate(data, by_alias=True)
        mission_graph = data_model.model_dump(by_alias=True)
        
        # ✅ Run in background (non-blocking)
        asyncio.create_task(self.run_mission(mission_graph))

        # Send response
        await self.mqtt_proxy.publish_message({
            'messageId': msg_id,
            'status': 'success',
            'result': 'Command executed successfully'
        })
        logger.info(f"{LogIcons.SUCCESS} MQTT command response sent.")