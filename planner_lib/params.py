"""Apply and validate manifest params against registry editable lists."""

from __future__ import annotations

from typing import Any


def apply_params(config: Any, params: dict[str, Any]) -> None:
    """Set attributes on planner Config from manifest params dict."""
    for key, value in params.items():
        if not hasattr(config, key):
            raise ValueError(f"Unknown config param: {key}")
        setattr(config, key, value)


def validate_params(algorithm: str, params: dict[str, Any], editable: list[str]) -> None:
    unknown = [k for k in params if k not in editable]
    if unknown:
        raise ValueError(
            f"Params {unknown} not in editable_in_planner for {algorithm}: {editable}"
        )
