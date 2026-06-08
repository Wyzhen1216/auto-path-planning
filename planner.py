"""
RRT* planner — Phase 2（Agent 实验时复制为 planner.py）。

逻辑源自 PythonRobotics PathPlanning/RRTStar/rrt_star.py
"""

from __future__ import annotations

import math
import random


class Config:
    """RRT* 参数 — Agent 主要改这里。"""

    def __init__(self) -> None:
        self.expand_dis = 3.2
        self.path_resolution = 0.5
        self.goal_sample_rate = 30
        self.max_iter = 600
        self.connect_circle_dist = 24.0
        self.robot_radius = 0.8


config = Config()


class Node:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.parent: Node | None = None
        self.cost = 0.0


class RRTStar:
    def __init__(
        self,
        obstacle_circles: list[list[float]],
        bounds: tuple[float, float, float, float],
        expand_dis: float,
        path_resolution: float,
        goal_sample_rate: int,
        max_iter: int,
        connect_circle_dist: float,
        robot_radius: float,
    ) -> None:
        self.obstacle_circles = obstacle_circles
        self.min_x, self.max_x, self.min_y, self.max_y = bounds
        self.expand_dis = expand_dis
        self.path_resolution = path_resolution
        self.goal_sample_rate = goal_sample_rate
        self.max_iter = max_iter
        self.connect_circle_dist = connect_circle_dist
        self.robot_radius = robot_radius
        self.node_list: list[Node] = []

    def planning(self, sx: float, sy: float, gx: float, gy: float) -> tuple[list[float], list[float]]:
        start = Node(sx, sy)
        goal = Node(gx, gy)
        self.node_list = [start]

        for _ in range(self.max_iter):
            rnd = self._sample(goal)
            nearest = self._nearest_node(rnd)
            new_node = self._steer(nearest, rnd)
            if not self._is_free_path(nearest.x, nearest.y, new_node.x, new_node.y):
                continue

            near_nodes = self._near_nodes(new_node)
            new_node = self._choose_parent(new_node, near_nodes, nearest)
            self.node_list.append(new_node)
            self._rewire(new_node, near_nodes)

            dist_to_goal = math.hypot(new_node.x - goal.x, new_node.y - goal.y)
            if dist_to_goal <= self.expand_dis:
                final = self._steer(new_node, [goal.x, goal.y])
                if self._is_free_path(new_node.x, new_node.y, final.x, final.y):
                    final.parent = new_node
                    final.cost = new_node.cost + dist_to_goal
                    return self._final_path(final)

        best = min(self.node_list, key=lambda n: math.hypot(n.x - goal.x, n.y - goal.y))
        if math.hypot(best.x - goal.x, best.y - goal.y) > self.expand_dis * 2:
            return [], []
        final = self._steer(best, [goal.x, goal.y])
        if not self._is_free_path(best.x, best.y, final.x, final.y):
            return [], []
        final.parent = best
        return self._final_path(final)

    def _sample(self, goal: Node) -> list[float]:
        if random.randint(0, 100) > self.goal_sample_rate:
            return [
                random.uniform(self.min_x, self.max_x),
                random.uniform(self.min_y, self.max_y),
            ]
        return [goal.x, goal.y]

    def _nearest_node(self, p: list[float]) -> Node:
        return min(self.node_list, key=lambda n: (n.x - p[0]) ** 2 + (n.y - p[1]) ** 2)

    def _steer(self, from_node: Node, to_point: list[float]) -> Node:
        dx = to_point[0] - from_node.x
        dy = to_point[1] - from_node.y
        dist = math.hypot(dx, dy)
        if dist <= self.expand_dis:
            node = Node(to_point[0], to_point[1])
        else:
            theta = math.atan2(dy, dx)
            node = Node(
                from_node.x + self.expand_dis * math.cos(theta),
                from_node.y + self.expand_dis * math.sin(theta),
            )
        node.cost = from_node.cost + math.hypot(node.x - from_node.x, node.y - from_node.y)
        return node

    def _is_free_path(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(int(dist / self.path_resolution), 1)
        for i in range(steps + 1):
            t = i / steps
            if not self._point_free(x1 + t * (x2 - x1), y1 + t * (y2 - y1)):
                return False
        return True

    def _point_free(self, x: float, y: float) -> bool:
        if x < self.min_x or x > self.max_x or y < self.min_y or y > self.max_y:
            return False
        for cx, cy, r in self.obstacle_circles:
            if math.hypot(x - cx, y - cy) <= r + self.robot_radius:
                return False
        return True

    def _near_nodes(self, node: Node) -> list[Node]:
        n = len(self.node_list) + 1
        r = self.connect_circle_dist * math.sqrt(math.log(n) / n)
        return [
            other
            for other in self.node_list
            if math.hypot(other.x - node.x, other.y - node.y) <= r
        ]

    def _choose_parent(self, node: Node, near_nodes: list[Node], nearest: Node) -> Node:
        candidates = near_nodes if near_nodes else [nearest]
        best: Node | None = None
        best_cost = float("inf")
        for near in candidates:
            if not self._is_free_path(near.x, near.y, node.x, node.y):
                continue
            cost = near.cost + math.hypot(node.x - near.x, node.y - near.y)
            if cost < best_cost:
                best_cost = cost
                best = Node(node.x, node.y)
                best.cost = best_cost
                best.parent = near
        if best is None:
            best = Node(node.x, node.y)
            best.cost = nearest.cost + math.hypot(node.x - nearest.x, node.y - nearest.y)
            best.parent = nearest
        return best

    def _rewire(self, new_node: Node, near_nodes: list[Node]) -> None:
        for near in near_nodes:
            if near is new_node.parent:
                continue
            new_cost = new_node.cost + math.hypot(near.x - new_node.x, near.y - new_node.y)
            if new_cost < near.cost and self._is_free_path(new_node.x, new_node.y, near.x, near.y):
                near.parent = new_node
                near.cost = new_cost

    @staticmethod
    def _final_path(end_node: Node) -> tuple[list[float], list[float]]:
        rx: list[float] = []
        ry: list[float] = []
        node: Node | None = end_node
        while node is not None:
            rx.append(node.x)
            ry.append(node.y)
            node = node.parent
        return rx, ry


def plan_path(
    sx: float,
    sy: float,
    gx: float,
    gy: float,
    obstacle_circles: list[list[float]],
    world_bounds: list[float],
    robot_radius: float | None = None,
) -> tuple[list[float], list[float]]:
    """单次全局规划 — prepare.py 对此函数计时。"""
    bounds = (world_bounds[0], world_bounds[1], world_bounds[2], world_bounds[3])
    radius = config.robot_radius if robot_radius is None else robot_radius
    planner = RRTStar(
        obstacle_circles=obstacle_circles,
        bounds=bounds,
        expand_dis=config.expand_dis,
        path_resolution=config.path_resolution,
        goal_sample_rate=config.goal_sample_rate,
        max_iter=config.max_iter,
        connect_circle_dist=config.connect_circle_dist,
        robot_radius=radius,
    )
    return planner.planning(sx, sy, gx, gy)
