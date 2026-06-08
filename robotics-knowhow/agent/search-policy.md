# Agent 搜索策略 — Phase 4 Composite (Scheme A)

完整决策见 [../PROJECT_DECISIONS.md](../PROJECT_DECISIONS.md)。

Phase 3 Portfolio 仍可通过 `registry.yaml` → `evolution_mode: portfolio` 启用（legacy）。

---

## 模式

`registry.yaml` 中 `evolution_mode: composite` 时启用 **Composite 自进化**：

- Agent **每轮**编辑 `evolution_manifest.yaml`（template、stages、params）
- 只与该 pipeline 的 `baselines/pipelines/<pipeline_id>.json` 比较
- **禁止**跨 pipeline_id 比较 path_length
- **禁止**改 `planner_lib/`、`prepare.py`

---

## Composite 每轮流程

```
1. 读 registry.yaml（allowed_pipelines、portfolio_allowed_algorithms）
2. 读 evolution_manifest.yaml，确认 template + stages 合法
3. 读各 stage 对应 knowhow 卡片
4. 提出假设，只改 evolution_manifest.yaml（params / stage algorithm）
5. git add evolution_manifest.yaml && git commit
6. python prepare.py --mode full --notes "pipeline=<id> | hyp=... | change=..."
7. better_than_baseline 对比 baselines/pipelines/<pipeline_id>.json → keep 或 rollback
8. 写 experiment_log.md
```

`pipeline_id` 示例：

- `single-rrt_star-global`
- `grid_global_dwa-dijkstra-global-dwa-local`

---

## Pipeline 模板

| template | stages | 地图 |
|----------|--------|------|
| `single` | 1× global（任意 allowed 算法） | 算法 native |
| `grid_global_dwa` | global: dijkstra/astar + local: dwa | `maps/grid/` |

切换 composite 模板：编辑 `evolution_manifest.yaml` 的 `template` 与 `stages` 块。  
`grid_global_dwa` 参考示例：`examples/evolution_manifest.grid_global_dwa.yaml`。

---

## 允许 / 禁止

**允许修改**：

- `evolution_manifest.yaml`

**禁止**：

- `prepare.py`、`program.md`、`maps/`、`planners/`、`planner_lib/`
- 未在 `allowed_pipelines` 注册的 template
- stage 算法不在 `portfolio_allowed_algorithms` 或 template role 允许列表
- 删碰撞检测、加 pip 依赖
- 提交 `results.tsv`、`baselines/`、`experiment_log.md`

---

## Rollback

```powershell
git reset HEAD~1
git checkout HEAD -- evolution_manifest.yaml
```

---

## 指标

字典序：success_rate ↑ → avg_path_length ↓ → plan_time_ms ↓

仅与 **当前 pipeline_id** 的 baseline 比较。

---

## Setup（Composite 首次）

```powershell
pip install -e .
python prepare.py --save-all-pipeline-baselines --mode full
```

确认 `baselines/pipelines/` 下 json 与当前 manifest 的 pipeline_id 一致。

Quick 冒烟（不写 baseline 对比）：

```powershell
python prepare.py --mode quick
```
