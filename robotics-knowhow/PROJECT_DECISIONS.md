# 已锁定产品决策（第一期）

## 1. 算法族：DWA

参考：PythonRobotics/PathPlanning/DynamicWindowApproach

## 2. 主指标（比较顺序）

1. success_rate 越高越好
2. 平局 avg_path_length 越低越好
3. 再平局 plan_time_ms 越低越好

## 3. 地图

- PythonRobotics DWA 自带障碍场景
- 自绘标准图 20 张（autopath/maps/）

## 4. 一晚预算

- quick 约 500 轮/夜

## 5. Agent

- Cursor Agent 读本机 autopath/program.md（第 3 步创建）
- 必读 agent/search-policy.md 与 dwa.md

---

# 已锁定产品决策（第二期）

## 1. 算法族：Dijkstra、A*、RRT*

参考：
- Dijkstra: PythonRobotics/PathPlanning/Dijkstra
- A*: PythonRobotics/PathPlanning/AStar
- RRT*: PythonRobotics/PathPlanning/RRTStar

## 2. 主指标（比较顺序）

与 Phase 1 相同：
1. success_rate 越高越好
2. 平局 avg_path_length 越低越好
3. 再平局 plan_time_ms 越低越好

## 3. 地图分配

| 算法 | eval_mode | 地图类型 | maps_dir |
|------|-----------|----------|----------|
| Dijkstra | grid | 网格地图 | maps/grid/ |
| A* | grid | 网格地图 | maps/grid/ |
| RRT* | sampling | 随机采样地图 | maps/sampling/ |

## 4. Agent 实验规则

- Agent 一次只进化 `registry.yaml` 里的 `active_algorithm`
- 切换算法需人类手动修改 `active_algorithm` 字段
- 每个算法独立评测，不跨算法比较

## 5. 知识库卡片

- DWA: domains/path-planning/dwa.md（Phase 1 金样）
- Dijkstra: domains/path-planning/dijkstra.md
- A*: domains/path-planning/astar.md
- RRT*: domains/path-planning/rrt-star.md

---

# 已锁定产品决策（第三期 — Portfolio）

## 1. 进化模式

- `registry.yaml` → `evolution_mode: portfolio`
- Agent 从 `portfolio_allowed_algorithms` **每轮自选**一个算法进化
- 不做跨算法指标排名（eval_mode / 地图不同）

## 2. 文件分工

| 文件 | 角色 |
|------|------|
| `planner.py` | 当前轮次可执行代码（Agent 改） |
| `planners/*.py` | 只读快照，切换时复制 |
| `portfolio_manifest.yaml` | Agent 声明本轮 algorithm |
| `baselines/<algo>.json` | 分算法 baseline |
| `prepare.py` | 按 `--algorithm` 选地图；**始终 import planner.py** |

## 3. 比较规则

- `better_than_baseline` 只对比 `baselines/<本轮算法>.json`
- 同一 git 历史可含多算法 commit；每轮 keep/rollback 仍按**本轮算法** baseline

## 4. 禁止

- Pipeline 组合（Phase 4 再议）
- 同时在一个 planner.py 里混跑两种 plan 接口

