import numpy as np
import random
import json
import os
from .evaluator import Evaluator

class SearchPolicy:
    PARAM_BOUNDS = {
        'to_goal_cost_gain': (0.01, 1.0),
        'speed_cost_gain': (0.1, 5.0),
        'obstacle_cost_gain': (0.1, 5.0),
        'predict_time': (1.0, 5.0),
        'v_resolution': (0.005, 0.05),
        'yaw_rate_resolution': (0.05, 1.0),
        'max_speed': (0.5, 2.0),
        'max_yawrate': (20.0, 60.0),
        'robot_radius': (0.5, 1.5),
        'robot_stuck_flag_cons': (0.0001, 0.01)
    }
    
    def __init__(self, scenarios):
        self.evaluator = Evaluator(scenarios)
        self.best_params = None
        self.best_score = None
        self.history = []
    
    def random_params(self):
        params = {}
        for key, (low, high) in self.PARAM_BOUNDS.items():
            params[key] = random.uniform(low, high)
        return params
    
    def mutate_params(self, params, mutation_rate=0.1, mutation_scale=0.2):
        new_params = params.copy()
        for key in params:
            if random.random() < mutation_rate:
                low, high = self.PARAM_BOUNDS[key]
                current = params[key]
                mutation = random.gauss(0, mutation_scale * (high - low))
                new_params[key] = max(low, min(high, current + mutation))
        return new_params
    
    def crossover_params(self, parent1, parent2):
        child = {}
        for key in parent1:
            if random.random() < 0.5:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child
    
    def fitness(self, result):
        sr = result['success_rate']
        pl = result['avg_path_length']
        pt = result['avg_plan_time_ms']
        
        if sr == 0:
            return -float('inf')
        
        return sr * 100 - pl * 0.1 - pt * 0.01
    
    def genetic_search(self, generations=50, pop_size=20):
        population = [self.random_params() for _ in range(pop_size)]
        
        for gen in range(generations):
            scores = []
            for params in population:
                result = self.evaluator.quick_evaluate(params)
                score = self.fitness(result)
                scores.append((score, params, result))
            
            scores.sort(reverse=True, key=lambda x: x[0])
            
            if self.best_score is None or scores[0][0] > self.best_score:
                self.best_score = scores[0][0]
                self.best_params = scores[0][1]
                self.history.append({
                    'generation': gen,
                    'score': scores[0][0],
                    'params': scores[0][1],
                    'result': scores[0][2]
                })
                print(f"Gen {gen}: Best score={scores[0][0]:.2f}, SR={scores[0][2]['success_rate']:.2f}, PL={scores[0][2]['avg_path_length']:.2f}")
            
            new_population = scores[:4]
            while len(new_population) < pop_size:
                parent1 = random.choice(scores[:10])[1]
                parent2 = random.choice(scores[:10])[1]
                child = self.crossover_params(parent1, parent2)
                child = self.mutate_params(child)
                new_population.append((0, child, None))
            
            population = [p[1] for p in new_population]
        
        return self.best_params, self.best_score
    
    def hill_climb(self, iterations=100, step_size=0.1):
        current_params = self.random_params()
        current_result = self.evaluator.quick_evaluate(current_params)
        current_score = self.fitness(current_result)
        
        self.best_params = current_params
        self.best_score = current_score
        
        for i in range(iterations):
            new_params = self.mutate_params(current_params, mutation_rate=0.5, mutation_scale=step_size)
            new_result = self.evaluator.quick_evaluate(new_params)
            new_score = self.fitness(new_result)
            
            if new_score > current_score:
                current_params = new_params
                current_score = new_score
                
                if current_score > self.best_score:
                    self.best_params = current_params
                    self.best_score = current_score
                    self.history.append({
                        'iteration': i,
                        'score': current_score,
                        'params': current_params,
                        'result': new_result
                    })
                    print(f"Iter {i}: Score={current_score:.2f}, SR={new_result['success_rate']:.2f}, PL={new_result['avg_path_length']:.2f}")
        
        return self.best_params, self.best_score
    
    def save_results(self, filename='results.tsv'):
        with open(filename, 'w') as f:
            f.write("generation\tscore\tsuccess_rate\tavg_path_length\tparams\n")
            for entry in self.history:
                params_str = json.dumps(entry['params'])
                f.write(f"{entry.get('generation', entry.get('iteration', 0))}\t{entry['score']:.4f}\t{entry['result']['success_rate']:.4f}\t{entry['result']['avg_path_length']:.4f}\t{params_str}\n")
    
    def load_best_params(self, filename='best_params.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.best_params = json.load(f)
            return True
        return False
    
    def save_best_params(self, filename='best_params.json'):
        if self.best_params is not None:
            with open(filename, 'w') as f:
                json.dump(self.best_params, f, indent=2)
            return True
        return False