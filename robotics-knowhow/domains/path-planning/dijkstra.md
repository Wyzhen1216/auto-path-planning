---
id: path-planning/dijkstra
title: Dijkstra (Grid-based Shortest Path)
domain: path_planning
tags: [global, grid, deterministic, optimal]
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
    - motion_model
  frozen_risk: low
  do_not_phase2:
    - 切换到 A*/RRT*/DWA
    - 修改 prepare.py 指标计算
    - 删除碰撞检测
    - 改变地图格式
---

## 简介

Dijkstra 算法是一种经典的**全局路径规划算法**，基于网格搜索，保证找到最短路径。

核心思想：从起点开始，逐步扩展到所有可达节点，按代价从小到大依次访问，直到到达终点。

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 静态地图、全局规划 | 动态障碍、实时避障 |
| 需要最优路径 | 高维空间（计算量大） |
| 网格地图 | 连续空间（需离散化） |

## 核心步骤

1. **初始化**: 将起点加入 open_set，cost=0
2. **扩展**: 从 open_set 取出 cost 最小的节点，扩展其邻居
3. **更新**: 若邻居节点未被访问或找到更短路径，更新其 cost
4. **终止**: 当终点被访问时，回溯得到路径

## 与 PythonRobotics 的对应

| 变量 | 含义 |
|------|------|
| `ox, oy` | 障碍物边界点列表 |
| `resolution` | 网格分辨率 [m] |
| `robot_radius` | 机器人半径 [m] |
| `Node` | 网格节点 (x_index, y_index, cost, parent) |
| `open_set` | 待访问节点字典 |
| `closed_set` | 已访问节点字典 |
| `motion` | 8 方向运动模型 |

### 关键参数（可调）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `resolution` | 2.0 m | 网格分辨率，越小精度越高但计算量增大 |
| `robot_radius` | 1.0 m | 机器人半径，用于障碍物膨胀 |
| `motion_model` | 8-dir | 8 方向（含对角线）或 4 方向（仅水平/垂直） |

## 扩展 knowhow

> **提示**: 在 autopath 实验时关注这些点

- [ ] 调整 resolution 观察路径精度与计算时间权衡
- [ ] 对比 4-dir 与 8-dir motion model 的路径长度差异
- [ ] 测试不同 robot_radius 对狭窄通道的影响

### 在 autopath 中的指标定义

- **success_rate**: 成功到达 goal 的测试地图比例
- **avg_path_length**: 路径点之间的欧氏距离累加（米）
- **plan_time_ms**: `planning()` 函数执行时间（毫秒）

## 已知局限

- 计算复杂度 O(V²)，大地图效率低
- 无启发式引导，搜索方向随机
- 不适合动态障碍场景

## 参考

- PythonRobotics: https://github.com/AtsushiSakai/PythonRobotics/tree/master/PathPlanning/Dijkstra
- Wikipedia: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm