"""Phase 4 composite pipeline library — manifest-driven algorithm composition."""

from planner_lib.manifest import EvolutionManifest, load_evolution_manifest
from planner_lib.pipeline_id import compute_pipeline_id

__all__ = [
    "EvolutionManifest",
    "compute_pipeline_id",
    "load_evolution_manifest",
]
