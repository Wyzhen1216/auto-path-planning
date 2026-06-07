---
id: path-planning/astar
title: A* (Grid-based with Heuristic)
domain: path_planning
tags: [global, grid, heuristic, optimal]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/AStar/a_star.py
  license: MIT
autopath:
  algorithm_family: astar
  editable_in_planner:
    - resolution
    - robot_radius
    - heuristic_weight
    - motion_model
  frozen_risk: low
  do_not_phase2:
    - 切换到 Dijkstra/RRT*/DWA
    - 修改 prepare.py 指标计算
    - 删除碰撞检测
    - 改变地图格式
---

## 简介

A* 算法是 Dijkstra 的改进版本，引入**启发式函数**引导搜索方向，大幅减少搜索空间。

核心思想：`f(n) = g(n) + h(n)`，其中 g(n) 是起点到 n 的实际代价，h(n) 是 n 到终点的估计代价。

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 静态地图、全局规划 | 动态障碍、实时避障 |
| 需要最优路径 + 快速搜索 | 启发式不可靠的场景 |
| 网格地图 | 连续空间（需离散化） |

## 核心步骤

1. **初始化**: 将起点加入 open_set，f = g + h
2. **扩展**: 从 open_set 取出 f 值最小的节点
3. **启发式**: 使用欧氏距离估计 h(n)
4. **更新**: 若邻居节点未被访问或找到更低 f 值，更新
5. **终止**: 当终点被访问时，回溯得到路径

## 与 PythonRobotics 的对应

| 变量 | 含义 |
|------|------|
| `ox, oy` | 障碍物边界点列表 |
| `resolution` | 网格分辨率 [m] |
| `robot_radius` | 机器人半径 [m] |
| `Node` | 网格节点 (x_index, y_index, cost, parent) |
| `calc_heuristic(n1, n2)` | 启发式函数：欧氏距离 |
| `w` | 启发式权重（默认 1.0） |
| `motion` | 8 方向运动模型 |

### 关键参数（可调）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `resolution` | 2.0 m | 网格分辨率 |
| `robot_radius` | 1.0 m | 机器人半径 |
| `heuristic_weight` | 1.0 | 启发式权重 w，w>1 加速但可能非最优 |
| `motion_model` | 8-dir | 8 方向或 4 方向 |

## 扩展 knowhow

> **提示**: 在 autopath 实验时关注这些点

- [ ] 调整 heuristic_weight 观察搜索速度与最优性权衡
  - w = 1.0: 保证最优路径
  - w > 1.0: 加速搜索，可能牺牲最优性
  - w < 1.0: 搜索更保守，路径更优但更慢
- [ ] 对比 A* 与 Dijkstra 的 plan_time_ms 差异
- [ ] 测试不同地图复杂度下的性能差异

### 在 autopath 中的指标定义

- **success_rate**: 成功到达 goal 的测试地图比例
- **avg_path_length**: 路径点之间的欧氏距离累加（米）
- **plan_time_ms**: `planning()` 函数执行时间（毫秒）

## 已知局限

- 启发式函数依赖问题特性
- 高维空间仍需大量计算
- 不适合动态障碍场景

## 与 Dijkstra 的区别

| 特性 | Dijkstra | A* |
|------|----------|-----|
| 搜索方向 | 随机扩展 | 目标导向 |
| 最优性 | 保证 | w=1 时保证 |
| 计算速度 | 较慢 | 通常更快 |

## 参考

- PythonRobotics: https://github.com/AtsushiSakai/PythonRobotics/tree/master/PathPlanning/AStar
- Wikipedia: https://en.wikipedia.org/wiki/A*_search_algorithm