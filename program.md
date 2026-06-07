# autopath — Agent 实验说明（对标 [karpathy/autoresearch](https://github.com/karpathy/autoresearch) 的 `program.md`）

你是路径规划 **自进化研究员**。人类维护本文件与知识库；**你只改 `planner.py`**，通过固定裁判 `prepare.py` 迭代 DWA。

## 三文件分工（与 autoresearch 对齐）

| 文件 | 角色 | 谁改 |
|------|------|------|
| `prepare.py` | 固定地图、仿真、指标、`results.tsv` | **禁止改** |
| `planner.py` | DWA 实现与 `Config` 参数 | **你只改这个** |
| `program.md` | 实验组织与纪律 | 人类改；你只读 |

## 必读上下文

1. 本仓库 `README.md`
2. 知识库（若路径不同，先读环境变量 `ROBOTICS_KNOWHOW` 指向的目录）：
   - `%ROBOTICS_KNOWHOW%/agent/search-policy.md`
   - `%ROBOTICS_KNOWHOW%/domains/path-planning/dwa.md`
   - `%ROBOTICS_KNOWHOW%/PROJECT_DECISIONS.md`

默认知识库路径（本机；可用环境变量 `ROBOTICS_KNOWHOW` 覆盖）：

```text
D:\autopathplanning\robotics-knowhow
```

PowerShell 设置（可选，与默认一致时可省略）：

```powershell
$env:ROBOTICS_KNOWHOW = "D:\autopathplanning\robotics-knowhow"
```

## 优化目标（字典序，不可争论）

1. **success_rate** 越高越好  
2. 平局 → **avg_path_length** 越低越好  
3. 再平局 → **plan_time_ms** 越低越好  

`prepare.py` 中 `is_better()` 已按此实现；`results.tsv` 列 `better_than_baseline` 供你快速判断。

## Setup（每次新会话先做）

```powershell
cd D:\autopathplanning
pip install -e .
python prepare.py --mode full --save-baseline
```

确认：

- `success_rate = 1.0`（当前 5 张地图）
- `avg_path_length` 约 14–15 m 量级（5 图均值）
- `baseline_results.json` 中 `maps_evaluated = 5`

若失败：不要改 `prepare.py`；检查 `planner.py` 是否与 PythonRobotics DWA 一致。

## 实验循环（Karpathy Loop）

每一轮 **必须** 按顺序执行：

1. **假设**：用一句话写本轮想验证的改动（例如增大 `obstacle_cost_gain` 避障更保守）。
2. **只改** `planner.py`（`Config` 默认值或 `calc_control_and_trajectory` 内逻辑，仍在 DWA 族内）。
3. `git add planner.py && git commit -m "exp: <简短描述>"`
4. `python prepare.py --mode full --notes "hyp=<假设一句话> | change=<具体改动>"`
5. 读 `results.tsv` 最后一行与终端输出：
   - `better_than_baseline` 为 `True` → **保留** commit  
   - 否则 → `git reset --hard HEAD~1` 回滚
6. **写入实验日志** `experiment_log.md`（追加一段，见下方模板）；同时在 Chat 回复里贴同一段摘要。

### 实验记录（每轮必须做）

人类可读主日志：`D:\autopathplanning\experiment_log.md`（本地文件，不 commit）。  
机器可读指标：`results.tsv`（`prepare.py` 自动追加；`notes` 列来自 `--notes`）。

**第 6 步模板**（将 `<...>` 替换为本轮真实值后追加到 `experiment_log.md`）：

```markdown
## Round <N> | <git短hash> | <keep|rollback>
- **假设**: <一句话>
- **改动**: <planner.py 中改了什么>
- **指标**: success_rate=<>, avg_path_length=<>, plan_time_ms=<>, better_than_baseline=<>
- **决策**: <keep 保留 commit / rollback 已 reset>
```

PowerShell 追加示例（决策完成后再执行）：

```powershell
$commit = git rev-parse --short HEAD
Add-Content -Path D:\autopathplanning\experiment_log.md -Encoding utf8 @"

## Round 1 | $commit | keep
- **假设**: 增大 obstacle_cost_gain 使绕障更保守
- **改动**: obstacle_cost_gain 1.0 -> 1.5
- **指标**: success_rate=1.0, avg_path_length=14.21, plan_time_ms=33.1, better_than_baseline=True
- **决策**: keep

"@
```

Chat 回复可简写为同一段的四行 bullet，便于在 Cursor 里滚动浏览 overnight 进度。

### 禁止

- 修改 `prepare.py`、`program.md`、`maps/`、`pyproject.toml`
- 更换算法族（A* / RRT / PRM 等）
- 删除或绕过碰撞检测
- 新增 pip 依赖
- `git add` / 提交 `results.tsv`、`experiment_log.md`（由 prepare / Agent 本地写入，仅人类可读盘）

### 允许改动（Phase 1）

见知识库 `dwa.md` frontmatter `editable_in_planner`，主要包括：

`to_goal_cost_gain`, `speed_cost_gain`, `obstacle_cost_gain`, `predict_time`,
`v_resolution`, `yaw_rate_resolution`, `max_speed`, `max_yaw_rate`,
`robot_radius`, `robot_stuck_flag_cons`

建议优先搜：`obstacle_cost_gain`, `to_goal_cost_gain`, `predict_time`（见 knowhow 敏感度）。

## 预算

- **quick**（`--mode quick`）：3 张图，约 **30s/轮**；仅作快速冒烟，**不与 baseline 比较**
- **full**（`--mode full`）：5 张图，约 **45s/轮**；**baseline 与过夜循环均用此模式**，目标一晚约 **80–150 轮**

## 启动提示（复制给 Agent）

```text
阅读 D:\autopathplanning\program.md，完成 Setup，然后做第 1 轮实验：
只改 planner.py，commit 后运行 python prepare.py --mode full --notes "hyp=... | change=..."，根据 better_than_baseline 决定 keep 或 git reset --hard HEAD~1，并按 program.md 模板追加 experiment_log.md。
```

## 成功标准（Phase 1 demo）

- 一晚 full 循环中，出现至少一次 `better_than_baseline=True` 且人类可解释的改动
- `success_rate` 不得长期低于 baseline；为降 path_length 牺牲成功率视为失败

---

# Phase 2 — 多算法接线（已完成）

`prepare.py --algorithm dwa|dijkstra|astar|rrt_star`；地图见 `maps/dwa|grid|sampling/`。  
Phase 3 已 supersede「人类锁 active_algorithm」模式。

---

# Phase 3 — Portfolio 自进化（当前）

Agent **每轮从 knowhow 白名单自选一个算法**，只与该算法的 baseline 比较。

## 必读

1. `robotics-knowhow/registry.yaml`（`evolution_mode: portfolio`）
2. `robotics-knowhow/agent/search-policy.md`
3. `robotics-knowhow/index.md` 选型表
4. 本轮算法对应 `domains/path-planning/<algo>.md`

## 三文件 + manifest

| 文件 | 谁改 |
|------|------|
| `prepare.py` | **禁止** |
| `planner.py` | **Agent**（当前轮可执行代码） |
| `portfolio_manifest.yaml` | **Agent**（声明本轮 `algorithm`） |
| `planners/*.py` | **禁止**（快照；切换时复制到 planner.py） |
| `program.md` | 人类 |

**评测始终 import `planner.py`**。切换算法必须：

```powershell
Copy-Item planners\<algo>.py planner.py -Force
# 编辑 portfolio_manifest.yaml → algorithm: <algo>
```

## Setup

```powershell
cd D:\autopathplanning
pip install -e .
python prepare.py --save-all-baselines --mode full
```

确认 `baselines/dwa.json`、`dijkstra.json`、`astar.json`、`rrt_star.json` 均 `success_rate=1.0`。

切换 planner 后若只跑单算法，可：

```powershell
python prepare.py --algorithm astar --mode full --save-baseline
```

## 实验循环（Portfolio Karpathy Loop）

1. **选型**：读 index + 卡片，决定本轮算法（可切换）
2. **若切换算法**：复制 `planners/<algo>.py` → `planner.py`，更新 `portfolio_manifest.yaml`
3. **假设**：一句话（含为何选此算法）
4. **只改** `planner.py`（参数或算法内逻辑，仍在该算法族内）
5. `git add planner.py portfolio_manifest.yaml && git commit -m "exp(<algo>): <描述>"`
6. `python prepare.py --mode full --notes "algo=<algo> | hyp=... | change=..."`
   - 或显式 `--algorithm <algo>`
7. 读 `results.tsv`：`better_than_baseline` 对比 **`baselines/<algo>.json`**
   - `True` → **keep**
   - `False` → rollback（见下）
8. 追加 `experiment_log.md`

### 实验记录模板（Phase 3）

```markdown
## P3-Round <N> | <hash> | <keep|rollback> | <algo>
- **选型**: <为何选此算法 / 是否从上一轮切换>
- **假设**: <一句话>
- **改动**: <planner.py 具体改动>
- **指标**: success_rate=<>, avg_path_length=<>, plan_time_ms=<>, better_than_baseline=<>
- **决策**: keep / rollback
```

### Rollback（禁止 `git reset --hard` 整仓）

```powershell
git reset HEAD~1
Copy-Item planners\<algo>.py planner.py -Force
git checkout HEAD -- portfolio_manifest.yaml   # 若 manifest 也提交过
```

### 禁止

- 改 `prepare.py`、`program.md`、`maps/`、`planners/`
- 一个 planner.py 里同时混两种 plan 接口
- 跨算法比较 path_length 决定是否 keep
- 删碰撞检测、加 pip 依赖
- 提交 `results.tsv`、`baselines/`、`experiment_log.md`

### 允许

- 每轮换算法（Portfolio 核心）
- 连续多轮优化同一算法
- 改 `portfolio_manifest.yaml` 的 `algorithm` 与 `rationale`

## 预算

- **quick**：冒烟，不与 baseline 比（切换算法后建议先 quick）
- **full**：过夜循环与 baseline 对比

## 启动提示（Phase 3 Agent）

```text
阅读 D:\autopathplanning\program.md Phase 3 与 robotics-knowhow/agent/search-policy.md。
若 baselines/ 不全，先 python prepare.py --save-all-baselines --mode full。
然后 Portfolio 循环：每轮自选算法，更新 portfolio_manifest.yaml，复制快照到 planner.py，
只改 planner.py，commit 后 python prepare.py --mode full --notes "algo=... | hyp=... | change=..."，
按 baselines/<algo>.json 决定 keep 或 git reset HEAD~1 + 恢复 planner，写 experiment_log.md。
持续循环直到我说停。
```

## 成功标准（Phase 3）

- 至少两个不同算法出现 `better_than_baseline=True` 且可解释
- 任一算法不得长期 success_rate 低于其 baseline

