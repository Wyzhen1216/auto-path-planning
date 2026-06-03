import numpy as np
import time
from .planner import plan_path, DWAConfig

class Evaluator:
    def __init__(self, scenarios):
        self.scenarios = scenarios
    
    def evaluate(self, params):
        config = DWAConfig(params)
        
        results = []
        for scenario in self.scenarios:
            start = scenario['start']
            goal = scenario['goal']
            obstacles = scenario['obstacles']
            
            start_time = time.time()
            trajectory, steps, dist_to_goal = plan_path(start, goal, obstacles, config)
            plan_time = time.time() - start_time
            
            path_length = np.sum(np.sqrt(np.diff(trajectory[:, 0])**2 + np.diff(trajectory[:, 1])**2))
            
            success = dist_to_goal <= config.robot_radius
            
            results.append({
                'success': success,
                'path_length': path_length,
                'steps': steps,
                'plan_time_ms': plan_time * 1000,
                'dist_to_goal': dist_to_goal
            })
        
        success_rate = np.mean([r['success'] for r in results])
        avg_path_length = np.mean([r['path_length'] for r in results])
        avg_plan_time_ms = np.mean([r['plan_time_ms'] for r in results])
        
        return {
            'success_rate': success_rate,
            'avg_path_length': avg_path_length,
            'avg_plan_time_ms': avg_plan_time_ms,
            'details': results
        }
    
    def quick_evaluate(self, params):
        config = DWAConfig(params)
        
        results = []
        for scenario in self.scenarios[:2]:
            start = scenario['start']
            goal = scenario['goal']
            obstacles = scenario['obstacles']
            
            trajectory, steps, dist_to_goal = plan_path(start, goal, obstacles, config)
            
            success = dist_to_goal <= config.robot_radius
            path_length = np.sum(np.sqrt(np.diff(trajectory[:, 0])**2 + np.diff(trajectory[:, 1])**2))
            
            results.append({
                'success': success,
                'path_length': path_length
            })
        
        success_rate = np.mean([r['success'] for r in results])
        avg_path_length = np.mean([r['path_length'] for r in results])
        
        return {
            'success_rate': success_rate,
            'avg_path_length': avg_path_length
        }