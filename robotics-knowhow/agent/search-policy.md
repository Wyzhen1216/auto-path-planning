# Agent 搜索策略 — Phase 3 Portfolio

完整决策见 [../PROJECT_DECISIONS.md](../PROJECT_DECISIONS.md)。

---

## 模式

`registry.yaml` 中 `evolution_mode: portfolio` 时启用 **Portfolio 自进化**：

- Agent **每轮**从 `portfolio_allowed_algorithms` 中**自选**一个算法
- 只与该算法自己的 `baselines/<algo>.json` 比较
- **禁止**跨算法比较 path_length（地图与 eval_mode 不同）

`evolution_mode: locked` 时退回 Phase 2：人类锁 `active_algorithm`。

---

## Portfolio 每轮流程

```
1. 读 registry.yaml + index.md 选型
2. 决定本轮算法（可继续上一轮或切换）
3. 若切换：Copy-Item planners\<algo>.py planner.py -Force
4. 更新 portfolio_manifest.yaml 的 algorithm + rationale
5. 读对应 knowhow 卡片，只改 planner.py 内 editable 参数/逻辑
6. git add planner.py portfolio_manifest.yaml && git commit
7. python prepare.py --mode full --notes "algo=<algo> | hyp=... | change=..."
8. better_than_baseline 对比 baselines/<algo>.json → keep 或 rollback
9. 写 experiment_log.md
```

---

## 算法与地图

| 算法 | 卡片 | eval_mode | maps_dir | 快照 |
|------|------|-----------|----------|------|
| dijkstra | [dijkstra.md](../domains/path-planning/dijkstra.md) | grid | maps/grid/ | planners/dijkstra.py |
| astar | [astar.md](../domains/path-planning/astar.md) | grid | maps/grid/ | planners/astar.py |
| rrt_star | [rrt-star.md](../domains/path-planning/rrt-star.md) | sampling | maps/sampling/ | planners/rrt_star.py |
| dwa | [dwa.md](../domains/path-planning/dwa.md) | dwa | maps/dwa/ | planners/dwa.py |

**评测始终调用 `planner.py`**（不是 `planners/` 目录）。切换算法必须复制快照到 `planner.py`。

---

## 允许 / 禁止

**允许修改**：
- `planner.py`
- `portfolio_manifest.yaml`（声明本轮算法）

**禁止**：
- `prepare.py`、`program.md`、`maps/`、`planners/` 快照目录
- 在 planner.py 中混入两种算法的 plan_path 接口（一次只服务一个算法）
- 删碰撞检测、加 pip 依赖
- 提交 `results.tsv`、`baselines/`、`experiment_log.md`

---

## 切换算法示例（PowerShell）

```powershell
Copy-Item planners\astar.py planner.py -Force
# 编辑 portfolio_manifest.yaml: algorithm: astar
python prepare.py --algorithm astar --mode full --notes "algo=astar | hyp=... | change=..."
```

`--algorithm` 可省略；默认读 `portfolio_manifest.yaml`。

---

## Rollback（禁止 git reset --hard 整仓）

仅撤销本轮 commit，恢复 planner 快照：

```powershell
git reset HEAD~1
Copy-Item planners\<本轮algo>.py planner.py -Force
# 若 manifest 也改了，手动改回或 git checkout HEAD -- portfolio_manifest.yaml
```

---

## 指标

字典序：success_rate ↑ → avg_path_length ↓ → plan_time_ms ↓

仅与 **本轮 `--algorithm` 对应** 的 baseline 比较。

---

## Setup（Portfolio 首次）

```powershell
python prepare.py --save-all-baselines --mode full
```

确认 `baselines/` 下四个 json 均 success_rate=1.0。
