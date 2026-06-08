"""Composite pipeline execution (Scheme A — fixed templates, manifest params)."""

from __future__ import annotations

import importlib
import math
import random
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

from planner_lib.manifest import EvolutionManifest, PipelineStage
from planner_lib.params import apply_params, validate_params


@dataclass
class StageResult:
    success: bool
    path_length: float
    plan_time_ms: float
    steps: int
    collision: bool


def _import_planner(algorithm: str):
    return importlib.import_module(f"planners.{algorithm}")


def _load_registry_editable(algorithm: str) -> list[str]:
    from prepare import read_registry

    reg = read_registry()
    algos = reg.get("algorithms") or {}
    if algorithm in algos and "editable_in_planner" in algos[algorithm]:
        return list(algos[algorithm]["editable_in_planner"])
    defaults: dict[str, list[str]] = {
        "dwa": [
            "to_goal_cost_gain",
            "speed_cost_gain",
            "obstacle_cost_gain",
            "predict_time",
            "v_resolution",
            "yaw_rate_resolution",
            "max_speed",
            "max_yaw_rate",
            "max_accel",
            "max_delta_yaw_rate",
            "robot_radius",
            "robot_stuck_flag_cons",
        ],
        "dijkstra": ["resolution", "robot_radius", "motion_model"],
        "astar": ["resolution", "robot_radius", "heuristic_weight", "motion_model"],
        "rrt_star": [
            "expand_dis",
            "path_resolution",
            "goal_sample_rate",
            "max_iter",
            "connect_circle_dist",
            "robot_radius",
        ],
    }
    return defaults.get(algorithm, [])


def configure_stage_module(stage: PipelineStage):
    mod = _import_planner(stage.algorithm)
    editable = _load_registry_editable(stage.algorithm)
    validate_params(stage.algorithm, stage.params, editable)
    apply_params(mod.config, stage.params)
    return mod


def segments_to_obstacle_points(
    obstacles: list[list[list[float]]], step: float = 0.5
) -> np.ndarray:
    points: list[list[float]] = []
    for segment in obstacles:
        for i in range(len(segment) - 1):
            x1, y1 = segment[i]
            x2, y2 = segment[i + 1]
            dist = math.hypot(x2 - x1, y2 - y1)
            n = max(int(dist / step), 1)
            for j in range(n + 1):
                t = j / n
                points.append([x1 + t * (x2 - x1), y1 + t * (y2 - y1)])
    if not points:
        return np.zeros((0, 2), dtype=float)
    return np.array(points, dtype=float)


def path_length_xy(rx: list[float], ry: list[float]) -> float:
    total = 0.0
    for i in range(len(rx) - 1):
        total += math.hypot(rx[i + 1] - rx[i], ry[i + 1] - ry[i])
    return total


def subsample_waypoints(
    rx: list[float], ry: list[float], spacing: float = 1.0
) -> list[tuple[float, float]]:
    if len(rx) < 2:
        return [(rx[0], ry[0])] if rx else []
    ordered = list(zip(reversed(rx), reversed(ry)))
    out: list[tuple[float, float]] = [ordered[0]]
    acc = 0.0
    for i in range(1, len(ordered)):
        dx = ordered[i][0] - ordered[i - 1][0]
        dy = ordered[i][1] - ordered[i - 1][1]
        acc += math.hypot(dx, dy)
        if acc >= spacing:
            out.append(ordered[i])
            acc = 0.0
    if out[-1] != ordered[-1]:
        out.append(ordered[-1])
    return out


def run_grid_global(
    stage: PipelineStage,
    sx: float,
    sy: float,
    gx: float,
    gy: float,
    ox: list[float],
    oy: list[float],
    resolution: float,
) -> tuple[list[float], list[float], float]:
    mod = configure_stage_module(stage)
    t0 = time.perf_counter()
    rx, ry = mod.plan_path(sx, sy, gx, gy, ox, oy)
    plan_ms = (time.perf_counter() - t0) * 1000.0
    success = len(rx) > 0 and math.hypot(rx[0] - gx, ry[0] - gy) <= resolution * 1.5
    if not success:
        return [], [], plan_ms
    return rx, ry, plan_ms


def run_sampling_global(
    stage: PipelineStage,
    sx: float,
    sy: float,
    gx: float,
    gy: float,
    obstacle_circles: list[list[float]],
    world_bounds: list[float],
    robot_radius: float,
    expand_dis: float,
) -> tuple[list[float], list[float], float]:
    mod = configure_stage_module(stage)
    random.seed(0)
    t0 = time.perf_counter()
    rx, ry = mod.plan_path(sx, sy, gx, gy, obstacle_circles, world_bounds, robot_radius)
    plan_ms = (time.perf_counter() - t0) * 1000.0
    success = len(rx) > 0 and math.hypot(rx[0] - gx, ry[0] - gy) <= expand_dis * 1.5
    if not success:
        return [], [], plan_ms
    return rx, ry, plan_ms


def run_dwa_track(
    stage: PipelineStage,
    start: np.ndarray,
    goal: np.ndarray,
    subgoals: list[tuple[float, float]],
    obstacles: np.ndarray,
    max_steps: int = 800,
) -> StageResult:
    mod = configure_stage_module(stage)
    config = mod.config
    dwa_control = mod.dwa_control
    motion = mod.motion
    state_collides = mod.state_collides

    x = np.array([start[0], start[1], 0.0, 0.0, 0.0], dtype=float)
    targets = subgoals if subgoals else [(float(goal[0]), float(goal[1]))]
    target_idx = 0
    current_goal = np.array(targets[target_idx], dtype=float)

    path_length = 0.0
    plan_times: list[float] = []
    collision = False
    success = False
    steps = 0

    for _ in range(max_steps):
        if target_idx < len(targets) - 1:
            if math.hypot(x[0] - current_goal[0], x[1] - current_goal[1]) <= config.robot_radius * 1.5:
                target_idx += 1
                current_goal = np.array(targets[target_idx], dtype=float)

        t0 = time.perf_counter()
        u, _ = dwa_control(x, config, current_goal, obstacles)
        plan_times.append((time.perf_counter() - t0) * 1000.0)

        x_prev = x.copy()
        x = motion(x, u, config.dt)
        steps += 1
        path_length += math.hypot(x[0] - x_prev[0], x[1] - x_prev[1])

        if state_collides(x, obstacles, config):
            collision = True
            break

        if math.hypot(x[0] - goal[0], x[1] - goal[1]) <= config.robot_radius:
            success = True
            break

    mean_plan = float(np.mean(plan_times)) if plan_times else float("inf")
    return StageResult(
        success=success and not collision,
        path_length=path_length if success and not collision else float("nan"),
        plan_time_ms=mean_plan,
        steps=steps,
        collision=collision,
    )


def simulate_single_stage(
    manifest: EvolutionManifest,
    *,
    simulate_fn,
    map_path,
) -> Any:
    """Configure planners snapshot from manifest, then run native simulate."""
    stage = manifest.stages[0]
    configure_stage_module(stage)
    return simulate_fn(map_path, stage.algorithm, use_snapshot=True)


def simulate_grid_global_dwa(
    manifest: EvolutionManifest,
    *,
    grid_spec,
    obstacles_to_ox_oy,
    max_steps: int = 800,
) -> StageResult:
    global_stage = manifest.stage_by_role("global")
    local_stage = manifest.stage_by_role("local")

    sx, sy = float(grid_spec.start[0]), float(grid_spec.start[1])
    gx, gy = float(grid_spec.goal[0]), float(grid_spec.goal[1])
    ox, oy = obstacles_to_ox_oy(grid_spec.obstacles, step=min(global_stage.params.get("resolution", 0.5), 0.5))

    rx, ry, global_ms = run_grid_global(
        global_stage, sx, sy, gx, gy, ox, oy, float(grid_spec.resolution)
    )
    if not rx:
        return StageResult(False, float("nan"), global_ms, 0, True)

    waypoints = subsample_waypoints(rx, ry, spacing=1.0)
    ob_points = segments_to_obstacle_points(grid_spec.obstacles, step=0.5)

    dwa_result = run_dwa_track(
        local_stage,
        grid_spec.start,
        grid_spec.goal,
        waypoints,
        ob_points,
        max_steps=max_steps,
    )

    total_plan_ms = global_ms + dwa_result.plan_time_ms
    return StageResult(
        success=dwa_result.success,
        path_length=dwa_result.path_length,
        plan_time_ms=total_plan_ms,
        steps=dwa_result.steps,
        collision=dwa_result.collision,
    )
