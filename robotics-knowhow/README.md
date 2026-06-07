# Robotics Knowhow 知识库

面向路径规划自进化（autopath）的算法 knowhow 文档库，素材以 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 为骨架。

---

## 当前阶段

| 步骤 | 状态 |
|------|------|
| 0 定范围 | 完成 — DWA，见 PROJECT_DECISIONS.md |
| 1 知识库骨架 | 完成 |
| 2 跑通 DWA demo | 完成 — Phase 1 最佳版本 e77f895 |
| 3 autopath/ | 完成 — Phase 1 实验结束 |
| **Step 1 knowhow Phase 2** | **进行中** |
| Step 2 实现 Dijkstra/A*/RRT* | 待做 |
| Step 3 Phase 2 实验 | 待做 |

---

## 目录结构

```
robotics-knowhow/
├── PROJECT_DECISIONS.md   # 产品决策（Phase 1 + Phase 2）
├── registry.yaml          # 算法注册表 ★ 新增
├── index.md               # 选型树
├── README.md              # 本文件
├── agent/
│   └── search-policy.md   # Agent 搜索策略
├── domains/
│   └── path-planning/
│       ├── _template.md   # 卡片模板 ★ 新增
│       ├── dwa.md         # DWA 金样（Phase 1）
│       ├── dijkstra.md    # Dijkstra 卡片 ★ 新增
│       ├── astar.md       # A* 卡片 ★ 新增
│       └ rrt-star.md      # RRT* 卡片 ★ 新增
├── maps/
│   ├── README.md          # 地图规格说明 ★ 新增
│   ├── grid/              # Grid 地图 ★ 新增
│   └ sampling/            # Sampling 地图 ★ 新增
├── sources/
│   └── pythonrobotics.md  # PythonRobotics 溯源
└── experiments/
    └── dwa_demo/
        └ demo.py
```

---

## Phase 2 新增内容

### 算法注册表

[registry.yaml](registry.yaml) 定义了 4 个算法的配置：
- `active_algorithm`：当前实验算法
- `eval_mode`：评测模式（grid / sampling / dwa）
- `maps_dir`：对应地图目录
- `knowhow`：知识卡片路径

### 算法卡片

| 算法 | 卡片 | 可调参数 |
|------|------|----------|
| DWA | [dwa.md](domains/path-planning/dwa.md) | gain 权重、predict_time、速度界等 |
| Dijkstra | [dijkstra.md](domains/path-planning/dijkstra.md) | resolution、robot_radius、motion_model |
| A* | [astar.md](domains/path-planning/astar.md) | resolution、heuristic_weight、motion_model |
| RRT* | [rrt-star.md](domains/path-planning/rrt-star.md) | expand_dis、max_iter、connect_circle_dist 等 |

### 地图规格

见 [maps/README.md](maps/README.md)，包含 Grid 和 Sampling 两种 JSON 格式。

---

## 与 autopath

autopath 引用本库的：
- `agent/search-policy.md` — Agent 边界
- `registry.yaml` — 当前算法配置
- `domains/path-planning/*.md` — 算法卡片