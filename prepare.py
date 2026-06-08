"""
固定评测脚本（对标 autoresearch 的 prepare.py）— Agent 禁止修改。

Phase 3 Portfolio / Phase 4 Composite：Agent 从 registry 选模式；
Phase 3: portfolio_manifest.yaml；Phase 4: evolution_manifest.yaml + planner_lib。
分算法 baseline：baselines/<algorithm>.json
Pipeline baseline：baselines/pipelines/<pipeline_id>.json
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
KNOWHOW = ROOT / "robotics-knowhow"
REGISTRY_PATH = KNOWHOW / "registry.yaml"
MANIFEST_PATH = ROOT / "portfolio_manifest.yaml"
EVOLUTION_MANIFEST_PATH = ROOT / "evolution_manifest.yaml"
RESULTS_PATH = ROOT / "results.tsv"
BASELINE_PATH = ROOT / "baseline_results.json"  # 兼容旧 Phase 1/2
BASELINES_DIR = ROOT / "baselines"
PIPELINES_BASELINE_DIR = BASELINES_DIR / "pipelines"

ALL_ALGORITHMS = ("dwa", "dijkstra", "astar", "rrt_star")

MAX_STEPS = 800

QUICK_DWA_MAPS = ["pr_default.json", "obstacle_field.json", "narrow_passage.json"]
QUICK_GRID_MAPS = ["simple_corridor.json", "open_room.json", "narrow_passage.json"]
QUICK_SAMPLING_MAPS = ["circles_obstacles.json", "sparse_circles.json", "narrow_gap.json"]

ALGO_MAPS_DIR = {
    "dwa": ROOT / "maps" / "dwa",
    "dijkstra": ROOT / "maps" / "grid",
    "astar": ROOT / "maps" / "grid",
    "rrt_star": ROOT / "maps" / "sampling",
}


@dataclass
class DwaMapSpec:
    map_id: str
    goal: np.ndarray
    initial: np.ndarray
    obstacles: np.ndarray


@dataclass
class GridMapSpec:
    map_id: str
    resolution: float
    robot_radius: float
    start: np.ndarray
    goal: np.ndarray
    obstacles: list[list[list[float]]]


@dataclass
class SamplingMapSpec:
    map_id: str
    start: np.ndarray
    goal: np.ndarray
    robot_radius: float
    obstacle_circles: list[list[float]]
    world_bounds: list[float]


@dataclass
class MapResult:
    map_id: str
    success: bool
    steps: int
    path_length: float
    mean_plan_time_ms: float
    collision: bool


@dataclass
class EvalSummary:
    success_rate: float
    avg_path_length: float
    plan_time_ms: float
    maps_evaluated: int
    per_map: list[MapResult]


def _parse_yaml_scalar(line: str) -> str:
    return line.split(":", 1)[1].strip().split("#")[0].strip().strip('"').strip("'")


def read_registry() -> dict[str, Any]:
    """轻量 YAML 解析（无 PyYAML 依赖）。"""
    result: dict[str, Any] = {
        "evolution_mode": "locked",
        "active_algorithm": "dijkstra",
        "portfolio_allowed_algorithms": list(ALL_ALGORITHMS),
        "allowed_pipelines": ["single", "grid_global_dwa"],
    }
    if not REGISTRY_PATH.exists():
        return result

    text = REGISTRY_PATH.read_text(encoding="utf-8")
    in_portfolio_list = False
    in_pipelines_list = False
    portfolio: list[str] = []
    pipelines: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("evolution_mode:"):
            result["evolution_mode"] = _parse_yaml_scalar(line)
            in_portfolio_list = False
            in_pipelines_list = False
        elif line.startswith("active_algorithm:"):
            result["active_algorithm"] = _parse_yaml_scalar(line)
            in_portfolio_list = False
            in_pipelines_list = False
        elif line.startswith("portfolio_allowed_algorithms:"):
            in_portfolio_list = True
            in_pipelines_list = False
            portfolio = []
        elif line.startswith("allowed_pipelines:"):
            in_pipelines_list = True
            in_portfolio_list = False
            pipelines = []
        elif in_portfolio_list:
            if line.startswith("- "):
                portfolio.append(_parse_yaml_scalar("x:" + line[1:].strip()))
            else:
                in_portfolio_list = False
        elif in_pipelines_list:
            if line.startswith("- "):
                pipelines.append(_parse_yaml_scalar("x:" + line[1:].strip()))
            else:
                in_pipelines_list = False
        elif line.startswith("algorithms:"):
            in_portfolio_list = False
            in_pipelines_list = False

    if portfolio:
        result["portfolio_allowed_algorithms"] = portfolio
    if pipelines:
        result["allowed_pipelines"] = pipelines
    return result


def read_portfolio_manifest() -> str | None:
    if not MANIFEST_PATH.exists():
        return None
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("algorithm:"):
            return _parse_yaml_scalar(stripped)
    return None


def resolve_default_algorithm(explicit: str | None) -> str:
    reg = read_registry()
    if explicit:
        algo = explicit
    elif reg["evolution_mode"] == "portfolio":
        algo = read_portfolio_manifest() or reg["active_algorithm"]
    else:
        algo = reg["active_algorithm"]

    allowed = reg["portfolio_allowed_algorithms"]
    if reg["evolution_mode"] == "portfolio" and algo not in allowed:
        raise ValueError(
            f"Algorithm '{algo}' not in portfolio_allowed_algorithms: {allowed}"
        )
    if algo not in ALL_ALGORITHMS:
        raise ValueError(f"Unknown algorithm: {algo}")
    return algo


def read_active_algorithm() -> str:
    return read_registry()["active_algorithm"]


def baseline_file(algorithm: str) -> Path:
    return BASELINES_DIR / f"{algorithm}.json"


def pipeline_baseline_file(pipeline_id: str) -> Path:
    safe = pipeline_id.replace("/", "_")
    return PIPELINES_BASELINE_DIR / f"{safe}.json"


def load_dwa_map(path: Path) -> DwaMapSpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    map_id = data.get("id") or data.get("name") or path.stem
    return DwaMapSpec(
        map_id=map_id,
        goal=np.array(data["goal"], dtype=float),
        initial=np.array(data["initial"], dtype=float),
        obstacles=np.array(data["obstacles"], dtype=float),
    )


def load_grid_map(path: Path) -> GridMapSpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    map_id = data.get("id") or data.get("name") or path.stem
    return GridMapSpec(
        map_id=map_id,
        resolution=float(data["resolution"]),
        robot_radius=float(data["robot_radius"]),
        start=np.array(data["start"], dtype=float),
        goal=np.array(data["goal"], dtype=float),
        obstacles=data["obstacles"],
    )


def load_sampling_map(path: Path) -> SamplingMapSpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    map_id = data.get("id") or data.get("name") or path.stem
    return SamplingMapSpec(
        map_id=map_id,
        start=np.array(data["start"], dtype=float),
        goal=np.array(data["goal"], dtype=float),
        robot_radius=float(data["robot_radius"]),
        obstacle_circles=data["obstacle_circles"],
        world_bounds=[float(v) for v in data["world_bounds"]],
    )


def list_map_files(algorithm: str, mode: str) -> list[Path]:
    maps_dir = ALGO_MAPS_DIR[algorithm]
    if mode == "quick":
        if algorithm == "dwa":
            names = QUICK_DWA_MAPS
        elif algorithm in ("dijkstra", "astar"):
            names = QUICK_GRID_MAPS
        else:
            names = QUICK_SAMPLING_MAPS
    else:
        names = sorted(p.name for p in maps_dir.glob("*.json"))
    paths = [maps_dir / n for n in names]
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing map files: {missing}")
    return paths


def list_map_files_for_template(template: str, primary_algorithm: str, mode: str) -> list[Path]:
    from planner_lib.manifest import ALLOWED_TEMPLATES

    spec = ALLOWED_TEMPLATES[template]
    if spec["maps"] == "grid":
        maps_dir = ALGO_MAPS_DIR["dijkstra"]
        names = QUICK_GRID_MAPS if mode == "quick" else sorted(p.name for p in maps_dir.glob("*.json"))
    elif spec["maps"] == "native":
        return list_map_files(primary_algorithm, mode)
    else:
        raise ValueError(f"Unknown maps spec for template {template}")
    paths = [maps_dir / n for n in names]
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing map files: {missing}")
    return paths


def obstacles_segments_to_ox_oy(
    obstacles: list[list[list[float]]], step: float = 0.5
) -> tuple[list[float], list[float]]:
    ox: list[float] = []
    oy: list[float] = []
    for segment in obstacles:
        for i in range(len(segment) - 1):
            x1, y1 = segment[i]
            x2, y2 = segment[i + 1]
            dist = math.hypot(x2 - x1, y2 - y1)
            n = max(int(dist / step), 1)
            for j in range(n + 1):
                t = j / n
                ox.append(x1 + t * (x2 - x1))
                oy.append(y1 + t * (y2 - y1))
    return ox, oy


def path_length_xy(rx: list[float], ry: list[float]) -> float:
    total = 0.0
    for i in range(len(rx) - 1):
        total += math.hypot(rx[i + 1] - rx[i], ry[i + 1] - ry[i])
    return total


def simulate_dwa_map(spec: DwaMapSpec, *, use_snapshot: bool = False) -> MapResult:
    if use_snapshot:
        from planners.dwa import config, dwa_control, motion, state_collides
    else:
        from planner import config, dwa_control, motion, state_collides

    x = spec.initial.copy()
    goal = spec.goal
    ob = spec.obstacles
    cfg = config

    path_length = 0.0
    plan_times_ms: list[float] = []
    collision = False
    success = False
    steps = 0

    for _ in range(MAX_STEPS):
        t0 = time.perf_counter()
        u, _ = dwa_control(x, cfg, goal, ob)
        plan_times_ms.append((time.perf_counter() - t0) * 1000.0)

        x_prev = x.copy()
        x = motion(x, u, cfg.dt)
        steps += 1
        path_length += math.hypot(x[0] - x_prev[0], x[1] - x_prev[1])

        if state_collides(x, ob, cfg):
            collision = True
            break

        if math.hypot(x[0] - goal[0], x[1] - goal[1]) <= cfg.robot_radius:
            success = True
            break

    mean_plan = float(np.mean(plan_times_ms)) if plan_times_ms else float("inf")
    return MapResult(
        map_id=spec.map_id,
        success=success and not collision,
        steps=steps,
        path_length=path_length if success and not collision else float("nan"),
        mean_plan_time_ms=mean_plan,
        collision=collision,
    )


def simulate_grid_map(spec: GridMapSpec, algorithm: str, *, use_snapshot: bool = False) -> MapResult:
    if use_snapshot:
        if algorithm == "dijkstra":
            from planners.dijkstra import config, plan_path
        elif algorithm == "astar":
            from planners.astar import config, plan_path
        else:
            raise ValueError(f"Unsupported grid algorithm: {algorithm}")
    else:
        from planner import config, plan_path

    ox, oy = obstacles_segments_to_ox_oy(spec.obstacles, step=min(config.resolution, 0.5))
    sx, sy = float(spec.start[0]), float(spec.start[1])
    gx, gy = float(spec.goal[0]), float(spec.goal[1])

    t0 = time.perf_counter()
    rx, ry = plan_path(sx, sy, gx, gy, ox, oy)
    plan_ms = (time.perf_counter() - t0) * 1000.0

    success = len(rx) > 0 and len(ry) > 0
    if success:
        end_dist = math.hypot(rx[0] - gx, ry[0] - gy)
        success = end_dist <= config.resolution * 1.5
    path_len = path_length_xy(rx, ry) if success else float("nan")

    return MapResult(
        map_id=spec.map_id,
        success=success,
        steps=len(rx),
        path_length=path_len,
        mean_plan_time_ms=plan_ms,
        collision=not success,
    )


def simulate_sampling_map(spec: SamplingMapSpec, *, use_snapshot: bool = False) -> MapResult:
    import random

    if use_snapshot:
        from planners.rrt_star import config, plan_path
    else:
        from planner import config, plan_path

    random.seed(0)

    sx, sy = float(spec.start[0]), float(spec.start[1])
    gx, gy = float(spec.goal[0]), float(spec.goal[1])

    t0 = time.perf_counter()
    rx, ry = plan_path(
        sx, sy, gx, gy, spec.obstacle_circles, spec.world_bounds, spec.robot_radius
    )
    plan_ms = (time.perf_counter() - t0) * 1000.0

    success = len(rx) > 0 and len(ry) > 0
    if success:
        end_dist = math.hypot(rx[0] - gx, ry[0] - gy)
        success = end_dist <= config.expand_dis * 1.5
    path_len = path_length_xy(rx, ry) if success else float("nan")

    return MapResult(
        map_id=spec.map_id,
        success=success,
        steps=len(rx),
        path_length=path_len,
        mean_plan_time_ms=plan_ms,
        collision=not success,
    )


def simulate_map(path: Path, algorithm: str, *, use_snapshot: bool = False) -> MapResult:
    if algorithm == "dwa":
        return simulate_dwa_map(load_dwa_map(path), use_snapshot=use_snapshot)
    if algorithm in ("dijkstra", "astar"):
        return simulate_grid_map(load_grid_map(path), algorithm, use_snapshot=use_snapshot)
    if algorithm == "rrt_star":
        return simulate_sampling_map(load_sampling_map(path), use_snapshot=use_snapshot)
    raise ValueError(f"Unknown algorithm: {algorithm}")


def aggregate(results: list[MapResult]) -> EvalSummary:
    n = len(results)
    successes = [r for r in results if r.success]
    success_rate = len(successes) / n if n else 0.0

    if successes:
        avg_path = float(np.mean([r.path_length for r in successes]))
        plan_ms = float(np.mean([r.mean_plan_time_ms for r in results]))
    else:
        avg_path = float("inf")
        plan_ms = float(np.mean([r.mean_plan_time_ms for r in results])) if results else float("inf")

    return EvalSummary(
        success_rate=success_rate,
        avg_path_length=avg_path,
        plan_time_ms=plan_ms,
        maps_evaluated=n,
        per_map=results,
    )


def is_better(candidate: EvalSummary, baseline: EvalSummary) -> bool:
    if candidate.success_rate > baseline.success_rate + 1e-12:
        return True
    if candidate.success_rate < baseline.success_rate - 1e-12:
        return False
    if candidate.avg_path_length < baseline.avg_path_length - 1e-9:
        return True
    if candidate.avg_path_length > baseline.avg_path_length + 1e-9:
        return False
    return candidate.plan_time_ms < baseline.plan_time_ms - 1e-9


def git_commit_short() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "no-git"


def save_baseline(summary: EvalSummary, algorithm: str) -> None:
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "algorithm": algorithm,
        "success_rate": summary.success_rate,
        "avg_path_length": summary.avg_path_length,
        "plan_time_ms": summary.plan_time_ms,
        "maps_evaluated": summary.maps_evaluated,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    baseline_file(algorithm).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # 兼容旧工具链：同步写一份指向当前算法的 baseline_results.json
    BASELINE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_baseline(algorithm: str) -> EvalSummary | None:
    path = baseline_file(algorithm)
    if not path.exists():
        if BASELINE_PATH.exists():
            data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
            if data.get("algorithm", algorithm) == algorithm:
                return EvalSummary(
                    success_rate=data["success_rate"],
                    avg_path_length=data["avg_path_length"],
                    plan_time_ms=data["plan_time_ms"],
                    maps_evaluated=data["maps_evaluated"],
                    per_map=[],
                )
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return EvalSummary(
        success_rate=data["success_rate"],
        avg_path_length=data["avg_path_length"],
        plan_time_ms=data["plan_time_ms"],
        maps_evaluated=data["maps_evaluated"],
        per_map=[],
    )


def save_pipeline_baseline(summary: EvalSummary, pipeline_id: str, manifest_template: str) -> None:
    PIPELINES_BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "pipeline_id": pipeline_id,
        "template": manifest_template,
        "success_rate": summary.success_rate,
        "avg_path_length": summary.avg_path_length,
        "plan_time_ms": summary.plan_time_ms,
        "maps_evaluated": summary.maps_evaluated,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    pipeline_baseline_file(pipeline_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_pipeline_baseline(pipeline_id: str) -> EvalSummary | None:
    path = pipeline_baseline_file(pipeline_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return EvalSummary(
        success_rate=data["success_rate"],
        avg_path_length=data["avg_path_length"],
        plan_time_ms=data["plan_time_ms"],
        maps_evaluated=data["maps_evaluated"],
        per_map=[],
    )


def save_all_baselines(mode: str) -> None:
    for algo in read_registry()["portfolio_allowed_algorithms"]:
        summary = run_eval(algo, mode, save_baseline_flag=True, use_snapshot=True)
        print_summary(summary, algo, mode)
        print(f"  -> baselines/{algo}.json")


def append_results_tsv(row: dict[str, str]) -> None:
    header = [
        "timestamp_utc",
        "algorithm",
        "pipeline_id",
        "template",
        "mode",
        "git_commit",
        "success_rate",
        "avg_path_length",
        "plan_time_ms",
        "maps_evaluated",
        "better_than_baseline",
        "notes",
    ]
    write_header = not RESULTS_PATH.exists() or RESULTS_PATH.stat().st_size == 0
    with RESULTS_PATH.open("a", encoding="utf-8") as f:
        if write_header:
            f.write("\t".join(header) + "\n")
        f.write("\t".join(row.get(h, "") for h in header) + "\n")


def run_eval(
    algorithm: str,
    mode: str,
    save_baseline_flag: bool,
    *,
    use_snapshot: bool = False,
) -> EvalSummary:
    map_paths = list_map_files(algorithm, mode)
    per_map = [simulate_map(p, algorithm, use_snapshot=use_snapshot) for p in map_paths]
    summary = aggregate(per_map)
    if save_baseline_flag or not baseline_file(algorithm).exists():
        save_baseline(summary, algorithm)
    return summary


def simulate_composite_map(path: Path, manifest) -> MapResult:
    from planner_lib.runners import simulate_grid_global_dwa, simulate_single_stage

    if manifest.template == "single":
        return simulate_single_stage(manifest, simulate_fn=simulate_map, map_path=path)
    if manifest.template == "grid_global_dwa":
        spec = load_grid_map(path)
        result = simulate_grid_global_dwa(
            manifest,
            grid_spec=spec,
            obstacles_to_ox_oy=obstacles_segments_to_ox_oy,
        )
        return MapResult(
            map_id=spec.map_id,
            success=result.success,
            steps=result.steps,
            path_length=result.path_length,
            mean_plan_time_ms=result.plan_time_ms,
            collision=result.collision,
        )
    raise ValueError(f"Unsupported composite template: {manifest.template}")


def run_composite_eval(manifest, mode: str, save_baseline_flag: bool) -> EvalSummary:
    from planner_lib.pipeline_id import compute_pipeline_id

    pipeline_id = compute_pipeline_id(manifest)
    map_paths = list_map_files_for_template(manifest.template, manifest.primary_algorithm, mode)
    per_map = [simulate_composite_map(p, manifest) for p in map_paths]
    summary = aggregate(per_map)
    if save_baseline_flag or not pipeline_baseline_file(pipeline_id).exists():
        save_pipeline_baseline(summary, pipeline_id, manifest.template)
    return summary


def save_all_pipeline_baselines(mode: str) -> None:
    from planner_lib.manifest import load_evolution_manifest
    from planner_lib.pipeline_id import compute_pipeline_id

    manifest_paths = {
        "single": EVOLUTION_MANIFEST_PATH,
        "grid_global_dwa": ROOT / "examples" / "evolution_manifest.grid_global_dwa.yaml",
    }
    for template, path in manifest_paths.items():
        if not path.exists():
            print(f"skip template={template}: missing {path}", file=sys.stderr)
            continue
        manifest = load_evolution_manifest(path)
        if manifest.template != template:
            print(f"skip {path}: template mismatch {manifest.template}", file=sys.stderr)
            continue
        summary = run_composite_eval(manifest, mode, save_baseline_flag=True)
        pid = compute_pipeline_id(manifest)
        print_summary(summary, manifest.primary_algorithm, mode)
        print(f"  -> baselines/pipelines/{pid}.json")


def print_summary(summary: EvalSummary, algorithm: str, mode: str) -> None:
    print(f"algorithm={algorithm} mode={mode} maps={summary.maps_evaluated}")
    print(f"success_rate={summary.success_rate:.4f}")
    print(f"avg_path_length={summary.avg_path_length:.4f}")
    print(f"plan_time_ms={summary.plan_time_ms:.3f}")
    for r in summary.per_map:
        status = "OK" if r.success else "FAIL"
        plen = f"{r.path_length:.2f}" if r.success else "n/a"
        print(f"  [{status}] {r.map_id} steps={r.steps} path_len={plen} plan_ms={r.mean_plan_time_ms:.2f}")


def validate_composite_manifest(manifest, reg: dict[str, Any]) -> None:
    allowed = reg.get("allowed_pipelines") or []
    if allowed and manifest.template not in allowed:
        raise ValueError(
            f"Template {manifest.template!r} not in allowed_pipelines: {allowed}"
        )
    portfolio = reg.get("portfolio_allowed_algorithms") or list(ALL_ALGORITHMS)
    for stage in manifest.stages:
        if stage.algorithm not in portfolio:
            raise ValueError(
                f"Stage {stage.id}: algorithm {stage.algorithm!r} not in "
                f"portfolio_allowed_algorithms: {portfolio}"
            )


def main() -> int:
    reg = read_registry()
    parser = argparse.ArgumentParser(description="autopath fixed evaluator (Phase 3/4)")
    parser.add_argument(
        "--algorithm",
        choices=list(ALL_ALGORITHMS),
        default=None,
        help="Portfolio/locked 模式：本轮评测算法",
    )
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument("--save-baseline", action="store_true", help="写入 baselines/<algorithm>.json")
    parser.add_argument(
        "--save-all-baselines",
        action="store_true",
        help="对 portfolio_allowed_algorithms 全部 save-baseline（Setup 用）",
    )
    parser.add_argument(
        "--save-pipeline-baseline",
        action="store_true",
        help="Composite：写入 baselines/pipelines/<pipeline_id>.json",
    )
    parser.add_argument(
        "--save-all-pipeline-baselines",
        action="store_true",
        help="Composite Setup：为各内置 manifest 写入 pipeline baseline",
    )
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    if args.save_all_baselines:
        print(f"evolution_mode={reg['evolution_mode']} save_all mode={args.mode}")
        save_all_baselines(args.mode)
        print(f"Wrote baselines under {BASELINES_DIR}")
        return 0

    if args.save_all_pipeline_baselines:
        print(f"evolution_mode={reg['evolution_mode']} save_all_pipeline mode={args.mode}")
        save_all_pipeline_baselines(args.mode)
        print(f"Wrote pipeline baselines under {PIPELINES_BASELINE_DIR}")
        return 0

    if reg["evolution_mode"] == "composite":
        from planner_lib.manifest import load_evolution_manifest
        from planner_lib.pipeline_id import compute_pipeline_id

        manifest = load_evolution_manifest()
        validate_composite_manifest(manifest, reg)
        pipeline_id = compute_pipeline_id(manifest)
        summary = run_composite_eval(
            manifest,
            args.mode,
            save_baseline_flag=args.save_pipeline_baseline,
        )
        print_summary(summary, manifest.primary_algorithm, args.mode)

        baseline = load_pipeline_baseline(pipeline_id)
        better = ""
        bl_path = pipeline_baseline_file(pipeline_id)
        if baseline is not None and bl_path.exists() and not args.save_pipeline_baseline:
            better = str(is_better(summary, baseline))
        elif args.save_pipeline_baseline:
            better = "baseline_set"

        append_results_tsv(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "algorithm": manifest.primary_algorithm,
                "pipeline_id": pipeline_id,
                "template": manifest.template,
                "mode": args.mode,
                "git_commit": git_commit_short(),
                "success_rate": f"{summary.success_rate:.6f}",
                "avg_path_length": f"{summary.avg_path_length:.6f}",
                "plan_time_ms": f"{summary.plan_time_ms:.6f}",
                "maps_evaluated": str(summary.maps_evaluated),
                "better_than_baseline": better,
                "notes": " ".join(args.notes.split()),
            }
        )
        print(f"pipeline_id={pipeline_id} template={manifest.template}")
        print(f"baseline={bl_path}")
        print(f"Wrote {RESULTS_PATH}")
        return 0 if summary.success_rate >= 1.0 - 1e-12 else 1

    if args.save_pipeline_baseline or args.save_all_pipeline_baselines:
        print(
            "warning: --save-pipeline-baseline(s) 仅在 evolution_mode=composite 时生效",
            file=sys.stderr,
        )

    algorithm = resolve_default_algorithm(args.algorithm)
    if reg["evolution_mode"] == "portfolio":
        manifest_algo = read_portfolio_manifest()
        if args.algorithm and manifest_algo and args.algorithm != manifest_algo:
            print(
                f"warning: --algorithm={args.algorithm} 与 portfolio_manifest "
                f"({manifest_algo}) 不一致，以 CLI 为准",
                file=sys.stderr,
            )

    summary = run_eval(algorithm, args.mode, save_baseline_flag=args.save_baseline)
    print_summary(summary, algorithm, args.mode)

    baseline = load_baseline(algorithm)
    better = ""
    bl_path = baseline_file(algorithm)
    if baseline is not None and bl_path.exists() and not args.save_baseline:
        better = str(is_better(summary, baseline))
    elif args.save_baseline:
        better = "baseline_set"

    append_results_tsv(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "algorithm": algorithm,
            "pipeline_id": "",
            "template": "",
            "mode": args.mode,
            "git_commit": git_commit_short(),
            "success_rate": f"{summary.success_rate:.6f}",
            "avg_path_length": f"{summary.avg_path_length:.6f}",
            "plan_time_ms": f"{summary.plan_time_ms:.6f}",
            "maps_evaluated": str(summary.maps_evaluated),
            "better_than_baseline": better,
            "notes": " ".join(args.notes.split()),
        }
    )
    print(f"baseline={bl_path}")
    print(f"Wrote {RESULTS_PATH}")
    return 0 if summary.success_rate >= 1.0 - 1e-12 else 1


if __name__ == "__main__":
    sys.exit(main())
