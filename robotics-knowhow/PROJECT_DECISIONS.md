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
