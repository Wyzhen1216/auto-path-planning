---
id: path_planning/dijkstra
title: Dijkstra's Algorithm
domain: path_planning
tags: [grid, optimal, shortest-path]
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
    - tie_breaker
  frozen_risk: low
  do_not_phase2:
    - switch to sampling-based algorithms
    - modify grid structure
---

# Dijkstra's Algorithm

## 算法概述

Dijkstra 算法是一种无启发式的最短路径搜索算法。它从起点开始，逐步向外扩展，直到找到目标点。保证找到最短路径，但在大型地图上效率较低。

## 工作原理

### 核心流程

1. **初始化**：创建距离矩阵，起点距离设为 0，其他节点设为无穷大
2. **优先级队列**：使用优先队列存储待访问节点
3. **松弛操作**：对每个节点的邻居，更新最短路径
4. **终止条件**：目标节点出队或队列为空

### 伪代码

```python
def dijkstra(start, goal, grid):
    dist = {node: infinity for node in grid}
    dist[start] = 0
    pq = PriorityQueue([(0, start)])
    
    while pq not empty:
        current_dist, current = pq.pop()
        
        if current == goal:
            return reconstruct_path(current)
        
        for neighbor in get_neighbors(current):
            new_dist = current_dist + distance(current, neighbor)
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                pq.push((new_dist, neighbor))
```

## 参数说明

| 参数 | 默认值 | 说明 | 可调范围 |
|------|--------|------|----------|
| `resolution` | 0.5 | 栅格分辨率（米） | [0.1, 1.0] |
| `robot_radius` | 0.5 | 机器人半径（米） | [0.3, 1.0] |
| `tie_breaker` | 0.0 | 平局打破系数 | [-0.1, 0.1] |

## PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 模块 | `dijkstra.py` |
| 主函数 | `main()` |
| 输入 | 栅格地图、起点、终点 |
| 输出 | 路径点列表 |
| 数据结构 | 优先队列 + 距离字典 |

## autopath 指标

| 指标 | 说明 |
|------|------|
| success_rate | 是否找到路径（0 或 1） |
| avg_path_length | 路径长度（米） |
| plan_time_ms | 规划耗时（毫秒） |

## 特点

| 特性 | 说明 |
|------|------|
| **最优性** | 保证找到最短路径 |
| **时间复杂度** | O((V+E)logV)，V=节点数，E=边数 |
| **空间复杂度** | O(V) |
| **适用场景** | 小型到中型栅格地图 |

## 注意事项

- 无启发式信息，在大型地图上效率较低
- 适合静态环境下的全局路径规划
- 不适合动态障碍物场景