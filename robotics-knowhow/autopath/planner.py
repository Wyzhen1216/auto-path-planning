import numpy as np

class DWAConfig:
    def __init__(self, params=None):
        if params is None:
            params = {}
        
        self.max_speed = params.get('max_speed', 1.0)
        self.min_speed = params.get('min_speed', -0.5)
        self.max_yawrate = params.get('max_yawrate', 40.0) * np.pi / 180.0
        self.max_accel = params.get('max_accel', 0.2)
        self.max_dyawrate = params.get('max_dyawrate', 40.0) * np.pi / 180.0
        
        self.velocity_resolution = params.get('v_resolution', 0.01)
        self.yawrate_resolution = params.get('yaw_rate_resolution', 0.1) * np.pi / 180.0
        self.predict_time = params.get('predict_time', 3.0)
        self.dt = 0.1
        
        self.to_goal_cost_gain = params.get('to_goal_cost_gain', 0.15)
        self.speed_cost_gain = params.get('speed_cost_gain', 1.0)
        self.obstacle_cost_gain = params.get('obstacle_cost_gain', 1.0)
        self.robot_radius = params.get('robot_radius', 1.0)
        
        self.robot_stuck_flag_cons = params.get('robot_stuck_flag_cons', 0.001)

    def to_dict(self):
        return {
            'max_speed': self.max_speed,
            'min_speed': self.min_speed,
            'max_yawrate': self.max_yawrate * 180.0 / np.pi,
            'max_accel': self.max_accel,
            'max_dyawrate': self.max_dyawrate * 180.0 / np.pi,
            'v_resolution': self.velocity_resolution,
            'yaw_rate_resolution': self.yawrate_resolution * 180.0 / np.pi,
            'predict_time': self.predict_time,
            'to_goal_cost_gain': self.to_goal_cost_gain,
            'speed_cost_gain': self.speed_cost_gain,
            'obstacle_cost_gain': self.obstacle_cost_gain,
            'robot_radius': self.robot_radius,
            'robot_stuck_flag_cons': self.robot_stuck_flag_cons
        }

def motion(x, u, dt):
    x[0] += u[0] * np.cos(x[2]) * dt
    x[1] += u[0] * np.sin(x[2]) * dt
    x[2] += u[1] * dt
    x[3] = u[0]
    x[4] = u[1]
    return x

def predict_trajectory(x_init, u, config):
    x = np.array(x_init)
    trajectory = np.array(x)
    time = 0
    while time <= config.predict_time:
        x = motion(x, u, config.dt)
        trajectory = np.vstack((trajectory, x))
        time += config.dt
    return trajectory

def dynamic_window(x, config):
    Vs = [config.min_speed, config.max_speed, 
          -config.max_yawrate, config.max_yawrate]
    Vd = [x[3] - config.max_accel * config.dt,
          x[3] + config.max_accel * config.dt,
          x[4] - config.max_dyawrate * config.dt,
          x[4] + config.max_dyawrate * config.dt]
    window = [max(Vs[0], Vd[0]), min(Vs[1], Vd[1]),
              max(Vs[2], Vd[2]), min(Vs[3], Vd[3])]
    return window

def calc_to_goal_cost(trajectory, goal, config):
    dx = goal[0] - trajectory[-1, 0]
    dy = goal[1] - trajectory[-1, 1]
    return np.sqrt(dx**2 + dy**2) * config.to_goal_cost_gain

def calc_speed_cost(trajectory, config):
    return (config.max_speed - trajectory[-1, 3]) * config.speed_cost_gain

def calc_obstacle_cost(trajectory, ob, config):
    min_dist = float("inf")
    for i in range(len(trajectory)):
        for j in range(len(ob)):
            dx = trajectory[i, 0] - ob[j, 0]
            dy = trajectory[i, 1] - ob[j, 1]
            dist = np.sqrt(dx**2 + dy**2)
            if dist < min_dist:
                min_dist = dist
    if min_dist <= config.robot_radius:
        return float("inf")
    return 1.0 / min_dist * config.obstacle_cost_gain

def dwa_control(x, config, goal, ob):
    window = dynamic_window(x, config)
    min_cost = float("inf")
    best_u = [0.0, 0.0]
    best_trajectory = np.array(x)

    v = window[0]
    while v <= window[1]:
        y = window[2]
        while y <= window[3]:
            trajectory = predict_trajectory(x, [v, y], config)
            to_goal_cost = calc_to_goal_cost(trajectory, goal, config)
            speed_cost = calc_speed_cost(trajectory, config)
            ob_cost = calc_obstacle_cost(trajectory, ob, config)
            final_cost = to_goal_cost + speed_cost + ob_cost
            if min_cost >= final_cost:
                min_cost = final_cost
                best_u = [v, y]
                best_trajectory = trajectory
            y += config.yawrate_resolution
        v += config.velocity_resolution
    return best_u, best_trajectory

def plan_path(start, goal, obstacles, config, max_steps=200):
    x = np.array([start[0], start[1], start[2], 0.0, 0.0])
    trajectory = np.array(x)
    step = 0
    
    while step < max_steps:
        u, best_trajectory = dwa_control(x, config, goal, obstacles)
        x = motion(x, u, config.dt)
        trajectory = np.vstack((trajectory, x))
        
        dx = goal[0] - x[0]
        dy = goal[1] - x[1]
        dist_to_goal = np.sqrt(dx**2 + dy**2)
        
        step += 1
        
        if dist_to_goal <= config.robot_radius:
            break
    
    return trajectory, step, dist_to_goal