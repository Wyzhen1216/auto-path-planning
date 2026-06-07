# PythonRobotics 溯源

本知识库以 PythonRobotics 为骨架，引用其算法实现。

---

## 仓库信息

- 仓库：https://github.com/AtsushiSakai/PythonRobotics
- 文档：https://atsushisakai.github.io/PythonRobotics/
- 许可：MIT

---

## PathPlanning 源路径

| 算法 | 源文件路径 |
|------|------------|
| DWA | `PathPlanning/DynamicWindowApproach/dynamic_window_approach.py` |
| Dijkstra | `PathPlanning/Dijkstra/dijkstra.py` |
| A* | `PathPlanning/AStar/a_star.py` |
| RRT* | `PathPlanning/RRTStar/rrt_star.py` |

---

## 其他相关模块

| 模块 | 说明 |
|------|------|
| RRT | `PathPlanning/RRT/rrt.py` — RRT* 的基类 |
| PRM | `PathPlanning/PRM/prm.py` — 概率路线图 |
| LQR-RRT* | `PathPlanning/LQRRRTStar/lqr_rrt_star.py` |

---

## 使用方式

在 autopath 实验中，参考上述源文件实现对应算法的 `planner.py`。