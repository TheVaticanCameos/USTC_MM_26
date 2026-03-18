# Beijing 最新年份地铁图数据（用于最短路作业）

## 文件

- `Beijing-2010-station-id-map.tsv`
  - 三列：`id`、`name`、`old_id`
  - `id` 从 1 开始，对应邻接矩阵的行/列编号
  - `old_id` 为原始站点表中的行号（从 1 开始）

- `Beijing-2010-adjacency-distance.csv`
  - 126×126 的邻接矩阵（CSV，无表头）
  - 第 i 行第 j 列为站点 i 到站点 j 的直达距离（单位：km）
  - 值为 `0` 表示 i 与 j 之间不可直达（或 i=j）
  - 已剔除孤立点（度为 0 的站点）

- `Beijing-2010-station-lines.txt`
  - 两列：`station`、`lines`（TSV 格式）
  - `station` 与 `station-id-map.tsv` 中的 `name` 一一对应
  - `lines` 为该站所属线路，多条线路用逗号分隔（如 `Line2,Line13,AirportExpress`）
  - 可用于判断换乘：相邻两站若不共享任何线路，则需要换乘

- `Beijing-2010-network.svg`
  - 使用经纬度坐标绘制的网络示意图（SVG，可直接用浏览器打开）

## 元信息

- 年份：2010
- 站点数：126
- 连通分量数：1
