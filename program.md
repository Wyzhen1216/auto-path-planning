# autopath — Agent 实验说明（对标 [karpathy/autoresearch](https://github.com/karpathy/autoresearch) 的 `program.md`）

你是路径规划 **自进化研究员**。人类维护本文件与知识库；**你只改 `planner.py`**，通过固定裁判 `prepare.py` 迭代 DWA。

## 三文件分工（与 autoresearch 对齐）

| 文件 | 角色 | 谁改 |
|------|------|------|
| `prepare.py` | 固定地图、仿真、指标、`results.tsv` | **禁止改** |
| `planner.py` | DWA 实现与 `Config` 参数 | **你只改这个** |
| `program.md` | 实验组织与纪律 | 人类改；你只读 |

## 必读上下文

1. 本仓库 `README.md`
2. 知识库（若路径不同，先读环境变量 `ROBOTICS_KNOWHOW` 指向的目录）：
   - `%ROBOTICS_KNOWHOW%/agent/search-policy.md`
   - `%ROBOTICS_KNOWHOW%/domains/path-planning/dwa.md`
   - `%ROBOTICS_KNOWHOW%/PROJECT_DECISIONS.md`

默认知识库路径（本机；可用环境变量 `ROBOTICS_KNOWHOW` 覆盖）：

```text
D:\autopathplanning\robotics-knowhow
```

PowerShell 设置（可选，与默认一致时可省略）：

```powershell
$env:ROBOTICS_KNOWHOW = "D:\autopathplanning\robotics-knowhow"
```

## 优化目标（字典序，不可争论）

1. **success_rate** 越高越好  
2. 平局 → **avg_path_length** 越低越好  
3. 再平局 → **plan_time_ms** 越低越好  

`prepare.py` 中 `is_better()` 已按此实现；`results.tsv` 列 `better_than_baseline` 供你快速判断。

## Setup（每次新会话先做）

```powershell
cd D:\autopathplanning
pip install -e .
python prepare.py --mode full --save-baseline
```

确认：

- `success_rate = 1.0`（当前 5 张地图）
- `avg_path_length` 约 14–15 m 量级（5 图均值）
- `baseline_results.json` 中 `maps_evaluated = 5`

若失败：不要改 `prepare.py`；检查 `planner.py` 是否与 PythonRobotics DWA 一致。

## 实验循环（Karpathy Loop）

每一轮 **必须** 按顺序执行：

1. **假设**：用一句话写本轮想验证的改动（例如增大 `obstacle_cost_gain` 避障更保守）。
2. **只改** `planner.py`（`Config` 默认值或 `calc_control_and_trajectory` 内逻辑，仍在 DWA 族内）。
3. `git add planner.py && git commit -m "exp: <简短描述>"`
4. `python prepare.py --mode full`
5. 读 `results.tsv` 最后一行与终端输出：
   - `better_than_baseline` 为 `True` → **保留** commit  
   - 否则 → `git reset --hard HEAD~1` 回滚
6. 在回复中记录：假设、改动、三指标、keep/rollback。

### 禁止

- 修改 `prepare.py`、`program.md`、`maps/`、`pyproject.toml`
- 更换算法族（A* / RRT / PRM 等）
- 删除或绕过碰撞检测
- 新增 pip 依赖
- `git add` / 提交 `results.tsv`（由 prepare 追加，仅人类可读盘）

### 允许改动（Phase 1）

见知识库 `dwa.md` frontmatter `editable_in_planner`，主要包括：

`to_goal_cost_gain`, `speed_cost_gain`, `obstacle_cost_gain`, `predict_time`,
`v_resolution`, `yaw_rate_resolution`, `max_speed`, `max_yaw_rate`,
`robot_radius`, `robot_stuck_flag_cons`

建议优先搜：`obstacle_cost_gain`, `to_goal_cost_gain`, `predict_time`（见 knowhow 敏感度）。

## 预算

- **quick**（`--mode quick`）：3 张图，约 **30s/轮**；仅作快速冒烟，**不与 baseline 比较**
- **full**（`--mode full`）：5 张图，约 **45s/轮**；**baseline 与过夜循环均用此模式**，目标一晚约 **80–150 轮**

## 启动提示（复制给 Agent）

```text
阅读 D:\autopathplanning\program.md，完成 Setup，然后做第 1 轮实验：
只改 planner.py，commit 后运行 python prepare.py --mode full，根据 better_than_baseline 决定 keep 或 git reset --hard HEAD~1。
```

## 成功标准（Phase 1 demo）

- 一晚 quick 循环中，出现至少一次 `better_than_baseline=True` 且人类可解释的改动
- `success_rate` 不得长期低于 baseline；为降 path_length 牺牲成功率视为失败
