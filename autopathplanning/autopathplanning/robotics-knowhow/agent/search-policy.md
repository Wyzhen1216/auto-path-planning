# Agent 搜索策略 — DWA Phase 1

完整决策见 ../PROJECT_DECISIONS.md。算法细节见 ../domains/path-planning/dwa.md。

## 目标指标顺序

success_rate > avg_path_length > plan_time_ms

## 只允许改 autopath/planner.py

允许：DWA 代价权重、采样分辨率、predict_time、速度/角速度界、脱困常数。

禁止：改 prepare.py、换算法族、删碰撞检测、改地图、加依赖、提交 results.tsv。

## 实验纪律

commit → quick 评测 → 更好则 keep，否则 git reset → 写 results.tsv。一晚约 500 轮 quick。
