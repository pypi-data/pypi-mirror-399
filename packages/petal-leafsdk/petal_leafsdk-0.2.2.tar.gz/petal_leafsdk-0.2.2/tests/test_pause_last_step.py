import unittest
from unittest.mock import MagicMock
from petal_leafsdk.mission_plan_executor import MissionControlCommand, MissionPlanExecutor, MissionState
from leafsdk.core.mission.mission_plan import MissionPlan
from leafsdk.core.mission.mission_step import Land, GotoLocalPosition
import networkx as nx

class TestMissionPauseLastStep(unittest.TestCase):
    def test_pause_last_step(self):
        # Setup
        plan = MagicMock(spec=MissionPlan)
        plan.id = "test_mission"
        plan.config = MagicMock()
        plan.config.joystick_mode.value = "enabled"
        
        # Create a simple graph with one Land step (non-pausable)
        graph = nx.MultiDiGraph()
        step = Land()
        graph.add_node("step1", step=step)
        plan.mission_graph = graph
        # plan.mission_graph.copy.return_value = graph.copy() 
        plan._head_node = "step1"
        plan._get_steps.return_value = [("step1", step)]
        
        mav_proxy = MagicMock()
        mav_proxy.target_system = 1
        redis_proxy = MagicMock()
        
        executor = MissionPlanExecutor(plan, mav_proxy, redis_proxy)
        executor.prepare()
        
        # Start execution
        executor.run_step() # First exec
        
        # Request pause
        # Land is non-pausable, so it should queue the pause
        executor.pause()
        
        # Simulate step completion
        # Land step needs to be told it's landed or we force it
        executor._current_step._landed = True # Hack to force completion
        
        # Run step again to process completion
        executor.run_step()
        
        # Expectation: It should be COMPLETED because it's the last step
        print(f"Final state: {executor._mission_status.state}")
        
        if executor._mission_status.state == MissionState.PAUSED:
            print("Failure: Mission stuck in PAUSED state after last step.")
        elif executor._mission_status.state == MissionState.COMPLETED:
            print("Success: Mission completed successfully.")
        else:
            print(f"Unexpected state: {executor._mission_status.state}")

        self.assertEqual(executor._mission_status.state, MissionState.COMPLETED)

    def test_pause_for_pausable_steps(self):
        # Setup
        plan = MagicMock(spec=MissionPlan)
        plan.id = "test_mission"
        plan.config = MagicMock()
        plan.config.joystick_mode.value = "enabled"
        
        # Create a simple graph with one pausable step (GotoLocalPosition)
        graph = nx.MultiDiGraph()
        step = GotoLocalPosition(waypoints=[(0, 0, 0)])
        step.average_deceleration = 0.5  # Add the required attribute
        graph.add_node("step1", step=step)
        plan.mission_graph = graph
        plan._head_node = "step1"
        plan._get_steps.return_value = [("step1", step)]
        
        mav_proxy = MagicMock()
        mav_proxy.target_system = 1
        redis_proxy = MagicMock()
        
        executor = MissionPlanExecutor(plan, mav_proxy, redis_proxy)
        executor.prepare()

        executor._mission_control_cmd = MissionControlCommand.PAUSE_NOW
        executor._mission_status.state = MissionState.RUNNING
        executor.run_step()

        self.assertEqual(executor._mission_status.state, MissionState.PAUSED)


if __name__ == '__main__':
    unittest.main()
