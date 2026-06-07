# 地图格式规范

本目录定义 autopath 使用的地图文件格式。

## 地图类型概览

| 类型 | 给谁用 | 关键字段 |
|------|--------|----------|
| grid | Dijkstra、A* | `resolution`, `robot_radius`, `start`, `goal`, `obstacles` |
| sampling | RRT* | `start`, `goal`, `robot_radius`, `obstacle_circles`, `world_bounds` |

---

## 1. Grid 格式（栅格地图）

适用于基于网格的路径规划算法（Dijkstra、A*）。

### 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `resolution` | float | 栅格分辨率（米） |
| `robot_radius` | float | 机器人半径（米） |
| `start` | [x, y] | 起点坐标 |
| `goal` | [x, y] | 终点坐标 |
| `obstacles` | list | 障碍物列表，每项为折线点序列 |

### 示例

```json
{
  "resolution": 0.1,
  "robot_radius": 0.5,
  "start": [0.0, 0.0],
  "goal": [10.0, 10.0],
  "obstacles": [
    [[2.0, 2.0], [2.0, 8.0], [4.0, 8.0], [4.0, 2.0]],
    [[6.0, 2.0], [6.0, 8.0], [8.0, 8.0], [8.0, 2.0]]
  ]
}
```

---

## 2. Sampling 格式（采样地图）

适用于基于采样的路径规划算法（RRT*）。

### 关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `robot_radius` | float | 机器人半径（米） |
| `start` | [x, y] | 起点坐标 |
| `goal` | [x, y] | 终点坐标 |
| `obstacle_circles` | list | 圆形障碍物列表 `[[x, y, radius], ...]` |
| `world_bounds` | [min_x, max_x, min_y, max_y] | 世界边界 |

### 示例

```json
{
  "robot_radius": 0.5,
  "start": [0.0, 0.0],
  "goal": [10.0, 10.0],
  "obstacle_circles": [
    [3.0, 3.0, 1.0],
    [7.0, 7.0, 1.5],
    [5.0, 5.0, 0.8]
  ],
  "world_bounds": [-1.0, 11.0, -1.0, 11.0]
}
```

---

## 文件命名规范

```
{algorithm}_{map_name}_{difficulty}.json

示例：
- grid/maze_simple_easy.json
- grid/maze_complex_hard.json
- sampling/random_obstacles_medium.json
```