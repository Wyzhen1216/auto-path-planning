"""
固定评测脚本（对标 autoresearch 的 prepare.py）— Agent 禁止修改。

加载 maps/，调用 planner.dwa_control 做无 GUI 仿真，写 results.tsv。
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

import numpy as np

from planner import config, dwa_control, motion, state_collides

ROOT = Path(__file__).resolve().parent
MAPS_DIR = ROOT / "maps"
RESULTS_PATH = ROOT / "results.tsv"
BASELINE_PATH = ROOT / "baseline_results.json"

MAX_STEPS = 800

# quick：3 张代表性地图，约 30s/轮，适合过夜循环
QUICK_MAPS = ["pr_default.json", "obstacle_field.json", "narrow_passage.json"]


@dataclass
class MapSpec:
    map_id: str
    goal: np.ndarray
    initial: np.ndarray
    obstacles: np.ndarray


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


def load_map(path: Path) -> MapSpec:
    data = json.loads(path.read_text(encoding="utf-8"))
    return MapSpec(
        map_id=data["id"],
        goal=np.array(data["goal"], dtype=float),
        initial=np.array(data["initial"], dtype=float),
        obstacles=np.array(data["obstacles"], dtype=float),
    )


def list_map_files(mode: str) -> list[Path]:
    if mode == "quick":
        names = QUICK_MAPS
    else:
        names = sorted(p.name for p in MAPS_DIR.glob("*.json"))
    paths = [MAPS_DIR / n for n in names]
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing map files: {missing}")
    return paths


def simulate_map(spec: MapSpec) -> MapResult:
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

        dist_to_goal = math.hypot(x[0] - goal[0], x[1] - goal[1])
        if dist_to_goal <= cfg.robot_radius:
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
    """与 PROJECT_DECISIONS / knowhow 一致：success_rate ↑, path ↓, time ↓。"""
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


def save_baseline(summary: EvalSummary) -> None:
    payload = {
        "success_rate": summary.success_rate,
        "avg_path_length": summary.avg_path_length,
        "plan_time_ms": summary.plan_time_ms,
        "maps_evaluated": summary.maps_evaluated,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_baseline() -> EvalSummary | None:
    if not BASELINE_PATH.exists():
        return None
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return EvalSummary(
        success_rate=data["success_rate"],
        avg_path_length=data["avg_path_length"],
        plan_time_ms=data["plan_time_ms"],
        maps_evaluated=data["maps_evaluated"],
        per_map=[],
    )


def append_results_tsv(row: dict[str, str]) -> None:
    header = [
        "timestamp_utc",
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
        f.write("\t".join(row[h] for h in header) + "\n")


def run_eval(mode: str, save_baseline_flag: bool) -> EvalSummary:
    map_paths = list_map_files(mode)
    per_map = [simulate_map(load_map(p)) for p in map_paths]
    summary = aggregate(per_map)

    if save_baseline_flag or not BASELINE_PATH.exists():
        save_baseline(summary)

    return summary


def print_summary(summary: EvalSummary, mode: str) -> None:
    print(f"mode={mode} maps={summary.maps_evaluated}")
    print(f"success_rate={summary.success_rate:.4f}")
    print(f"avg_path_length={summary.avg_path_length:.4f}")
    print(f"plan_time_ms={summary.plan_time_ms:.3f}")
    for r in summary.per_map:
        status = "OK" if r.success else "FAIL"
        plen = f"{r.path_length:.2f}" if r.success else "n/a"
        print(f"  [{status}] {r.map_id} steps={r.steps} path_len={plen} plan_ms={r.mean_plan_time_ms:.2f}")


def main() -> int:
    parser = argparse.ArgumentParser(description="autopath fixed evaluator")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="将本次结果写入 baseline_results.json（首次 setup 时使用）",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="实验备注（写入 results.tsv 的 notes 列，建议：hyp=... | change=...）",
    )
    args = parser.parse_args()

    summary = run_eval(args.mode, save_baseline_flag=args.save_baseline)
    print_summary(summary, args.mode)

    baseline = load_baseline()
    better = ""
    if baseline is not None and BASELINE_PATH.exists() and not args.save_baseline:
        better = str(is_better(summary, baseline))
    elif args.save_baseline:
        better = "baseline_set"

    append_results_tsv(
        {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
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
    print(f"Wrote {RESULTS_PATH}")
    return 0 if summary.success_rate >= 1.0 - 1e-12 else 1


if __name__ == "__main__":
    sys.exit(main())
