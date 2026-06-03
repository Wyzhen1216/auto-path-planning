"""
DWA local planner — Agent 可修改的唯一代码文件（对标 autoresearch 的 train.py）。

逻辑源自 PythonRobotics PathPlanning/DynamicWindowApproach/dynamic_window_approach.py
"""

from __future__ import annotations

import math
from enum import Enum

import numpy as np


class RobotType(Enum):
    circle = 0
    rectangle = 1


class Config:
    """仿真与代价参数 — Agent 主要改这里或 dwa_control 内的代价组合。"""

    def __init__(self) -> None:
        self.max_speed = 1.0
        self.min_speed = -0.5
        self.max_yaw_rate = 40.0 * math.pi / 180.0
        self.max_accel = 0.2
        self.max_delta_yaw_rate = 40.0 * math.pi / 180.0
        self.v_resolution = 0.01
        self.yaw_rate_resolution = 0.1 * math.pi / 180.0
        self.dt = 0.1
        self.predict_time = 3.0
        self.to_goal_cost_gain = 0.25
        self.speed_cost_gain = 2.0
        self.obstacle_cost_gain = 1.0
        self.robot_stuck_flag_cons = 0.001
        self._robot_type = RobotType.circle
        self.robot_radius = 1.0
        self.robot_width = 0.5
        self.robot_length = 1.2
        self.ob = np.array(
            [
                [-1, -1],
                [0, 2],
                [4.0, 2.0],
                [5.0, 4.0],
                [5.0, 5.0],
                [5.0, 6.0],
                [5.0, 9.0],
                [8.0, 9.0],
                [7.0, 9.0],
                [8.0, 10.0],
                [9.0, 11.0],
                [12.0, 13.0],
                [12.0, 12.0],
                [15.0, 15.0],
                [13.0, 13.0],
            ],
            dtype=float,
        )

    @property
    def robot_type(self) -> RobotType:
        return self._robot_type

    @robot_type.setter
    def robot_type(self, value: RobotType) -> None:
        if not isinstance(value, RobotType):
            raise TypeError("robot_type must be an instance of RobotType")
        self._robot_type = value


config = Config()


def motion(x: np.ndarray, u: list[float], dt: float) -> np.ndarray:
    x = x.copy()
    x[2] += u[1] * dt
    x[0] += u[0] * math.cos(x[2]) * dt
    x[1] += u[0] * math.sin(x[2]) * dt
    x[3] = u[0]
    x[4] = u[1]
    return x


def calc_dynamic_window(x: np.ndarray, cfg: Config) -> list[float]:
    vs = [cfg.min_speed, cfg.max_speed, -cfg.max_yaw_rate, cfg.max_yaw_rate]
    vd = [
        x[3] - cfg.max_accel * cfg.dt,
        x[3] + cfg.max_accel * cfg.dt,
        x[4] - cfg.max_delta_yaw_rate * cfg.dt,
        x[4] + cfg.max_delta_yaw_rate * cfg.dt,
    ]
    return [
        max(vs[0], vd[0]),
        min(vs[1], vd[1]),
        max(vs[2], vd[2]),
        min(vs[3], vd[3]),
    ]


def predict_trajectory(x_init: np.ndarray, v: float, y: float, cfg: Config) -> np.ndarray:
    x = np.array(x_init, dtype=float)
    trajectory = np.array(x)
    time = 0.0
    while time <= cfg.predict_time:
        x = motion(x, [v, y], cfg.dt)
        trajectory = np.vstack((trajectory, x))
        time += cfg.dt
    return trajectory


def calc_to_goal_cost(trajectory: np.ndarray, goal: np.ndarray) -> float:
    dx = goal[0] - trajectory[-1, 0]
    dy = goal[1] - trajectory[-1, 1]
    error_angle = math.atan2(dy, dx)
    cost_angle = error_angle - trajectory[-1, 2]
    return abs(math.atan2(math.sin(cost_angle), math.cos(cost_angle)))


def calc_obstacle_cost(trajectory: np.ndarray, ob: np.ndarray, cfg: Config) -> float:
    ox = ob[:, 0]
    oy = ob[:, 1]
    dx = trajectory[:, 0] - ox[:, None]
    dy = trajectory[:, 1] - oy[:, None]
    r = np.hypot(dx, dy)

    if cfg.robot_type == RobotType.rectangle:
        yaw = trajectory[:, 2]
        rot = np.array([[np.cos(yaw), -np.sin(yaw)], [np.sin(yaw), np.cos(yaw)]])
        rot = np.transpose(rot, [2, 0, 1])
        local_ob = ob[:, None] - trajectory[:, 0:2]
        local_ob = local_ob.reshape(-1, local_ob.shape[-1])
        local_ob = np.array([local_ob @ x for x in rot])
        local_ob = local_ob.reshape(-1, local_ob.shape[-1])
        upper_check = local_ob[:, 0] <= cfg.robot_length / 2
        right_check = local_ob[:, 1] <= cfg.robot_width / 2
        bottom_check = local_ob[:, 0] >= -cfg.robot_length / 2
        left_check = local_ob[:, 1] >= -cfg.robot_width / 2
        if (
            np.logical_and(
                np.logical_and(upper_check, right_check),
                np.logical_and(bottom_check, left_check),
            )
        ).any():
            return float("inf")
    elif cfg.robot_type == RobotType.circle:
        if np.array(r <= cfg.robot_radius).any():
            return float("inf")

    min_r = np.min(r)
    return 1.0 / min_r


def calc_control_and_trajectory(
    x: np.ndarray, dw: list[float], cfg: Config, goal: np.ndarray, ob: np.ndarray
) -> tuple[list[float], np.ndarray]:
    x_init = x[:]
    min_cost = float("inf")
    best_u = [0.0, 0.0]
    best_trajectory = np.array([x])

    for v in np.arange(dw[0], dw[1], cfg.v_resolution):
        for y in np.arange(dw[2], dw[3], cfg.yaw_rate_resolution):
            trajectory = predict_trajectory(x_init, v, y, cfg)
            to_goal_cost = cfg.to_goal_cost_gain * calc_to_goal_cost(trajectory, goal)
            speed_cost = cfg.speed_cost_gain * (cfg.max_speed - trajectory[-1, 3])
            ob_cost = cfg.obstacle_cost_gain * calc_obstacle_cost(trajectory, ob, cfg)
            final_cost = to_goal_cost + speed_cost + ob_cost

            if min_cost >= final_cost:
                min_cost = final_cost
                best_u = [v, y]
                best_trajectory = trajectory
                if (
                    abs(best_u[0]) < cfg.robot_stuck_flag_cons
                    and abs(x[3]) < cfg.robot_stuck_flag_cons
                ):
                    best_u[1] = -cfg.max_delta_yaw_rate

    return best_u, best_trajectory


def dwa_control(
    x: np.ndarray, cfg: Config, goal: np.ndarray, ob: np.ndarray
) -> tuple[list[float], np.ndarray]:
    """单步 DWA 规划 — prepare.py 对此函数计时。"""
    dw = calc_dynamic_window(x, cfg)
    return calc_control_and_trajectory(x, dw, cfg, goal, ob)


def state_collides(x: np.ndarray, ob: np.ndarray, cfg: Config) -> bool:
    """圆盘机器人：任障碍点距离 <= robot_radius 视为碰撞。"""
    if cfg.robot_type != RobotType.circle:
        raise NotImplementedError("prepare.py Phase 1 仅评测 circle")
    d = np.hypot(ob[:, 0] - x[0], ob[:, 1] - x[1])
    return bool(np.any(d <= cfg.robot_radius))
