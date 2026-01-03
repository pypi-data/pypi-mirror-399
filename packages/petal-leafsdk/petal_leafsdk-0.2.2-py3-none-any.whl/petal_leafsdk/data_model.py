# petal_leafsdk/data_model.py

from pydantic import BaseModel, Field
from typing import Any, List, Optional, Literal, Union, Tuple, Sequence, Dict
from enum import Enum

Tuple3D = Tuple[float, float, float]   # exact length 3

# Mission schema
class TakeoffParams(BaseModel):
    alt: float

class GotoLocalPositionParams(BaseModel):
    waypoints: Union[Tuple3D, Sequence[Tuple3D]]
    yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0
    speed: Optional[Union[float, Sequence[float]]] = 0.2
    yaw_speed: Optional[Union[float, Sequence[float], Literal["sync"]]] = "sync"
    is_pausable: bool = True
    average_deceleration: float = 0.5   # m2/s

class GotoGPSWaypointParams(BaseModel):
    waypoints: Union[Tuple3D, Sequence[Tuple3D]]
    yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0
    speed: Optional[Union[float, Sequence[float]]] = 0.2
    yaw_speed: Optional[Union[float, Sequence[float], Literal["sync"]]] = "sync"
    is_pausable: bool = True
    average_deceleration: float = 0.5   # m2/s

class GotoRelativeParams(BaseModel):
    waypoints: Union[Tuple3D, Sequence[Tuple3D]]
    yaws_deg: Optional[Union[float, Sequence[float]]] = 0.0
    speed: Optional[Union[float, Sequence[float]]] = 0.2
    yaw_speed: Optional[Union[float, Sequence[float], Literal["sync"]]] = "sync"
    is_pausable: bool = True
    average_deceleration: float = 0.5   # m2/s

class YawAbsoluteParams(BaseModel):
    yaws_deg: Union[float, Sequence[float]]
    yaw_speed: Optional[Union[float, Sequence[float]]] = 30.0
    is_pausable: bool = True
    average_deceleration: float = 0.5   # m2/s

class YawRelativeParams(BaseModel):
    yaws_deg: Union[float, Sequence[float]]
    yaw_speed: Optional[Union[float, Sequence[float]]] = 30.0
    is_pausable: bool = True
    average_deceleration: float = 0.5   # m2/s

class WaitParams(BaseModel):
    duration: float

class TakeoffNode(BaseModel):
    name: str
    type: Literal["Takeoff"]
    params: TakeoffParams

class GotoLocalPositionNode(BaseModel):
    name: str
    type: Literal["GotoLocalPosition"]
    params: GotoLocalPositionParams

class GotoGPSWaypointNode(BaseModel):
    name: str
    type: Literal["GotoGPSWaypoint"]
    params: GotoGPSWaypointParams

class GotoRelativeNode(BaseModel):
    name: str
    type: Literal["GotoRelative"]
    params: GotoRelativeParams

class YawAbsoluteNode(BaseModel):
    name: str
    type: Literal["YawAbsolute"]
    params: YawAbsoluteParams

class YawRelativeNode(BaseModel):
    name: str
    type: Literal["YawRelative"]
    params: YawRelativeParams

class WaitNode(BaseModel):
    name: str
    type: Literal["Wait"]
    params: WaitParams

class LandNode(BaseModel):
    name: str
    type: Literal["Land"]
    params: Optional[dict] = None

class Edge(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    condition: Optional[str] = None

    model_config = {"populate_by_name": True}

Node = Union[TakeoffNode, GotoLocalPositionNode, GotoGPSWaypointNode, GotoRelativeNode, YawAbsoluteNode, YawRelativeNode, WaitNode, LandNode]


class MissionStepProgress(BaseModel):
    completed_mission_step_id: str
    completed_mission_step_description: Optional[str] = ""
    next_mission_step_id: str
    next_mission_step_description: Optional[str] = ""

class ProgressUpdateSubscription(BaseModel):
    address: str  # e.g., http://localhost:5000/WHMS/v1/update_step_progress

class SafeReturnPlanRequestAddress(BaseModel):
    address: str  # e.g., http://localhost:5000/WHMS/v1/safe_return_plan_request


class JoystickMode(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ENABLED_ON_PAUSE = "enabled_on_pause"


class MissionConfig:
    joystick_mode: JoystickMode = JoystickMode.ENABLED


class MissionGraph(BaseModel):
    id: str = Field(..., description="Unique identifier for the mission", example="main")
    joystick_mode: JoystickMode = JoystickMode.ENABLED
    nodes: List[Node] = Field(..., description="List of mission steps/nodes")
    edges: List[Edge] = Field(..., description="Connections between mission steps/nodes")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "main",
                "nodes": [
                    {
                    "name": "Takeoff",
                    "type": "Takeoff",
                    "params": {
                        "alt": 1
                    }
                    },
                    {
                    "name": "Wait 1",
                    "type": "Wait",
                    "params": {
                        "duration": 2
                    }
                    },
                    {
                    "name": "GotoLocalWaypoint 1",
                    "type": "GotoLocalPosition",
                    "params": {
                        "waypoints": [
                        [
                            0.5,
                            0.0,
                            1.0
                        ]
                        ],
                        "yaws_deg": [
                        0.0
                        ],
                        "speed": [
                        0.2
                        ],
                        "yaw_speed": [
                        30.0
                        ]
                    }
                    },
                    {
                    "name": "GotoLocalWaypoint 2",
                    "type": "GotoLocalPosition",
                    "params": {
                        "waypoints": [
                        [
                            0.5,
                            0.5,
                            1.0
                        ],
                        [
                            0.0,
                            0.0,
                            1.0
                        ]
                        ],
                        "yaws_deg": [
                        0.0,
                        0.0
                        ],
                        "speed": [
                        0.2,
                        0.2
                        ],
                        "yaw_speed": [
                        30.0,
                        30.0
                        ]
                    }
                    },
                    {
                    "name": "GotoLocalWaypoint 3",
                    "type": "GotoLocalPosition",
                    "params": {
                        "waypoints": [
                        [
                            0.0,
                            0.5,
                            1.0
                        ],
                        [
                            0.5,
                            0.5,
                            1.0
                        ],
                        [
                            0.5,
                            0.0,
                            1.0
                        ]
                        ],
                        "yaws_deg": [
                        0.0,
                        10.0,
                        20.0
                        ],
                        "speed": [
                        0.2,
                        0.3,
                        0.4
                        ],
                        "yaw_speed": [
                        10.0,
                        20.0,
                        20.0
                        ]
                    }
                    },
                    {
                    "name": "Wait 2",
                    "type": "Wait",
                    "params": {
                        "duration": 2
                    }
                    },
                    {
                    "name": "Land",
                    "type": "Land",
                    "params": {}
                    }
                ],
                "edges": [
                    {
                    "from": "Takeoff",
                    "to": "Wait 1",
                    "condition": None
                    },
                    {
                    "from": "Wait 1",
                    "to": "GotoLocalWaypoint 1",
                    "condition": None
                    },
                    {
                    "from": "GotoLocalWaypoint 1",
                    "to": "GotoLocalWaypoint 2",
                    "condition": None
                    },
                    {
                    "from": "GotoLocalWaypoint 2",
                    "to": "GotoLocalWaypoint 3",
                    "condition": None
                    },
                    {
                    "from": "GotoLocalWaypoint 3",
                    "to": "Wait 2",
                    "condition": None
                    },
                    {
                    "from": "Wait 2",
                    "to": "Land",
                    "condition": None
                    }
                ]
            }
        }
    }

class CancelMissionRequest(BaseModel):
    action: Optional[Literal["NONE", "HOVER", "RETURN_TO_HOME", "LAND_IMMEDIATELY"]] = "HOVER"