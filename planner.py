"""
Phase 4 Scheme A — thin bootstrap.

Composite 评测走 evolution_manifest.yaml + planner_lib.runners；
template=single 时从此处 re-export 已配置的快照符号（便于 import planner）。
"""

from __future__ import annotations

from planner_lib.runtime import bootstrap_planner_exports

bootstrap_planner_exports(globals())
