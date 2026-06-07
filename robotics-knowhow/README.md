# Robotics Knowhow 知识库

面向路径规划 **Portfolio 自进化**（autopath Phase 3）的算法 knowhow 文档库。

---

## 当前阶段

| 步骤 | 状态 |
|------|------|
| Phase 1 DWA | ✅ 完成 — 最佳 e77f895 |
| Phase 2 多算法接线 | ✅ Dijkstra / A* / RRT* + prepare |
| **Phase 3 Portfolio** | ✅ 框架就绪 — `evolution_mode: portfolio` |
| Phase 4 Pipeline 组合 | 未开始 |

---

## Phase 3 要点

- [registry.yaml](registry.yaml) — `portfolio_allowed_algorithms`
- [agent/search-policy.md](agent/search-policy.md) — Agent 每轮流程
- 仓库根 [portfolio_manifest.yaml](../portfolio_manifest.yaml) — 本轮算法声明
- `baselines/<algo>.json` — 分算法 baseline（prepare 生成）

---

## 目录结构

```
robotics-knowhow/
├── PROJECT_DECISIONS.md   # Phase 1–3 决策
├── registry.yaml          # evolution_mode + 算法注册
├── index.md               # 选型树
├── agent/search-policy.md # Portfolio 流程
├── domains/path-planning/ # 算法卡片
├── maps/README.md         # 地图 JSON 规格
└── sources/pythonrobotics.md
```

---

## 与 autopath

| autopath 文件 | knowhow 引用 |
|---------------|--------------|
| `prepare.py` | registry、maps 目录 |
| `planner.py` | 卡片 `editable_in_planner` |
| `portfolio_manifest.yaml` | registry 白名单 |
| `program.md` | search-policy + PROJECT_DECISIONS |
