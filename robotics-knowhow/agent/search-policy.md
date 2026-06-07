# Agent 搜索策略 — Phase 2

完整决策见 [../PROJECT_DECISIONS.md](../PROJECT_DECISIONS.md)。

---

## 核心流程

```
读 registry.yaml → 读 active_algorithm → 读对应 knowhow 卡片 → 修改 planner.py
```

---

## 目标指标顺序

success_rate > avg_path_length > plan_time_ms

---

## 实验规则

### 1. 确定当前算法

打开 [registry.yaml](../registry.yaml)，查看 `active_algorithm` 字段：
- `dijkstra` → 读 [dijkstra.md](../domains/path-planning/dijkstra.md)
- `astar` → 读 [astar.md](../domains/path-planning/astar.md)
- `rrt_star` → 读 [rrt-star.md](../domains/path-planning/rrt-star.md)
- `dwa` → 读 [dwa.md](../domains/path-planning/dwa.md)（Phase 1）

### 2. 只允许改 autopath/planner.py

**允许修改**：卡片中 `editable_in_planner` 列出的参数

**禁止操作**：
- 改 prepare.py
- 换算法族（需人类修改 registry.yaml）
- 删碰撞检测
- 改地图文件
- 加外部依赖
- 提交 results.tsv

### 3. 地图对应

| active_algorithm | eval_mode | maps_dir |
|------------------|-----------|----------|
| dijkstra | grid | maps/grid/ |
| astar | grid | maps/grid/ |
| rrt_star | sampling | maps/sampling/ |
| dwa | dwa | maps/dwa/ |

---

## 实验纪律

```
commit → quick 评测 → 更好则 keep → 否则 git reset → 写 experiment_log.md
```

一晚约 500 轮 quick。

---

## 切换算法（人类操作）

修改 [registry.yaml](../registry.yaml) 的 `active_algorithm` 字段，然后重新启动 Agent。