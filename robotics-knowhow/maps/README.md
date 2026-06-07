# 地图 JSON 规格

本目录存放路径规划评测用的地图文件，按算法类型分两类。

---

## 1. Grid 地图（Dijkstra / A*）

**存放目录**: `maps/grid/`

**适用算法**: Dijkstra、A*

### JSON 格式

```json
{
  "name": "simple_corridor",
  "resolution": 0.5,          // 网格分辨率 [m]
  "robot_radius": 0.3,        // 机器人半径 [m]
  "start": [0.0, 0.0],        // 起点 [x, y] [m]
  "goal": [10.0, 10.0],       // 终点 [x, y] [m]
  "world_bounds": [           // 世界边界 [m]
    -5.0, 15.0,               // [min_x, max_x]
    -5.0, 15.0                // [min_y, max_y]
  ],
  "obstacles": [              // 障碍物折线点列表
    [[-5, -5], [15, -5]],     // 下边界墙
    [[15, -5], [15, 15]],     // 右边界墙
    [[15, 15], [-5, 15]],     // 上边界墙
    [[-5, 15], [-5, -5]],     // 左边界墙
    [[3, 0], [3, 8]],         // 内部障碍墙 1
    [[7, 5], [7, 12]]         // 内部障碍墙 2
  ]
}
```

### 字段说明

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `resolution` | float | m | 网格分辨率，越小精度越高但计算量增大 |
| `robot_radius` | float | m | 机器人半径，用于碰撞检测膨胀 |
| `start` | [float, float] | m | 起点坐标 |
| `goal` | [float, float] | m | 终点坐标 |
| `world_bounds` | [float, float, float, float] | m | [min_x, max_x, min_y, max_y] |
| `obstacles` | [[float, float], ...] | m | 障碍物折线点，每段墙用连续点描述 |

### 示例文件

见 `maps/grid/simple_corridor.json`

---

## 2. Sampling 地图（RRT*）

**存放目录**: `maps/sampling/`

**适用算法**: RRT*

### JSON 格式

```json
{
  "name": "circles_obstacles",
  "start": [0.0, 0.0],        // 起点 [x, y] [m]
  "goal": [10.0, 10.0],       // 终点 [x, y] [m]
  "robot_radius": 0.5,        // 机器人半径 [m]
  "world_bounds": [           // 世界边界 [m]
    -2.0, 15.0,               // [min_x, max_x]
    -2.0, 15.0                // [min_y, max_y]
  ],
  "obstacle_circles": [       // 圆形障碍物列表
    [5.0, 5.0, 1.0],          // [x, y, radius]
    [3.0, 6.0, 2.0],
    [3.0, 8.0, 2.0],
    [7.0, 5.0, 2.0],
    [9.0, 5.0, 2.0]
  ]
}
```

### 字段说明

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `start` | [float, float] | m | 起点坐标 |
| `goal` | [float, float] | m | 终点坐标 |
| `robot_radius` | float | m | 机器人半径 |
| `world_bounds` | [float, float, float, float] | m | [min_x, max_x, min_y, max_y]，随机采样区域 |
| `obstacle_circles` | [[float, float, float], ...] | m | 圆形障碍物 [x, y, radius] |

### 示例文件

见 `maps/sampling/circles_obstacles.json`

---

## 3. 地图命名规范

- 文件名使用小写字母 + 下划线：`simple_corridor.json`
- 文件名应描述地图特征：`narrow_passage.json`、`maze_10x10.json`
- 每个地图文件应包含 `name` 字段，与文件名一致

---

## 4. 地图生成建议

### Grid 地图
- 从 PythonRobotics Dijkstra/A* demo 的 `ox, oy` 障碍列表转换
- 边界墙必须闭合
- 内部障碍可以是任意折线

### Sampling 地图
- 从 PythonRobotics RRT* demo 的 `obstacle_list` 转换
- 圆形障碍物更适合 RRT* 的碰撞检测
- `world_bounds` 决定随机采样范围