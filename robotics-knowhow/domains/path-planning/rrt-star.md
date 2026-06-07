---
id: path-planning/rrt-star
title: RRT* (Optimal Sampling-based Path Planning)
domain: path_planning
tags: [global, sampling, probabilistic, asymptotically_optimal]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/RRTStar/rrt_star.py
  license: MIT
autopath:
  algorithm_family: rrt_star
  editable_in_planner:
    - expand_dis
    - path_resolution
    - goal_sample_rate
    - max_iter
    - connect_circle_dist
    - robot_radius
    - random_seed
  frozen_risk: medium
  do_not_phase2:
    - 切换到 Dijkstra/A*/DWA
    - 修改 prepare.py 指标计算
    - 删除碰撞检测
    - 改变地图格式（必须用 sampling）
---

## 简介

RRT* (Rapidly-exploring Random Tree Star) 是一种**基于随机采样的全局路径规划算法**，在 RRT 基础上引入重连机制，随着迭代次数增加路径逐渐趋于最优。

核心思想：
1. 随机采样空间中的点
2. 向采样点扩展树
3. 在扩展过程中重连附近节点，优化路径代价

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 高维空间、复杂障碍 | 需要严格最优路径 |
| 非网格地图、连续空间 | 时间受限场景 |
| 圆形障碍物 | 狭窄通道（采样困难） |

## 核心步骤

1. **随机采样**: 在 world_bounds 内随机生成一个点 rnd
2. **最近邻**: 找到树中距离 rnd 最近的节点 nearest
3. **扩展**: 从 nearest 向 rnd 扩展 expand_dis 距离，生成新节点 new_node
4. **重连**: 在 connect_circle_dist 范围内找近邻节点，尝试重连以降低代价
5. **终止**: 达到 max_iter 或找到 goal 后返回路径

## 与 PythonRobotics 的对应

| 变量 | 含义 |
|------|------|
| `start` | 起点 [x, y] |
| `goal` | 终点 [x, y] |
| `obstacle_list` | 圆形障碍物 [[x, y, radius], ...] |
| `rand_area` | 随机采样区域 [min, max] |
| `expand_dis` | 每次扩展距离 [m] |
| `path_resolution` | 路径点分辨率 [m] |
| `goal_sample_rate` | 直接采样 goal 的概率 [%] |
| `max_iter` | 最大迭代次数 |
| `connect_circle_dist` | 重连搜索半径 [m] |
| `robot_radius` | 机器人半径 [m] |

### 关键参数（可调）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `expand_dis` | 30.0 m | 每次扩展距离，影响树生长速度 |
| `path_resolution` | 1.0 m | 路径点密度 |
| `goal_sample_rate` | 20 | 直接采样 goal 的概率，加速收敛 |
| `max_iter` | 300 | 最大迭代次数，越大路径越优 |
| `connect_circle_dist` | 50.0 m | 重连搜索半径，影响优化程度 |
| `robot_radius` | 0.0 m | 机器人半径 |
| `random_seed` | None | 固定随机种子可复现结果 |

## 扩展 knowhow

> **提示**: 在 autopath 实验时关注这些点

- [ ] 调整 max_iter 观察路径质量与计算时间关系
- [ ] 调整 connect_circle_dist 影响重连优化程度
- [ ] 固定 random_seed 确保实验可复现
- [ ] 调整 goal_sample_rate 加速收敛到 goal

### 在 autopath 中的指标定义

- **success_rate**: 成功到达 goal 的测试地图比例
- **avg_path_length**: 路径点之间的欧氏距离累加（米）
- **plan_time_ms**: `planning()` 函数执行时间（毫秒）

## 已知局限

- 随机性导致结果不稳定（需固定种子）
- 狭窄通道难以采样到
- 需要足够迭代次数才能趋于最优

## 与 Dijkstra/A* 的区别

| 特性 | Dijkstra/A* | RRT* |
|------|-------------|------|
| 搜索方式 | 网格遍历 | 随机采样 |
| 最优性 | 保证最优 | 渐近最优 |
| 高维空间 | 计算量大 | 效率较高 |
| 地图类型 | 网格地图 | 连续空间 |

## 参考

- PythonRobotics: https://github.com/AtsushiSakai/PythonRobotics/tree/master/PathPlanning/RRTStar
- Paper: "Sampling-based Algorithms for Optimal Motion Planning" (Karaman & Frazzoli, 2011)