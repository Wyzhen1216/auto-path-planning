import numpy as np

def get_default_scenarios():
    scenarios = []
    
    scenarios.append({
        'name': 'simple_straight',
        'start': [0.0, 0.0, np.pi / 2.0],
        'goal': [10.0, 10.0],
        'obstacles': np.array([[3.0, 3.0], [5.0, 5.0], [7.0, 7.0]])
    })
    
    scenarios.append({
        'name': 'obstacle_field',
        'start': [0.0, 0.0, np.pi / 2.0],
        'goal': [10.0, 10.0],
        'obstacles': np.array([[2.0, 2.0], [2.0, 5.0], [2.0, 8.0],
                               [5.0, 2.0], [5.0, 8.0],
                               [8.0, 2.0], [8.0, 5.0], [8.0, 8.0]])
    })
    
    scenarios.append({
        'name': 'narrow_passage',
        'start': [0.0, 0.0, 0.0],
        'goal': [10.0, 5.0],
        'obstacles': np.array([[4.0, 2.0], [4.0, 8.0],
                               [6.0, 2.0], [6.0, 8.0]])
    })
    
    scenarios.append({
        'name': 'corner',
        'start': [0.0, 0.0, 0.0],
        'goal': [10.0, 10.0],
        'obstacles': np.array([[5.0, 0.0], [5.0, 5.0],
                               [10.0, 5.0]])
    })
    
    return scenarios