---
id: path_planning/{algorithm_id}
title: {Algorithm Name}
domain: path_planning
tags: [{tag1}, {tag2}, ...]
phase: {phase_number}
source:
  repo: https://github.com/AtsushiSakai/PythonRobotics
  path: PathPlanning/{Directory}/{filename}.py
  license: MIT
autopath:
  algorithm_family: {algorithm_id}
  editable_in_planner:
    - param1
    - param2
    - param3
  frozen_risk: {low/medium/high}
  do_not_phase{phase}:
    - action1
    - action2
---

## 算法概述

{算法的核心思想和特点}

## 适用场景 / 不适用场景

| 适用 | 不适用 |
|------|--------|
| 场景1 | 场景2 |

## 核心原理

1. **原理1**：简要说明
2. **原理2**：简要说明

## 从 PythonRobotics 溯源

| 项目 | 说明 |
|------|------|
| 源文件 | `{filename}.py` 的 `main()` |
| 输入 `x` | 状态向量 `[...]` |
| 输出 `u` | 控制向量 `[...]` |
| 配置类 | `Config` 类，包含参数 |
| 障碍物格式 | `Config.ob`，共 N 个 |
| 终止条件 | `{条件描述}` |

### Config 可调参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `param1` | value | 描述 |
| `param2` | value | 描述 |

## 关键 knowhow

> **实验前必做 checklist**

- [ ] 检查项1
- [ ] 检查项2
- [ ] 检查项3

### 在 autopath 中的指标

- **success_rate**：成功率描述
- **avg_path_length**：路径长度描述
- **plan_time_ms**：规划时间描述

## 常见变体

- 变体1
- 变体2

## 参考文献

- Author, Paper Title, Year
- PythonRobotics README