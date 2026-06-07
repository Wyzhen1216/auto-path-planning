---
id: path_planning/astar
title: A* Algorithm
domain: path_planning
tags: [grid, optimal, heuristic, shortest-path]
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
    - tie_breaker
  frozen_risk: low
  do_not_phase2:
    - switch to sampling-based algorithms
    - modify grid structure
---

# A* Algorithm

## 算法概述

A* 算法是一种带启发式的最短路径搜索算法。它在 Dijkstra 算法的基础上引入了启发式函数，能够更高效地找到最短路径。是目前最常用的路径规划算法之一。

## 工作原理

### 核心流程

1. **初始化**：创建 g、h、f 三个代价矩阵
2. **优先级队列**：使用优先队列存储待访问节点，按 f 值排序
3. **松弛操作**：对每个节点的邻居，更新 g、h、f 值
4. **终止条件**：目标节点出队或队列为空

### 代价函数

```
f(n) = g(n) + h(n)
```

| 分量 | 含义 | 计算方式 |
|------|------|----------|
| `g(n)` | 从起点到节点 n 的实际代价 | 累计路径长度 |
| `h(n)` | 从节点 n 到目标的估计代价 | 启发式函数 |
| `f(n)` | 总代价估计 | g(n) + h(n) |

### 启发式函数

```python
# Manhattan 距离（适合网格移动）
h = |x1 - x2| + |y1 - y2|

# Euclidean 距离（适合自由移动）
h = sqrt((x1-x2)^2 + (y1-y2)^2)

# Chebyshev 距离（适合八方向移动）
h = max(|x1-x2|, |y1-y2|)
```

## 参数说明

| 参数 | 默认值 | 说明 | 可调范围 |
|------|--------|------|----------|
| `resolution` | 0.5 | 栅格分辨率（米） | [0.1, 1.0] |
| `robot_radius` | 0.5 | 机器人半径（米） | [0.3, 1.0] |
| `heuristic_weight` | 1.0 | 启发式权重 | [0.5, 2.0] |
| `tie_breaker` | 0.0 | 平局打破系数 | [-0.1, 0.1] |

## PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 模块 | `a_star.py` |
| 主函数 | `main()` |
| 输入 | 栅格地图、起点、终点 |
| 输出 | 路径点列表 |
| 启发式 | Euclidean 距离 |
| 数据结构 | 优先队列 + 代价字典 |

## autopath 指标

| 指标 | 说明 |
|------|------|
| success_rate | 是否找到路径（0 或 1） |
| avg_path_length | 路径长度（米） |
| plan_time_ms | 规划耗时（毫秒） |

## 特点

| 特性 | 说明 |
|------|------|
| **最优性** | 当 h(n) 是可采纳启发式时保证最优 |
| **时间复杂度** | 取决于启发式质量，通常远优于 Dijkstra |
| **空间复杂度** | O(V) |
| **适用场景** | 中小型栅格地图，需要快速规划 |

## 与 Dijkstra 的对比

| 特性 | Dijkstra | A* |
|------|----------|----|
| 启发式 | 无 | 有 |
| 最优性 | 保证 | 保证（可采纳启发式） |
| 效率 | 低 | 高 |
| 内存 | 适中 | 可能更高 |

## 注意事项

- 启发式函数的选择至关重要
- `heuristic_weight > 1` 可加速但不保证最优
- 适合静态环境下的全局路径规划