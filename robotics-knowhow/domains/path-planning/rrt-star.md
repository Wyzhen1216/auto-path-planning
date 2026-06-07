---
id: path_planning/rrt-star
title: RRT* Algorithm
domain: path_planning
tags: [sampling, probabilistic, asymptotically-optimal]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/RRTStar/rrt_star.py
  license: MIT
autopath:
  algorithm_family: rrt_star
  editable_in_planner:
    - max_iter
    - connect_circle_dist
    - goal_sample_rate
    - random_seed
    - robot_radius
    - search_until_max_iter
  frozen_risk: medium
  do_not_phase2:
    - switch to grid-based algorithms
    - modify sampling strategy
---

# RRT* Algorithm

## 算法概述

RRT*（Rapidly-exploring Random Trees Star）是一种基于采样的概率路径规划算法。它在 RRT 的基础上增加了重布线（rewire）操作，能够渐进地找到最优路径。适用于高维空间和复杂环境。

## 工作原理

### 核心流程

1. **初始化**：创建根节点（起点），初始化随机树
2. **采样**：随机采样一个点 `x_rand`
3. **最近节点**：找到树中距离 `x_rand` 最近的节点 `x_nearest`
4. **扩展**：从 `x_nearest` 向 `x_rand` 方向扩展，生成新节点 `x_new`
5. **重布线**：在 `x_new` 附近一定范围内，重新连接节点以优化路径
6. **终止条件**：达到最大迭代次数或找到目标

### 重布线操作

```python
def rewire(x_new, tree, radius):
    for node in tree.nodes:
        dist = distance(x_new, node)
        if dist < radius:
            # 检查通过 x_new 是否能获得更短路径
            new_cost = x_new.cost + dist
            if new_cost < node.cost:
                node.parent = x_new
                node.cost = new_cost
```

## 参数说明

| 参数 | 默认值 | 说明 | 可调范围 |
|------|--------|------|----------|
| `max_iter` | 5000 | 最大迭代次数 | [1000, 20000] |
| `connect_circle_dist` | 50.0 | 重布线搜索半径（米） | [20, 100] |
| `goal_sample_rate` | 5.0 | 目标采样概率（%） | [1, 20] |
| `random_seed` | 0 | 随机种子（0=随机） | [0, 9999] |
| `robot_radius` | 0.3 | 机器人半径（米） | [0.2, 0.8] |
| `search_until_max_iter` | true | 是否搜索到最大迭代次数 | true/false |

## PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 模块 | `rrt_star.py` |
| 主函数 | `main()` |
| 输入 | 起点、终点、障碍物、世界边界 |
| 输出 | 路径点列表 |
| 数据结构 | 树形结构 + 距离查询 |

## autopath 指标

| 指标 | 说明 |
|------|------|
| success_rate | 是否找到路径（0 或 1） |
| avg_path_length | 路径长度（米） |
| plan_time_ms | 规划耗时（毫秒） |

## 特点

| 特性 | 说明 |
|------|------|
| **渐进最优性** | 随着迭代次数增加，路径逐渐收敛到最优 |
| **时间复杂度** | O(n log n)，n=节点数 |
| **空间复杂度** | O(n) |
| **适用场景** | 高维空间、复杂障碍物环境 |

## 参数敏感性

| 参数 | 敏感性 | 影响 |
|------|--------|------|
| `max_iter` | 高 | 影响路径质量和计算时间 |
| `connect_circle_dist` | 中 | 影响重布线效果 |
| `goal_sample_rate` | 中 | 影响收敛速度 |
| `random_seed` | 高 | 影响结果的可重复性 |

## 注意事项

- 结果具有随机性，建议多次运行取最优
- 设置固定 `random_seed` 可保证结果可重复
- 增加 `max_iter` 可提高路径质量，但增加计算时间
- `connect_circle_dist` 过大会增加计算开销

## RRT vs RRT*

| 特性 | RRT | RRT* |
|------|-----|------|
| 最优性 | 不保证 | 渐进最优 |
| 重布线 | 无 | 有 |
| 复杂度 | 低 | 较高 |
| 路径质量 | 一般 | 较好 |