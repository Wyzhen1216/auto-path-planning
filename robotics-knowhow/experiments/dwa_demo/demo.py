import sys
sys.path.append('d:/robotics-knowhow/PythonRobotics/PathPlanning/DynamicWindowApproach')

import numpy as np
from dynamic_window_approach import Config, motion, dwa_control

def main():
    print("DWA Demo 开始运行...")
    
    # 初始化机器人状态 [x, y, yaw, v, omega]
    x = np.array([0.0, 0.0, np.pi / 2.0, 0.0, 0.0])
    # 目标位置
    goal = np.array([10.0, 10.0])
    # 障碍物位置
    ob = np.array([[2.0, 2.0], [4.0, 4.0], [6.0, 6.0], [8.0, 8.0]])
    # 配置参数
    config = Config()
    
    # 存储轨迹
    trajectory = np.array(x)
    step = 0
    max_steps = 200
    
    while step < max_steps:
        # 使用 DWA 算法计算控制量
        u, best_trajectory = dwa_control(x, config, goal, ob)
        # 更新机器人状态
        x = motion(x, u, config.dt)
        trajectory = np.vstack((trajectory, x))
        
        # 计算到目标的距离
        dx = goal[0] - x[0]
        dy = goal[1] - x[1]
        dist_to_goal = np.sqrt(dx**2 + dy**2)
        
        step += 1
        
        if step % 20 == 0:
            print(f"步骤 {step}: 位置 ({x[0]:.2f}, {x[1]:.2f}), 速度 {x[3]:.2f} m/s, 到目标距离 {dist_to_goal:.2f} m")
        
        # 检查是否到达目标
        if dist_to_goal <= config.robot_radius:
            print(f"\n到达目标！总步数: {step}")
            break
    
    if step >= max_steps:
        print(f"\n达到最大步数 {max_steps}，未到达目标")
    
    # 输出轨迹统计
    print(f"\n轨迹统计:")
    print(f"起点: ({trajectory[0, 0]:.2f}, {trajectory[0, 1]:.2f})")
    print(f"终点: ({trajectory[-1, 0]:.2f}, {trajectory[-1, 1]:.2f})")
    print(f"轨迹长度: {np.sum(np.sqrt(np.diff(trajectory[:, 0])**2 + np.diff(trajectory[:, 1])**2)):.2f} m")
    print(f"目标距离: {np.sqrt((goal[0]-trajectory[-1, 0])**2 + (goal[1]-trajectory[-1, 1])**2):.2f} m")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)