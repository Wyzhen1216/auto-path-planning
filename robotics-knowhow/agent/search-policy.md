# Agent 搜索策略 — Phase 2

完整决策见 ../PROJECT_DECISIONS.md。

## 目标指标顺序

success_rate > avg_path_length > plan_time_ms

## 算法选择流程

```
1. 读取 registry.yaml → 获取 active_algorithm
2. 根据 active_algorithm 读取对应算法卡片
3. 从卡片中获取 editable_in_planner 列表
4. 只修改 planner.py 中列表内的参数
```

## 当前支持的算法

| 算法 | eval_mode | 地图目录 | 卡片路径 |
|------|-----------|----------|----------|
| dwa | grid | autopath/maps/grid | domains/path-planning/dwa.md |
| dijkstra | grid | autopath/maps/grid | domains/path-planning/dijkstra.md |
| astar | grid | autopath/maps/grid | domains/path-planning/astar.md |
| rrt_star | sampling | autopath/maps/sampling | domains/path-planning/rrt-star.md |

## 修改权限

### 允许

根据 active_algorithm 对应的卡片，修改 `editable_in_planner` 中列出的参数：

- **DWA**: to_goal_cost_gain, speed_cost_gain, obstacle_cost_gain, predict_time, v_resolution, yawrate_resolution, max_speed, max_yawrate, robot_radius, robot_stuck_flag_cons
- **Dijkstra**: resolution, robot_radius, weight
- **A***: resolution, robot_radius, heuristic_weight
- **RRT***: robot_radius, max_iter, connect_circle_dist, goal_sample_rate, random_seed

### 禁止

- 改 prepare.py
- 换算法族（需修改 registry.yaml）
- 删碰撞检测
- 改地图格式
- 加依赖
- 提交 results.tsv

## 实验纪律

1. 修改参数 → commit
2. 运行 quick 评测
3. 更好则 keep，否则 git reset
4. 写 results.tsv
5. 一晚约 500 轮 quick