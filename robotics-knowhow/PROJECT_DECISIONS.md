# 已锁定产品决策（第一期）

## 1. 算法族：DWA

参考：PythonRobotics/PathPlanning/DynamicWindowApproach

## 2. 主指标（比较顺序）

1. success_rate 越高越好
2. 平局 avg_path_length 越低越好
3. 再平局 plan_time_ms 越低越好

## 3. 地图

- PythonRobotics DWA 自带障碍场景
- 自绘标准图 20 张（autopath/maps/）

## 4. 一晚预算

- quick 约 500 轮/夜

## 5. Agent

- Cursor Agent 读本机 autopath/program.md（第 3 步创建）
- 必读 agent/search-policy.md 与 dwa.md

---

# Phase 2：全局路径规划扩展

## 1. 算法

- Dijkstra：基于网格的全局最短路径算法
- A*：带启发式的 Dijkstra 改进版
- RRT*：基于采样的概率路径规划算法

## 2. 主指标（比较顺序）

1. success_rate 越高越好
2. 平局 avg_path_length 越低越好
3. 再平局 plan_time_ms 越低越好

## 3. 地图

- grid 格式：Dijkstra、A* 使用
- sampling 格式：RRT* 使用

## 4. Agent 规则

- 一次只进化 `registry.yaml` 里的 `active_algorithm`
- 根据 active_algorithm 读取对应算法卡片
- 修改仅限卡片中 `editable_in_planner` 字段列出的参数
