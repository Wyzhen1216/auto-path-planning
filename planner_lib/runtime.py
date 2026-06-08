"""Bootstrap planner.py exports from evolution_manifest (single template)."""

from __future__ import annotations

from types import ModuleType
from typing import Any

from planner_lib.manifest import load_evolution_manifest
from planner_lib.runners import configure_stage_module


def bootstrap_planner_exports(namespace: dict[str, Any]) -> None:
    """For template=single, re-export configured planner module symbols into planner.py."""
    manifest = load_evolution_manifest()
    if manifest.template != "single":
        raise RuntimeError(
            f"planner.py bootstrap only supports template=single; got {manifest.template!r}. "
            "Composite templates are executed via prepare.py + planner_lib.runners."
        )
    stage = manifest.stages[0]
    mod: ModuleType = configure_stage_module(stage)
    for name in (
        "config",
        "plan_path",
        "dwa_control",
        "motion",
        "state_collides",
        "Config",
        "DijkstraPlanner",
        "AStarPlanner",
        "RRTStar",
    ):
        if hasattr(mod, name):
            namespace[name] = getattr(mod, name)
