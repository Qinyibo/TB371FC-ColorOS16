# 数值与材料索引

这些数据从本项目已有记录导出，不是重新跑的测试。范围截至2026-10-30；源材料SHA256在[source-artifacts.json](source-artifacts.json)。

| 文件 | 内容 |
|---|---|
| [frame-cohorts.csv](frame-cohorts.csv) | 24组native帧统计：GC延后、client合成与平行视窗冷热对照 |
| [gc-light-cohorts.json](gc-light-cohorts.json) | A1/B1/A2各次运行、实际ART哈希、原始温度读数；候选未保留 |
| [composition-cohorts.json](composition-cohorts.json) | 原合成/client/恢复三阶段；候选未保留 |
| [parallel-startup.json](parallel-startup.json) | 冷态/预热、细采样窗口路径与证据边界 |
| [communication-v17.json](communication-v17.json) | 实际v17提取的14份载荷哈希对照与init差异 |
| [v23-runtime.json](v23-runtime.json) | 最终包首启/重启的逐项结果、不同启动周期、B站边界与最终ZIP哈希 |
| [release-interruption-metrics.txt](release-interruption-metrics.txt) | 12次打开/返回夹具的24阶段与后两轮FrameTimeline统计 |

CSV的missedFrames为SurfaceFlinger原生计数器，Dropped Frame为FrameTimeline记录中的类别，不能直接互换。frame_duration_p95_bin_ms和present_interval_p95_bin_ms是直方图桶，不是精确到小数的百分位；present间隔含空闲/停留，不用于直接认定冻结。

GC和client各阶段之间经历不同运行状态/温度，不是恒温实验。thermal原始整数未在这里替某传感器强加物理含义，不能混同电池温度。比较应读对应正文的工作量与覆盖限制。

时间顺序以主机执行/版本归档为依据，双清后未同步的设备墙上时间可能为2025-01-01。数值摘要不含原始trace；因此仓库可以复用采样与查询、检查已公开汇总，但不能宣称已有全部原始现场可以一键重算。
