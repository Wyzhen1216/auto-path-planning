# 地图 JSON 规格说明

## 地图格式类型

### 1. Grid 格式（栅格地图）

**适用算法**：Dijkstra、A*

**关键字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 地图唯一标识 |
| `resolution` | number | 栅格分辨率（米/格） |
| `robot_radius` | number | 机器人半径（米） |
| `start` | array[2] | 起点坐标 [x, y] |
| `goal` | array[2] | 终点坐标 [x, y] |
| `obstacles` | array[array[2]] | 障碍物折线点列表 |

**示例** (`maps/grid/pr_grid_01.json`)：

```json
{
  "id": "pr_grid_01",
  "resolution": 0.5,
  "robot_radius": 0.5,
  "start": [0, 0],
  "goal": [10, 10],
  "obstacles": [
    [[2, 2], [2, 8], [4, 8], [4, 2]],
    [[6, 2], [6, 6], [8, 6], [8, 2]]
  ]
}
```

---

### 2. Sampling 格式（采样空间）

**适用算法**：RRT*

**关键字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 地图唯一标识 |
| `robot_radius` | number | 机器人半径（米） |
| `start` | array[2] | 起点坐标 [x, y] |
| `goal` | array[2] | 终点坐标 [x, y] |
| `obstacle_circles` | array[array[3]] | 圆形障碍物列表 [x, y, radius] |
| `world_bounds` | array[4] | 世界边界 [min_x, max_x, min_y, max_y] |

**示例** (`maps/sampling/pr_sampling_01.json`)：

```json
{
  "id": "pr_sampling_01",
  "robot_radius": 0.3,
  "start": [0, 0],
  "goal": [15, 15],
  "obstacle_circles": [
    [5, 5, 2],
    [10, 7, 1.5],
    [7, 12, 2],
    [12, 10, 1.8]
  ],
  "world_bounds": [-2, 18, -2, 18]
}
```

---

### 3. Local 格式（局部地图）

**适用算法**：DWA

**关键字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 地图唯一标识 |
| `initial` | array[5] | 初始状态 [x, y, yaw, v, w] |
| `goal` | array[2] | 目标点 [x, y] |
| `obstacles` | array[array[2]] | 障碍物点列表 |

**示例** (`maps/local/pr_default.json`)：

```json
{
  "id": "pr_default",
  "initial": [0, 0, 0, 0, 0],
  "goal": [10, 10],
  "obstacles": [
    [0, 2],
    [4.0, 2.0],
    [5.0, 4.0],
    [5.0, 5.0],
    [5.0, 6.0],
    [5.0, 9.0],
    [8.0, 9.0]
  ]
}
```

---

## 目录结构

```
maps/
├── grid/          # 栅格地图（Dijkstra、A*）
│   ├── pr_grid_01.json
│   ├── pr_grid_02.json
│   └── ...
├── sampling/      # 采样空间（RRT*）
│   ├── pr_sampling_01.json
│   ├── pr_sampling_02.json
│   └── ...
└── local/         # 局部地图（DWA）
    ├── pr_default.json
    └── ...
```

## 命名规范

- 地图文件名：`pr_{format}_{number}.json`
- `format`：`grid` / `sampling` / `local`
- `number`：两位数序号（01, 02, 03...）

## 坐标约定

- 使用笛卡尔坐标系
- 单位：米（m）
- 角度：弧度（rad）