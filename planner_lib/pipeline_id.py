"""Stable pipeline identifiers for baselines/pipelines/."""

from __future__ import annotations

from planner_lib.manifest import EvolutionManifest


def compute_pipeline_id(manifest: EvolutionManifest) -> str:
    """Identity from template + stage algorithms/roles (not param values)."""
    parts = [manifest.template]
    for stage in manifest.stages:
        parts.append(stage.algorithm)
        if stage.role:
            parts.append(stage.role)
    return "-".join(parts)
