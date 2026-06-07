# autopath

对标 [karpathy/autoresearch](https://github.com/karpathy/autoresearch) 的 **路径规划 Portfolio 自进化**（Phase 3）。

| Phase | 内容 |
|-------|------|
| 1 | DWA 单算法进化 ✅ |
| 2 | Dijkstra / A* / RRT* 多算法接线 ✅ |
| 3 | **Portfolio**：Agent 从 knowhow 白名单自由选算法进化 |

## 结构

```text
prepare.py              — 固定裁判（勿改）
planner.py              — 当前轮可执行代码（Agent 改）
portfolio_manifest.yaml — 本轮选用算法（Agent 改）
planners/*.py           — 算法快照（只读，切换时复制）
baselines/<algo>.json   — 分算法 baseline
maps/{dwa,grid,sampling}/
robotics-knowhow/       — registry + 算法卡片
program.md              — Agent 实验说明
```

## Quick start（Phase 3 Portfolio）

```powershell
cd D:\autopathplanning
pip install -e .

# 初始化四个算法的 baseline
python prepare.py --save-all-baselines --mode full

# 单轮评测（默认读 portfolio_manifest.yaml）
python prepare.py --mode full --notes "algo=dijkstra | hyp=... | change=..."
```

## 运行 Agent

```text
阅读 program.md Phase 3，完成 --save-all-baselines，然后开始 Portfolio 循环。
每轮自选算法，更新 portfolio_manifest.yaml，只改 planner.py，full 评测后 keep/rollback。
```

## 指标

字典序：success_rate ↑ → avg_path_length ↓ → plan_time_ms ↓  
**仅与本轮算法的 `baselines/<algo>.json` 比较**，不跨算法比 path_length。

## 许可

算法逻辑源自 [PythonRobotics](https://github.com/AtsushiSakai/PythonRobotics)（MIT）。
