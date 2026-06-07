---
id: path_planning/dijkstra
title: Dijkstra's Algorithm
domain: path_planning
tags: [global, grid-based, shortest-path, deterministic]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/Dijkstra/dijkstra.py
  license: MIT
autopath:
  algorithm_family: dijkstra
  editable_in_planner:
    - resolution
    - robot_radius
    - weight
  frozen_risk: low
  do_not_phase2:
    - change grid structure
    - modify obstacle representation
    - switch to continuous space
---

## 算法概述

Dijkstra 算法是一种贪心算法，用于在加权图中寻找从起点到所有其他节点的最短路径。它通过维护一个优先队列，每次选择距离起点最近的未访问节点进行扩展。

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 静态环境全局路径规划 | 动态障碍环境 |
| 非负权边的图 | 含负权边的图 |
| 需要最优路径 | 实时性要求极高 |

## 核心原理

1. **初始化**：设置起点距离为0，其他所有节点距离为无穷大
2. **优先队列**：使用优先队列存储待扩展节点，按距离排序
3. **松弛操作**：对每个邻居节点，尝试更新最短距离
4. **终止条件**：到达目标节点或队列为空

## 从 PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 源文件 | `dijkstra.py` 的 `main()` |
| 输入 | `start`, `goal`, `grid` |
| 输出 | `path_x`, `path_y` |
| 配置类 | `Dijkstra` 类 |
| 障碍物格式 | 栅格地图 `grid[0,0]` 为障碍 |
| 终止条件 | 当前节点为目标节点 |

### Config 可调参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `resolution` | 0.1 m | 栅格分辨率 |
| `robot_radius` | 0.5 m | 机器人半径 |
| `weight` | 1.0 | 路径代价权重 |

## 关键 knowhow

> **实验前必做 checklist**

- [ ] 确认栅格分辨率适合机器人尺寸
- [ ] 检查起点和终点是否在自由空间
- [ ] 确保障碍物已正确膨胀

### 在 autopath 中的指标

- **success_rate**：能否找到可行路径到达目标
- **avg_path_length**：路径总长度（米）
- **plan_time_ms**：单次规划耗时（毫秒）

## 常见变体

- Dijkstra with Fibonacci heap（更优时间复杂度）
- 双向 Dijkstra（从起点和终点同时搜索）

## 参考文献

- Dijkstra, E. W. (1959). A note on two problems in connexion with graphs.
- PythonRobotics README: PathPlanning/Dijkstra