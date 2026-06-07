---
id: path_planning/rrt_star
title: RRT* (Rapidly-exploring Random Tree Star)
domain: path_planning
tags: [global, sampling-based, probabilistic, asymptotically-optimal]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/RRTStar/rrt_star.py
  license: MIT
autopath:
  algorithm_family: rrt_star
  editable_in_planner:
    - robot_radius
    - max_iter
    - connect_circle_dist
    - goal_sample_rate
    - random_seed
  frozen_risk: medium
  do_not_phase2:
    - change obstacle representation
    - switch to grid-based
    - modify tree structure
---

## 算法概述

RRT* 是 RRT（快速扩展随机树）的改进版，通过重新布线机制实现渐近最优性。它在扩展树的同时，不断优化已有路径，最终收敛到最优路径。

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 高维空间路径规划 | 需要严格最优解 |
| 复杂障碍物环境 | 实时性要求极高 |
| 非完整约束机器人 | 小空间精细规划 |

## 核心原理

1. **随机采样**：在可行空间随机采样点
2. **最近节点**：找到树中距离采样点最近的节点
3. **局部规划**：从最近节点向采样点延伸一段距离
4. **重新布线**：检查附近节点，优化路径代价
5. **渐近最优**：随着迭代增加，路径逐渐收敛到最优

## 从 PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 源文件 | `rrt_star.py` 的 `main()` |
| 输入 | `start`, `goal`, `obstacle_list` |
| 输出 | `path_x`, `path_y` |
| 配置类 | `RRTStar` 类 |
| 障碍物格式 | 圆形障碍物列表 |
| 终止条件 | 达到最大迭代或找到目标 |

### Config 可调参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `robot_radius` | 0.5 m | 机器人半径 |
| `max_iter` | 1000 | 最大迭代次数 |
| `connect_circle_dist` | 50.0 | 重新布线搜索半径 |
| `goal_sample_rate` | 5 | 目标点采样概率（%） |
| `random_seed` | 0 | 随机种子（0=随机） |

## 关键 knowhow

> **实验前必做 checklist**

- [ ] 设置合适的随机种子保证可重复性
- [ ] 根据环境大小调整 connect_circle_dist
- [ ] 调整 goal_sample_rate 平衡探索与目标导向

### 在 autopath 中的指标

- **success_rate**：能否找到可行路径到达目标
- **avg_path_length**：路径总长度（米），随迭代增加优化
- **plan_time_ms**：单次规划耗时（毫秒），与迭代次数相关

## 常见变体

- RRT-Connect（双向扩展）
- RRT#（更快收敛）
- Informed RRT*（目标区域采样加速）

## 参考文献

- Karaman, S., & Frazzoli, E. (2011). Sampling-based algorithms for optimal motion planning.
- PythonRobotics README: PathPlanning/RRTStar