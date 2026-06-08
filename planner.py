"""
Dijkstra grid planner — Agent 可修改的唯一代码文件（Phase 2）。

逻辑源自 PythonRobotics PathPlanning/Dijkstra/dijkstra.py
"""

from __future__ import annotations

import math


class Config:
    """栅格 Dijkstra 参数 — Agent 主要改这里。"""

    def __init__(self) -> None:
        self.resolution = 0.4
        self.robot_radius = 0.3
        self.motion_model = "8-dir"  # "8-dir" | "4-dir"


config = Config()


class DijkstraPlanner:
    """无 GUI 版 PythonRobotics DijkstraPlanner。"""

    class Node:
        def __init__(self, x: int, y: int, cost: float, parent_index: int) -> None:
            self.x = x
            self.y = y
            self.cost = cost
            self.parent_index = parent_index

    def __init__(
        self,
        ox: list[float],
        oy: list[float],
        resolution: float,
        robot_radius: float,
        motion_model: str = "8-dir",
    ) -> None:
        self.resolution = resolution
        self.robot_radius = robot_radius
        self.motion = self._motion_model(motion_model)
        self.min_x = round(min(ox))
        self.min_y = round(min(oy))
        self.max_x = round(max(ox))
        self.max_y = round(max(oy))
        self.x_width = round((self.max_x - self.min_x) / self.resolution)
        self.y_width = round((self.max_y - self.min_y) / self.resolution)
        self.obstacle_map = self._build_obstacle_map(ox, oy)

    @staticmethod
    def _motion_model(name: str) -> list[list[float]]:
        four = [[1, 0, 1], [0, 1, 1], [-1, 0, 1], [0, -1, 1]]
        if name == "4-dir":
            return four
        return four + [
            [-1, -1, math.sqrt(2)],
            [-1, 1, math.sqrt(2)],
            [1, -1, math.sqrt(2)],
            [1, 1, math.sqrt(2)],
        ]

    def _build_obstacle_map(self, ox: list[float], oy: list[float]) -> list[list[bool]]:
        obstacle_map = [[False for _ in range(self.y_width)] for _ in range(self.x_width)]
        for ix in range(self.x_width):
            x = self.calc_position(ix, self.min_x)
            for iy in range(self.y_width):
                y = self.calc_position(iy, self.min_y)
                for iox, ioy in zip(ox, oy, strict=True):
                    if math.hypot(iox - x, ioy - y) <= self.robot_radius:
                        obstacle_map[ix][iy] = True
                        break
        return obstacle_map

    def planning(self, sx: float, sy: float, gx: float, gy: float) -> tuple[list[float], list[float]]:
        start_node = self.Node(
            self.calc_xy_index(sx, self.min_x),
            self.calc_xy_index(sy, self.min_y),
            0.0,
            -1,
        )
        goal_node = self.Node(
            self.calc_xy_index(gx, self.min_x),
            self.calc_xy_index(gy, self.min_y),
            0.0,
            -1,
        )

        open_set: dict[int, DijkstraPlanner.Node] = {self.calc_index(start_node): start_node}
        closed_set: dict[int, DijkstraPlanner.Node] = {}

        while open_set:
            c_id = min(open_set, key=lambda o: open_set[o].cost)
            current = open_set[c_id]

            if current.x == goal_node.x and current.y == goal_node.y:
                closed_set[c_id] = current
                goal_node.parent_index = c_id
                goal_node.cost = current.cost
                break

            del open_set[c_id]
            closed_set[c_id] = current

            for move_x, move_y, move_cost in self.motion:
                node = self.Node(
                    current.x + int(move_x),
                    current.y + int(move_y),
                    current.cost + move_cost,
                    c_id,
                )
                n_id = self.calc_index(node)

                if n_id in closed_set or not self.verify_node(node):
                    continue

                if n_id not in open_set or open_set[n_id].cost >= node.cost:
                    open_set[n_id] = node
        else:
            return [], []

        return self.calc_final_path(goal_node, closed_set)

    def calc_final_path(
        self, goal_node: Node, closed_set: dict[int, Node]
    ) -> tuple[list[float], list[float]]:
        rx = [self.calc_position(goal_node.x, self.min_x)]
        ry = [self.calc_position(goal_node.y, self.min_y)]
        parent_index = goal_node.parent_index
        while parent_index != -1:
            n = closed_set[parent_index]
            rx.append(self.calc_position(n.x, self.min_x))
            ry.append(self.calc_position(n.y, self.min_y))
            parent_index = n.parent_index
        return rx, ry

    def calc_position(self, index: int, minp: float) -> float:
        return index * self.resolution + minp

    def calc_xy_index(self, position: float, minp: float) -> int:
        return round((position - minp) / self.resolution)

    def calc_index(self, node: Node) -> int:
        return (node.y - self.min_y) * self.x_width + (node.x - self.min_x)

    def verify_node(self, node: Node) -> bool:
        px = self.calc_position(node.x, self.min_x)
        py = self.calc_position(node.y, self.min_y)
        if px < self.min_x or py < self.min_y or px >= self.max_x or py >= self.max_y:
            return False
        return not self.obstacle_map[node.x][node.y]


def plan_path(
    sx: float, sy: float, gx: float, gy: float, ox: list[float], oy: list[float]
) -> tuple[list[float], list[float]]:
    """单次全局规划 — prepare.py 对此函数计时。"""
    planner = DijkstraPlanner(
        ox,
        oy,
        config.resolution,
        config.robot_radius,
        config.motion_model,
    )
    return planner.planning(sx, sy, gx, gy)
