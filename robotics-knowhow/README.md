# Robotics Knowhow 知识库

面向路径规划自进化（autopath）的算法 knowhow 文档库，素材以 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics) 为骨架。

## 当前阶段

| 步骤 | 状态 |
|------|------|
| 0 定范围 | 完成 — DWA，见 PROJECT_DECISIONS.md |
| 1 知识库骨架 | 完成 |
| 1b Phase 2 决策 | **进行中** — 扩展 Dijkstra、A*、RRT* |
| 2 跑通 DWA demo | 待做 |
| 3 autopath/ | 待做 |

## 目录

```
robotics-knowhow/
├── PROJECT_DECISIONS.md    # 锁定决策（Phase 1 + Phase 2）
├── index.md               # 选型树
├── registry.yaml          # 算法注册表
├── README.md              # 本文件
├── sources/
│   └── pythonrobotics.md  # PythonRobotics 溯源
├── maps/
│   └── README.md          # 地图格式规范
├── domains/
│   └── path-planning/     # 算法卡片目录
│       ├── _template.md   # 卡片模板
│       ├── dwa.md         # DWA 卡片
│       ├── dijkstra.md    # Dijkstra 卡片
│       ├── astar.md       # A* 卡片
│       └── rrt-star.md    # RRT* 卡片
└── agent/
    └── search-policy.md   # Agent 搜索策略
```

## 算法卡片列表

| 算法 | 阶段 | 类型 | 卡片路径 |
|------|------|------|----------|
| DWA | Phase 1 | 局部 | domains/path-planning/dwa.md |
| Dijkstra | Phase 2 | 全局/Grid | domains/path-planning/dijkstra.md |
| A* | Phase 2 | 全局/Grid | domains/path-planning/astar.md |
| RRT* | Phase 2 | 全局/Sampling | domains/path-planning/rrt-star.md |

## 与 autopath

autopath 将引用本库的：
- `registry.yaml` — 确定当前激活算法
- `agent/search-policy.md` — Agent 搜索边界
- `domains/path-planning/*.md` — 算法具体参数与约束