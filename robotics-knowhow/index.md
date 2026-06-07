# 路径规划选型

本文档帮助快速选择合适的路径规划算法。

---

## Phase 1: DWA（局部避障）

**已完成**，最佳版本见 [domains/path-planning/dwa.md](domains/path-planning/dwa.md)。

| 特性 | DWA |
|------|-----|
| 类型 | 局部规划、反应式 |
| 适用场景 | 动态障碍、实时避障 |
| 最优性 | 局部最优 |
| 地图类型 | 动态障碍场景 |

---

## Phase 2: 全局规划算法

**进行中**，三种算法可选。

### 选型表

| 算法 | 类型 | 适用场景 | 最优性 | 地图类型 | 卡片 |
|------|------|----------|--------|----------|------|
| **Dijkstra** | 网格搜索 | 静态地图、简单障碍 | 保证最优 | Grid | [dijkstra.md](domains/path-planning/dijkstra.md) |
| **A*** | 网格搜索 + 启发式 | 静态地图、需要快速搜索 | w=1 时最优 | Grid | [astar.md](domains/path-planning/astar.md) |
| **RRT*** | 随机采样 | 高维空间、圆形障碍 | 渐近最优 | Sampling | [rrt-star.md](domains/path-planning/rrt-star.md) |

### 快速判断

- **静态地图 + 网格地图 + 需要最优路径** → **Dijkstra**（最简单）
- **静态地图 + 网格地图 + 需要快速搜索** → **A***（有启发式）
- **高维空间 + 圆形障碍 + 连续空间** → **RRT***（采样式）

### 地图类型对应

| 地图类型 | 适用算法 | 目录 |
|----------|----------|------|
| Grid（网格） | Dijkstra、A* | `maps/grid/` |
| Sampling（采样） | RRT* | `maps/sampling/` |

---

## 算法注册表

当前实验算法由 [registry.yaml](registry.yaml) 的 `active_algorithm` 字段控制。

Agent 一次只进化一个算法，切换需人类手动修改。

---

## 相关文档

- [PROJECT_DECISIONS.md](PROJECT_DECISIONS.md) — 产品决策
- [registry.yaml](registry.yaml) — 算法注册表
- [agent/search-policy.md](agent/search-policy.md) — Agent 搜索策略
- [maps/README.md](maps/README.md) — 地图规格说明