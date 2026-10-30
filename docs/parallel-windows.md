# 微信、B站与平行视窗

## 这条路线为什么要保留

用户明确要求保留平行视窗。把微信切到原生横屏/全屏虽然能改变大小，却丢掉需要的双窗行为，因此不是最终修复。B站缩窄首页是明确保留的界面需求，后来做流畅度回退时曾错误地回退该框架，随即按用户要求恢复。不能把这项界面改动当成可随性能实验一起丢弃的参数。

## 微信小界面的具体原因

运行时的magicwindow配置有 `scaleWindow=0.8`；实际 `OplusBaseFlexibleConfig` 的几何缩放路径，在2944×1840横屏现场产生约0.625比例，逻辑窗约1416×2944而物理窗约885×1840。单独打开平行视窗开关只出现暂时变化，冷重开又恢复小界面。

最终将微信magicwindow的 `scaleWindow` 改为 `-1`，保留status启用与可拖动规则。测试确认物理窗约885×1840、界面正常放大，双窗仍在。没有通过全局DPI或把微信APK改成平板版来解决。

## 从运行时数据库到原生来源

最初用事务修改运行数据、触发窗口协议重载，只适合作为诊断和现机试验。双清后不能依赖某个用户数据库或每次后台重写它。

涉及两类原生来源：

- `sys_fantasy_window_managed`：微信和B站magicwindow。
- `sys_full_orientation_managed`：B站全方向及直播重启例外。

原生工厂位置为 `/my_product/etc/fantasy/`。系统还会接收ROM-update配置，因此需要同时看加载来源、内部版本、实际生效配置；只改工厂XML却被更高版本来源覆盖，会制造“刚改好又变回去”的现象。

v23使用已验证的规则内容作为原生输入，保留B站LiveRoomActivityV3的默认全屏与force_relaunch例外。两个应用都保留 `scaleWindow=-1`、可拖动双窗。旧 `r94_bili_native_rules` 不再默认种入，实际检查无旧规则维护进程；没有新增微信常驻模块。

当前可编辑内容：[规则JSON](../patches/native-window-rules.json)、[原生XML合并脚本](../patches/apply_native_window_rules.py)。这份合并器保留其他应用条目，不应把私人运行数据库拷给别人。

## B站首页宽度

需求最后明确为缩小居中的整个首页窗口，而不是修改原版B站信息流布局。改动位于：

```
oplus-services.jar
com.android.server.wm.CompactWindowBoundsCalculator
calculateBoundsInPosition(Task, int)
```

只在B站、居中/默认半屏路径使用1.6比例；左右双窗和全屏路径保持原分支。2944×1840现场的实测：

| 状态 | 边界或宽度 |
|---|---|
| 改前居中首页 | 约1471px宽 |
| 最终居中首页 | Rect(897,0—2046,1840)，1149px宽 |
| 搜索打开后的左窗 | Rect(0,0—1025,1840) |
| 微信独立窗 | 约885px宽 |

最初实际视频详情双窗、后续正常重启后的搜索双窗均有记录；v23交付前又验证1149px首页与1025px搜索左窗。不同屏幕/方向不应硬套这些像素数。

补丁源码：[patch_bili_native_middle_width.py](../patches/work/patch_bili_native_middle_width.py)。最终JAR是压缩封装；与测试过的未压缩候选DEX内容相同。精确文件哈希在[发布清单](../release/v23/manifest.json)。

## “等几秒再打断就顺”的检查

做了两次进程冷态与两次每应用预热5秒的同节奏对照，全程保留双窗和窄首页。四轮native present间隔P95桶均为13ms，missedFrames为124、136、229、257，不能据此证明预热稳定改善全段。

细采样确实看到启动窗口一帧127.62ms，其中52.93ms relayout包含49.72ms IPC及45.08ms WMS监视器等待；但 `getCurrentEmbeddedTask` 是等待者，冷态最大68.48ms、预热后92.43ms，尚未证明它是长锁持有者。辅助输入层创建次数冷态1、预热2，也没有“冷态总是创建更多”的证据。

预热组另见桌面Taskbar约64.59ms帧，包含45.06ms ClassLinker锁等待，锁持有者是同进程HeapTaskDaemon。这个例子说明应用初始化、ART、调度和窗口管理会交叠，不能只因时间上与双窗相关就直接关掉双窗。

完整数字和限制见[parallel-startup.json](evidence/parallel-startup.json)。没有因这轮假设额外加入新的优先级策略。
