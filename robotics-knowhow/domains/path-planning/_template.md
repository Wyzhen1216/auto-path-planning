---
id: path_planning/algorithm_name
title: Algorithm Name
domain: path_planning
tags: [local/grid/sampling, reactive/optimal/probabilistic]
phase: 2
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/AlgorithmName/algorithm_name.py
  license: MIT
autopath:
  algorithm_family: algorithm_name
  editable_in_planner:
    - param1
    - param2
    - param3
  frozen_risk: low/medium/high
  do_not_phase2:
    - switch to other algorithm
    - modify metrics
---

# Algorithm Name

## 算法概述

简要描述算法的核心思想和适用场景。

## 工作原理

详细解释算法的工作流程，包括：
1. 输入输出
2. 核心步骤
3. 关键技术点

## 参数说明

| 参数 | 默认值 | 说明 | 可调范围 |
|------|--------|------|----------|
| param1 | value | description | [min, max] |
| param2 | value | description | [min, max] |

## 代价函数

如果适用，说明代价函数的构成：

```
final_cost = w1 * cost1 + w2 * cost2 + ...
```

## PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 模块 | `algorithm_name.py` |
| 主函数 | `main()` |
| 状态向量 | `[x, y, ...]` |
| 控制向量 | `[v, w, ...]` |

## autopath 指标

| 指标 | 说明 |
|------|------|
| success_rate | 到达目标且无碰撞的比例 |
| avg_path_length | 成功轨迹的平均长度 |
| plan_time_ms | 单次规划的平均耗时 |

## 注意事项

- 算法的优缺点
- 参数调优建议
- 适用场景限制