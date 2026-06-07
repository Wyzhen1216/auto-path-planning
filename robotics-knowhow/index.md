# 路径规划选型

## Phase 1：DWA（已完成）

局部避障专用算法。

- 适用：动态障碍、在线重规划
- 详见：domains/path-planning/dwa.md

---

## Phase 2：全局路径规划（进行中）

### 算法选型表

| 算法 | 类型 | 适用场景 | 最优性 | 特点 |
|------|------|----------|--------|------|
| **Dijkstra** | Grid | 静态环境 | 最优 | 经典最短路径，无启发式 |
| **A*** | Grid | 静态环境 | 最优 | 带启发式，比Dijkstra快 |
| **RRT*** | Sampling | 高维/复杂环境 | 渐近最优 | 概率采样，适用于非完整约束 |

### 快速判断

| 场景 | 推荐算法 |
|------|----------|
| 局部避障、动态障碍、在线重规划 | **DWA** |
| 静态地图、需要严格最优路径 | **A*** |
| 高维空间、复杂约束 | **RRT*** |

### 算法卡片目录

- [DWA](domains/path-planning/dwa.md)
- [Dijkstra](domains/path-planning/dijkstra.md)
- [A*](domains/path-planning/astar.md)
- [RRT*](domains/path-planning/rrt-star.md)