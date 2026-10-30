# 历史研究代码：不参与发布构建

这里分享没有保留的候选修改和测量工具，方便理解失败经过。它们不会由rom-build自动加载，也不是一套推荐优化模块。不要连续执行这些脚本：部分按历史工作目录、精确输入哈希、符号地址或smali结构运行，其他版本不适用。

| 目录 | 来源与最终状态 |
|---|---|
| `not-retained/lock-compat/` | 框架锁boost门槛和嵌套平衡修正；用户体验未改善，撤回 |
| `not-retained/art-gc/` | 精确libart符号上的后台collector切换延后；端点混合，恢复原ART |
| `not-retained/caption-experiments/` | recents、TO_BACK、800ms延后；不替代当前400ms焦点版 |
| `not-retained/launcher-replay/` | 缓冲完整手势重放；目标分支未被观察到，恢复原Launcher |
| `measurement/` | 短夹具、低开销trace配置、SQL与本机测试脚本 |

这些源码仅公开实际写过的可编辑改动，不附原厂APK/JAR/libart二进制或可直接安装候选。文件里的历史“offline”“candidate”等状态保持原意；当前解释以[性能记录](../docs/performance.md)为准。

已接受的正式修改位于[patches](../patches/)，两者分别存放，避免把研究分支装回发布包。修改设备前自行读清具体脚本；测量代码也带当时图标坐标，需按现场调整。
