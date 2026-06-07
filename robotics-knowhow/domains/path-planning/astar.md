---
id: path_planning/astar
title: A* Algorithm
domain: path_planning
tags: [global, grid-based, heuristic, shortest-path]
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
  frozen_risk: low
  do_not_phase2:
    - change grid structure
    - modify obstacle representation
    - switch to continuous space
---

## 算法概述

A* 算法是 Dijkstra 算法的改进版，通过引入启发式函数来引导搜索方向，显著提高搜索效率。它在计算代价时同时考虑已走距离和预估剩余距离。

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 静态环境全局路径规划 | 动态障碍环境 |
| 已知目标位置 | 无目标或多目标 |
| 需要最优路径且效率要求高 | 启发式难以定义的场景 |

## 核心原理

1. **评估函数**：`f(n) = g(n) + h(n)`
   - `g(n)`：从起点到节点 n 的实际代价
   - `h(n)`：从节点 n 到目标的启发式估计
2. **优先队列**：按 f 值排序扩展节点
3. **启发式选择**：常用曼哈顿距离或欧几里得距离
4. **最优性保证**：当 h(n) 是可采纳的（不高估），保证找到最优解

## 从 PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 源文件 | `a_star.py` 的 `main()` |
| 输入 | `start`, `goal`, `grid` |
| 输出 | `path_x`, `path_y` |
| 配置类 | `AStar` 类 |
| 障碍物格式 | 栅格地图 `grid[0,0]` 为障碍 |
| 终止条件 | 当前节点为目标节点 |

### Config 可调参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `resolution` | 0.1 m | 栅格分辨率 |
| `robot_radius` | 0.5 m | 机器人半径 |
| `heuristic_weight` | 1.0 | 启发式权重（>1加速但可能非最优） |

## 关键 knowhow

> **实验前必做 checklist**

- [ ] 确认启发式函数是可采纳的
- [ ] 调整 heuristic_weight 平衡效率与最优性
- [ ] 检查起点和终点是否在自由空间

### 在 autopath 中的指标

- **success_rate**：能否找到可行路径到达目标
- **avg_path_length**：路径总长度（米），最优时应等于 Dijkstra
- **plan_time_ms**：单次规划耗时（毫秒），通常快于 Dijkstra

## 常见变体

- Weighted A*（非可采纳启发式，更快但可能次优）
- ARA*（Anytime Repairing A*，逐步优化）
- Jump Point Search（网格剪枝优化）

## 参考文献

- Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths.
- PythonRobotics README: PathPlanning/AStar