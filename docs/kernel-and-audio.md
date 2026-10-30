# #43内核、唤醒与四扬路由

## 当前内核是什么

最终v23保留4.19.325-perf+ #43，历史构建时间为2026-10-20 22:49 +0800。它是完整4.19内核与本机修改，不是把参考项目5.10/6.1模块强塞进来。

[独立内核仓库](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc)含66,826份被跟踪文件、完整配置、构建入口，以及本次真正使用的oplus_vnet外部模块源码。完整源和配置已公开，但没有完成一次从公开Git树独立重编并证明Image字节完全一致的验收。

历史Image SHA256：`c234e5c0ed600369816fb98f5d4a54748dc46bc4dcd5bff07529c82e165a2519`。

历史boot SHA256：`09d3c1bd67946575de8b0dad434f651e746747da2686fa227719142ad47cfbbe`。

## 为什么必须整理实际编译覆盖层

原构建脚本先确认stock11底树，再bind挂载11个触控/DSI/USB文件、两个音频文件并加入r94_route_core.h；编完会撤销挂载恢复底树。所以工作目录“现在看到的源码”不必然是 #43 的对应源码。

公开仓库把这14个实际参与构建的文件合入Git索引，逐个比对构建源哈希。新增[内核开发说明](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/main/docs/tb371fc)同时提供stock11→#43差异。该补丁的基准是当时stock11文件，不是v17→v23差异；不能拿它重复应用到已经含修改的公开树。

工具链记录包括LLVM21、GNU aarch64 binutils、固定config、构建用户/主机、版本43和时间。历史运行库曾依赖tc-shim；公开脚本使用LOCALVERSION空覆盖，避免Git目录带来的额外“+”。来源与许可按COPYING和原头文件保留，没有补造已丢失的上游Git历史。

## 触控/显示：让转换过程有明确所有者

触控固件下载、DSI面板准备/恢复、正常输入IRQ和IRQ wake不能各自无条件操作。#43的具体方向是：IRQ wake状态单一所有权、Hall/PM完成发布与转换owner同步，以及固件异常时先隔离输入包、关闭相关IRQ，等待正常PREPARE链路恢复。

源码可见 `nvt_irq_wake_ctrl_locked`、`nvt_hall_sleep_update`、`nvt_ts_pm_suspend/resume`、`nvt_panel_resume_prepare/arm/commit/abort` 等路径。正常IRQ disable放在ts锁外；Hall路径使用trylock，避免与取消工作/面板转换形成互等。终端NUL兼容与USB文件亦属于实际覆盖层，不能只抽出一个touch补丁宣称完整对应。

历史源码测试覆盖34个驱动/IRQ core失败与pthread用例，含ASan/UBSan，使用真实部分IRQ core逻辑，但硬件和工作队列原语有替身。它能揭示状态不平衡和特定交错，不能证明实物双击唤醒、所有面板批次与偶发黑屏全部修好。

异步HWC缓存试验没有合入 #43；本次不以“源码里出现过”判断是否交付。公开测试回执保留当时状态，运行状态以v23实机为准。

## 实际vnet源必须对上模块

最早找到的r94-vnet-source目录对应旧模块，哈希与当前包不符。最终定位到双栈候选目录，产物与v17/v23的oplus_vnet.ko精确相符：

```
01cb1335daddcf308d11076af1db50f5386c6bb94312243b02197d1a7bfc66bd
```

因此公开的是这份4.19适配的实际外部源码，不是同名旧源或另一个平台的参考文件。放在drivers/net/oplus_vnet不表示已改成内建；编译方式仍按外部模块及匹配的配置/符号CRC处理。

## 四扬方向与归还

音频路径不只是检测屏幕旋转再写寄存器。需要确认当前输出为扬声器、媒体活跃、AudioManager处于NORMAL；通话、耳机和蓝牙路径应回归原控制。方向helper通过原生控制接口请求，实际寄存器访问进入与固件/profile转换同一DSP互斥锁。

驱动按本机总线、四个I2C地址、固件名和芯片revision限定设备；请求带generation，逐设备记录ack、精确readback、errno与profile epoch。归还失败不能立刻宣布恢复，否则媒体旋转会踩到仍由通话持有的状态。

当前用户态源码在[speaker](../speaker/)，原生路由核心及tfa98xx修改在内核树。既有实现带低频状态确认/失败恢复，并不是“完全零轮询”。没有用录音保活或重启HAL来维持扬声器。

v23保留四扬0.29与 #43，但不能由模块已启动推出每个方向听感、真实通话双向音频及通话结束后的归还都已跨场景验收。继续测试应分别记录方向、输出路由、播放/通话状态、请求generation与实际ack。
