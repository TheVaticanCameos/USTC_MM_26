# Subway 作业数据集

本目录包含用于最短路/图算法作业的地铁网络数据。

## 目录结构

- `./hw_1/op_2/data/<City>/`
  - `<City>-<Year>-adjacency-distance.csv`
  - `<City>-<Year>-station-id-map.tsv`
  - `<City>-<Year>-network.svg`
  - `README.md`
- `./hw_1/op_2/data/summary.tsv`：各城市数据的索引表

## 顶点表（station-id-map.tsv）

文件名：`<City>-<Year>-station-id-map.tsv`

- 制表符分隔（TSV），首行为表头
- 三列：
  - `id`：站点编号，从 1 开始，对应邻接矩阵的行/列编号
  - `name`：站点名称
  - `old_id`：保留字段（一般不需要使用）

## 邻接矩阵（adjacency-distance.csv）

文件名：`<City>-<Year>-adjacency-distance.csv`

- CSV，无表头
- 尺寸：`N × N`（`N` 为该城市该年份的站点数）
- 语义（从 1 开始计数）：
  - `A[i, j] > 0`：站点 `i` 与站点 `j` 可直达，数值为直达距离（单位：km）
  - `A[i, j] = 0`：不可直达（或 `i=j`）
- 矩阵为对称矩阵（无向图）

## 线路信息（station-lines.txt）

文件名：`<City>-<Year>-station-lines.txt`

- 制表符分隔（TSV），首行为表头
- 两列：
  - `station`：站点名称，与 `station-id-map.tsv` 中的 `name` 一一对应
  - `lines`：该站所属的地铁线路，多条线路用逗号分隔（如 `Line2,Line13,AirportExpress`）
- 可用于判断换乘：相邻两站若不共享任何线路，则需要换乘

> **注意**：目前仅 Beijing 提供了线路信息。

## 可视化（network.svg）

文件名：`<City>-<Year>-network.svg`

- 网络示意图（SVG，可直接用浏览器打开）
- 仅用于帮助理解连通关系与站点分布，不用于精确测量距离

## 汇总表（summary.tsv）

文件名：`summary.tsv`

- 制表符分隔（TSV），首行为表头
- 常用字段：
  - `city`：城市名称
  - `year`：年份
  - `stations`：站点数
  - `components`：连通分量数量
