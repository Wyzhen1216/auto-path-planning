"""Load and validate evolution_manifest.yaml (Phase 4 Scheme A)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "evolution_manifest.yaml"

ALLOWED_TEMPLATES: dict[str, dict[str, Any]] = {
    "single": {
        "maps": "native",
        "min_stages": 1,
        "max_stages": 1,
        "stage_roles": {"global": ["dwa", "dijkstra", "astar", "rrt_star"]},
    },
    "grid_global_dwa": {
        "maps": "grid",
        "min_stages": 2,
        "max_stages": 2,
        "stage_roles": {
            "global": ["dijkstra", "astar"],
            "local": ["dwa"],
        },
    },
}


@dataclass
class PipelineStage:
    id: str
    algorithm: str
    role: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionManifest:
    template: str
    rationale: str
    stages: list[PipelineStage]

    @property
    def primary_algorithm(self) -> str:
        return self.stages[0].algorithm

    def stage_by_role(self, role: str) -> PipelineStage:
        for stage in self.stages:
            if stage.role == role:
                return stage
        raise KeyError(f"No stage with role={role!r}")


def _parse_yaml_scalar(line: str) -> str:
    return line.split(":", 1)[1].strip().split("#")[0].strip().strip('"').strip("'")


def _coerce_value(raw: str) -> Any:
    val = raw.strip().split("#")[0].strip().strip('"').strip("'")
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    try:
        if "." in val:
            return float(val)
        return int(val)
    except ValueError:
        return val


def load_evolution_manifest(path: Path | None = None) -> EvolutionManifest:
    path = path or MANIFEST_PATH
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}")

    template = ""
    rationale = ""
    stages: list[PipelineStage] = []
    current: dict[str, Any] | None = None
    in_params = False

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("template:"):
            template = _parse_yaml_scalar(stripped)
            in_params = False
            continue
        if stripped.startswith("rationale:"):
            rationale = _parse_yaml_scalar(stripped)
            in_params = False
            continue

        if stripped.startswith("- id:"):
            if current is not None:
                stages.append(_stage_from_dict(current))
            current = {"id": _parse_yaml_scalar(stripped.replace("- ", "", 1)), "params": {}}
            in_params = False
            continue

        if current is None:
            continue

        if stripped.startswith("algorithm:"):
            current["algorithm"] = _parse_yaml_scalar(stripped)
            in_params = False
        elif stripped.startswith("role:"):
            current["role"] = _parse_yaml_scalar(stripped)
            in_params = False
        elif stripped.startswith("params:"):
            rest = stripped.split(":", 1)[1].strip()
            if rest:
                in_params = False
            else:
                in_params = True
        elif in_params and ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            current.setdefault("params", {})[key.strip()] = _coerce_value(val)
        elif stripped.startswith("id:"):
            current["id"] = _parse_yaml_scalar(stripped)

    if current is not None:
        stages.append(_stage_from_dict(current))

    manifest = EvolutionManifest(template=template, rationale=rationale, stages=stages)
    _validate_manifest(manifest)
    return manifest


def _stage_from_dict(data: dict[str, Any]) -> PipelineStage:
    if "algorithm" not in data:
        raise ValueError(f"Stage missing algorithm: {data}")
    return PipelineStage(
        id=str(data.get("id", data["algorithm"])),
        algorithm=str(data["algorithm"]),
        role=str(data.get("role", "global")),
        params=dict(data.get("params") or {}),
    )


def _validate_manifest(manifest: EvolutionManifest) -> None:
    if manifest.template not in ALLOWED_TEMPLATES:
        raise ValueError(
            f"Unknown template {manifest.template!r}; allowed: {list(ALLOWED_TEMPLATES)}"
        )
    spec = ALLOWED_TEMPLATES[manifest.template]
    n = len(manifest.stages)
    if n < spec["min_stages"] or n > spec["max_stages"]:
        raise ValueError(
            f"Template {manifest.template} requires {spec['min_stages']}-{spec['max_stages']} stages, got {n}"
        )

    role_allow = spec["stage_roles"]
    for stage in manifest.stages:
        allowed = role_allow.get(stage.role)
        if allowed is None:
            raise ValueError(f"Template {manifest.template} does not allow role {stage.role!r}")
        if stage.algorithm not in allowed:
            raise ValueError(
                f"Stage {stage.id}: algorithm {stage.algorithm!r} not allowed for role "
                f"{stage.role!r} (allowed: {allowed})"
            )
