import numpy as np

class Config:
    max_speed = 1.0
    min_speed = -0.5
    max_yawrate = 40.0 * np.pi / 180.0
    max_accel = 0.2
    max_dyawrate = 40.0 * np.pi / 180.0
    velocity_resolution = 0.01
    yawrate_resolution = 0.1 * np.pi / 180.0
    predict_time = 3.0
    dt = 0.1
    to_goal_cost_gain = 0.15
    speed_cost_gain = 1.0
    obstacle_cost_gain = 1.0
    robot_radius = 1.0

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
    Vs = [config.min_speed, config.max_speed, -config.max_yawrate, config.max_yawrate]
    Vd = [x[3] - config.max_accel * config.dt, x[3] + config.max_accel * config.dt,
          x[4] - config.max_dyawrate * config.dt, x[4] + config.max_dyawrate * config.dt]
    window = [max(Vs[0], Vd[0]), min(Vs[1], Vd[1]), max(Vs[2], Vd[2]), min(Vs[3], Vd[3])]
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

def main():
    print("=" * 60)
    print("DWA (Dynamic Window Approach) Demo")
    print("=" * 60)
    
    x = np.array([0.0, 0.0, np.pi / 2.0, 0.0, 0.0])
    goal = np.array([10.0, 10.0])
    ob = np.array([[2.0, 2.0], [4.0, 4.0], [6.0, 6.0], [8.0, 8.0]])
    config = Config()
    trajectory = np.array(x)
    step = 0
    max_steps = 200

    print(f"初始位置: ({x[0]:.2f}, {x[1]:.2f})")
    print(f"目标位置: ({goal[0]:.2f}, {goal[1]:.2f})")
    print(f"障碍物数量: {len(ob)}")
    print("-" * 60)

    while step < max_steps:
        u, best_trajectory = dwa_control(x, config, goal, ob)
        x = motion(x, u, config.dt)
        trajectory = np.vstack((trajectory, x))
        
        dx = goal[0] - x[0]
        dy = goal[1] - x[1]
        dist_to_goal = np.sqrt(dx**2 + dy**2)
        
        step += 1
        
        if step % 20 == 0:
            print(f"步骤 {step:3d} | 位置: ({x[0]:6.2f}, {x[1]:6.2f}) | 速度: {x[3]:.2f} m/s | 到目标: {dist_to_goal:.2f} m")
        
        if dist_to_goal <= config.robot_radius:
            print("\n✓ 到达目标！")
            break

    if step >= max_steps:
        print("\n✗ 达到最大步数，未到达目标")

    print("\n" + "-" * 60)
    print("轨迹统计:")
    print(f"起点: ({trajectory[0, 0]:.2f}, {trajectory[0, 1]:.2f})")
    print(f"终点: ({trajectory[-1, 0]:.2f}, {trajectory[-1, 1]:.2f})")
    path_length = np.sum(np.sqrt(np.diff(trajectory[:, 0])**2 + np.diff(trajectory[:, 1])**2))
    print(f"轨迹长度: {path_length:.2f} m")
    print(f"目标距离: {np.sqrt((goal[0]-trajectory[-1, 0])**2 + (goal[1]-trajectory[-1, 1])**2):.2f} m")
    print(f"总步数: {step}")
    print("=" * 60)

if __name__ == '__main__':
    main()