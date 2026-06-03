# autopath

对标 [karpathy/autoresearch](https://github.com/karpathy/autoresearch) 的 **机器人路径规划自进化 demo**（Phase 1：DWA）。

知识库（人类文档）：`robotics-knowhow` — 算法 knowhow、指标定义、Agent 边界。

## 三文件结构

```text
prepare.py   — 固定裁判：地图、仿真、指标、results.tsv（勿改）
planner.py   — DWA 规划器（Agent 唯一可改）
program.md   — Agent 实验说明（人类维护）
maps/        — 评测场景 JSON
```

## Quick start

```powershell
cd D:\autopathplanning
pip install -e .
python prepare.py --mode full --save-baseline
```

期望：`success_rate=1.0`，`full` 模式 5 张图均可到达目标；baseline 以 5 图均值为准。

## 运行 Agent

在 `D:\autopathplanning` 打开 Cursor Agent，提示：

```text
阅读 program.md，完成 Setup，然后开始第 1 轮实验。
```

知识库默认位于仓库内 `robotics-knowhow/`。可选环境变量（路径不同时设置）：

```powershell
$env:ROBOTICS_KNOWHOW = "D:\autopathplanning\robotics-knowhow"
```

## 指标

| 指标 | 说明 |
|------|------|
| success_rate | 地图到达且无碰撞的比例 |
| avg_path_length | 成功轨迹 (x,y) 折线长度均值 [m] |
| plan_time_ms | 每步 `dwa_control` 平均耗时 [ms] |

比较顺序：success_rate ↑ → avg_path_length ↓ → plan_time_ms ↓

## 许可

DWA 逻辑源自 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics)（MIT）。本仓库实验框架 MIT。
