# autopath experiment log

## Round 1 | 5b5c2b4 | keep
- **假设**: 增大 to_goal_cost_gain 使轨迹更朝向目标，减少绕路
- **改动**: to_goal_cost_gain 0.15 -> 0.25
- **指标**: success_rate=1.0, avg_path_length=14.1158, plan_time_ms=58.06, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 2 | fc0792a | rollback
- **假设**: 继续增大 to_goal_cost_gain 可进一步缩短路径
- **改动**: to_goal_cost_gain 0.25 -> 0.35
- **指标**: success_rate=1.0, avg_path_length=14.7314, plan_time_ms=79.27, better_than_baseline=False
- **决策**: rollback 已 reset

## Round 3 | d26d3dc | keep
- **假设**: 增大 speed_cost_gain 鼓励更高线速度，缩短总路径
- **改动**: speed_cost_gain 1.0 -> 1.5
- **指标**: success_rate=1.0, avg_path_length=13.8006, plan_time_ms=41.53, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 4 | 30b1bb7 | keep
- **假设**: 继续增大 speed_cost_gain 可进一步缩短路径
- **改动**: speed_cost_gain 1.5 -> 2.0
- **指标**: success_rate=1.0, avg_path_length=13.4690, plan_time_ms=49.49, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 5 | 9d686b0 | keep
- **假设**: 继续增大 speed_cost_gain 可进一步缩短路径
- **改动**: speed_cost_gain 2.0 -> 2.5
- **指标**: success_rate=1.0, avg_path_length=13.4734, plan_time_ms=46.29, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 6 | 2ca3d88 | rollback
- **假设**: 提高 max_speed 上限使机器人更快到达目标
- **改动**: max_speed 1.0 -> 1.2
- **决策**: rollback 已 reset

## Round 7 | 3671a01 | keep
- **假设**: 缩短 predict_time 减少过度前瞻导致的绕路
- **改动**: predict_time 3.0 -> 2.0
- **指标**: success_rate=1.0, avg_path_length=14.1190, plan_time_ms=33.68, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 8 | d0c9c98 | keep
- **假设**: 降低 obstacle_cost_gain 允许更贴近障碍的短路径，同时恢复 predict_time
- **改动**: predict_time 2.0->3.0, obstacle_cost_gain 1.0->0.8
- **指标**: success_rate=1.0, avg_path_length=14.2800, plan_time_ms=42.06, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 9 | d0f5d74 | keep
- **假设**: 在较低 obstacle 权重下，speed_cost_gain=2.0 优于 2.5
- **改动**: speed_cost_gain 2.5 -> 2.0
- **指标**: success_rate=1.0, avg_path_length=14.2728, plan_time_ms=42.15, better_than_baseline=True
- **决策**: keep（后 reset 至 Round 4 最佳 30b1bb7 继续搜索）

## Round 10 | 8c9ed64 | rollback
- **假设**: 略降 obstacle_cost_gain 允许更贴近障碍的短路径
- **改动**: obstacle_cost_gain 1.0 -> 0.85
- **指标**: success_rate=0.8, avg_path_length=13.0405, plan_time_ms=52.11, better_than_baseline=False
- **决策**: rollback 已 reset（pr_default 碰撞失败）

## Round 11 | a1fdf3d | keep
- **假设**: 提高最大角速度使转弯更灵活，缩短路径
- **改动**: max_yaw_rate / max_delta_yaw_rate 40°->50°/s
- **指标**: success_rate=1.0, avg_path_length=13.4480, plan_time_ms=64.59, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 12 | e795ecd | rollback
- **假设**: 继续提高 max_yaw_rate 可进一步缩短路径
- **改动**: max_yaw_rate 50°->60°/s
- **指标**: success_rate=1.0, avg_path_length=13.4538, plan_time_ms=68.24, better_than_baseline=True
- **决策**: rollback 已 reset（略差于 Round 11）

## Round 13 | 2034b78 | rollback
- **假设**: 在更快转弯配置下略增 speed_cost_gain 可进一步提速
- **改动**: speed_cost_gain 2.0 -> 2.2
- **指标**: success_rate=1.0, avg_path_length=13.4512, plan_time_ms=53.32, better_than_baseline=True
- **决策**: rollback 已 reset（略差于 Round 11）

## Round 14 | d25fc74 | rollback
- **假设**: 在 0.25 与 0.35 之间微调 to_goal_cost_gain 可进一步优化
- **改动**: to_goal_cost_gain 0.25 -> 0.28
- **指标**: success_rate=1.0, avg_path_length=13.4516, plan_time_ms=58.40, better_than_baseline=True
- **决策**: rollback 已 reset（略差于 Round 11）

## Round 15 | 990c270 | keep
- **假设**: 提高 max_accel 使机器人更快达到目标速度，缩短路径
- **改动**: max_accel 0.2 -> 0.3
- **指标**: success_rate=1.0, avg_path_length=13.3850, plan_time_ms=85.70, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 16 | a68263a | rollback
- **假设**: 继续提高 max_accel 可进一步缩短路径
- **改动**: max_accel 0.3 -> 0.4
- **指标**: success_rate=1.0, avg_path_length=13.4244, plan_time_ms=93.52, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 15）

## Round 17 | 7b64bb8 | rollback
- **假设**: 更长 predict_time 改善障碍前瞻，减少绕路
- **改动**: predict_time 3.0 -> 3.5
- **指标**: success_rate=1.0, avg_path_length=14.3720, plan_time_ms=87.40, better_than_baseline=True
- **决策**: rollback 已 reset（显著差于 Round 15）

## Round 18 | 258d04b | keep
- **假设**: 在高加速度配置下略降 speed_cost_gain 平衡路径长度
- **改动**: speed_cost_gain 2.0 -> 1.8
- **指标**: success_rate=1.0, avg_path_length=13.3846, plan_time_ms=79.75, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 19 | 6b346fc | keep
- **假设**: 继续降低 speed_cost_gain 可进一步缩短路径
- **改动**: speed_cost_gain 1.8 -> 1.6
- **指标**: success_rate=1.0, avg_path_length=13.3832, plan_time_ms=72.81, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 20 | 76e8ebc | rollback
- **假设**: 继续降低 speed_cost_gain 可进一步缩短路径
- **改动**: speed_cost_gain 1.6 -> 1.4
- **指标**: success_rate=1.0, avg_path_length=13.9856, plan_time_ms=80.14, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19）

## Round 21 | 1396ac6 | rollback
- **假设**: 在 0.3 与 0.4 之间微调 max_accel
- **改动**: max_accel 0.3 -> 0.35
- **指标**: success_rate=1.0, avg_path_length=13.4010, plan_time_ms=79.07, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19）

## Round 22 | 8220317 | rollback
- **假设**: 在 1.6 与 1.8 之间微调 speed_cost_gain
- **改动**: speed_cost_gain 1.6 -> 1.7
- **指标**: success_rate=1.0, avg_path_length=13.3834, plan_time_ms=75.79, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19）

## Round 23 | dedf409 | rollback
- **假设**: 更早触发脱困逻辑避免长时间停滞
- **改动**: robot_stuck_flag_cons 0.001 -> 0.005
- **指标**: success_rate=1.0, avg_path_length=13.3832, plan_time_ms=73.37, better_than_baseline=True
- **决策**: rollback 已 reset（无改善）

## Round 24 | e1fbad2 | rollback
- **假设**: 用轨迹平均速度代替末端速度计算 speed_cost，鼓励全程高速
- **改动**: speed_cost 使用 np.mean(trajectory[:, 3])
- **指标**: success_rate=1.0, avg_path_length=13.9546, plan_time_ms=86.38, better_than_baseline=True
- **决策**: rollback 已 reset

## Round 25 | 973c820 | rollback
- **假设**: 轻微降低 obstacle_cost_gain 允许更紧凑路径
- **改动**: obstacle_cost_gain 1.0 -> 0.95
- **指标**: success_rate=1.0, avg_path_length=13.3858, plan_time_ms=82.48, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19）

## Round 26 | c353e35 | rollback
- **假设**: 略降 to_goal_cost_gain 平衡速度与朝向
- **改动**: to_goal_cost_gain 0.25 -> 0.23
- **指标**: success_rate=1.0, avg_path_length=13.3980, plan_time_ms=80.11, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19）

## Round 27 | f4e870a | rollback
- **假设**: 更细 yaw_rate_resolution 找到更优角速度
- **改动**: yaw_rate_resolution 0.1°->0.05°
- **指标**: success_rate=1.0, avg_path_length=13.3864, plan_time_ms=153.34, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 19，plan_time 翻倍）

## Round 28 | 26d327c | keep
- **假设**: 在当前最优参数下略缩短 predict_time 减少过度前瞻
- **改动**: predict_time 3.0 -> 2.8
- **指标**: success_rate=1.0, avg_path_length=13.2764, plan_time_ms=70.18, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 29 | 77944a5 | rollback
- **假设**: 继续缩短 predict_time 可进一步缩短路径
- **改动**: predict_time 2.8 -> 2.6
- **指标**: success_rate=1.0, avg_path_length=13.3498, plan_time_ms=63.48, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 28）

## Round 30 | bc2f2d4 | keep
- **假设**: 在 predict_time=2.8 下微调 speed_cost_gain
- **改动**: speed_cost_gain 1.6 -> 1.55
- **指标**: success_rate=1.0, avg_path_length=13.2760, plan_time_ms=71.14, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 31 | e77f895 | keep
- **假设**: 继续微调 speed_cost_gain
- **改动**: speed_cost_gain 1.55 -> 1.5
- **指标**: success_rate=1.0, avg_path_length=13.2760, plan_time_ms=71.75, better_than_baseline=True
- **决策**: keep 保留 commit

## Round 32 | 29b886a | rollback
- **假设**: 继续降低 speed_cost_gain
- **改动**: speed_cost_gain 1.5 -> 1.45
- **指标**: success_rate=1.0, avg_path_length=14.0832, plan_time_ms=75.82, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 31）

## Round 33 | 025ddab | rollback
- **假设**: 略增 to_goal_cost_gain 配合 predict_time=2.8
- **改动**: to_goal_cost_gain 0.25 -> 0.26
- **指标**: success_rate=1.0, avg_path_length=14.1090, plan_time_ms=73.06, better_than_baseline=True
- **决策**: rollback 已 reset

## Round 34 | 90f6a26 | rollback
- **假设**: 微调 max_yaw_rate 至 52°/s
- **改动**: max_yaw_rate 50°->52°/s
- **指标**: success_rate=0.8, avg_path_length=13.1915, plan_time_ms=86.54, better_than_baseline=False
- **决策**: rollback 已 reset（obstacle_field 超时失败）

## Round 35 | 698cc16 | rollback
- **假设**: 略降 max_accel 配合 predict2.8/speed1.5
- **改动**: max_accel 0.3 -> 0.28
- **指标**: success_rate=0.6, avg_path_length=13.9133, plan_time_ms=76.70, better_than_baseline=False
- **决策**: rollback 已 reset（narrow_passage/obstacle_field 失败）

## Round 36 | f91dac2 | rollback
- **假设**: 提高 max_delta_yaw_rate 使转向响应更快
- **改动**: max_delta_yaw_rate 50°->55°/s
- **指标**: success_rate=1.0, avg_path_length=13.2794, plan_time_ms=73.83, better_than_baseline=True
- **决策**: rollback 已 reset（略差于 Round 31）

## Round 37 | 24ef0a5 | rollback
- **假设**: 减少倒车倾向可缩短路径
- **改动**: min_speed -0.5 -> -0.4
- **指标**: success_rate=1.0, avg_path_length=13.2760, plan_time_ms=75.01, better_than_baseline=True
- **决策**: rollback 已 reset（与 Round 31 相同，无改善）

## Round 38 | 8953c97 | rollback
- **假设**: 更细 v_resolution 找到更优线速度
- **改动**: v_resolution 0.01 -> 0.008
- **指标**: success_rate=1.0, avg_path_length=13.2834, plan_time_ms=87.42, better_than_baseline=True
- **决策**: rollback 已 reset（差于 Round 31）

## Round 39 | f8eb5e5 | rollback
- **假设**: 略降 to_goal_cost_gain 在 0.23–0.25 之间寻优
- **改动**: to_goal_cost_gain 0.25 -> 0.24
- **指标**: success_rate=1.0, avg_path_length=13.2806, plan_time_ms=74.43, better_than_baseline=True
- **决策**: rollback 已 reset（略差于 Round 31）
