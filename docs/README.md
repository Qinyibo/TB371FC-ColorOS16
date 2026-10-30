# 开发记录与接续入口

这里记录 TB371FC ColorOS 16 移植从早期功能修复到 R94T v23 的主要判断、实测结果和失败路线。整理日期：2026-10-30。这些是项目研究记录，不是跨设备通用优化结论。

如果只看更新内容，读[版本沿革](history.md)。要接着排流畅度，先读[性能排障](performance.md)、[测量方法](measurement.md)和[已知问题](known-issues.md)。要自己打包，读[构建与首启](build-and-first-boot.md)。

| 主题 | 记录内容 |
|---|---|
| [版本沿革](history.md) | 早期八项修复、v16/v17首启事故、#43、v22a/v22b及v23之间的关系 |
| [性能排障](performance.md) | 卡顿现象、窗口锁等待、有效改动、GPU/GC/绑核等失败对照 |
| [平行视窗](parallel-windows.md) | 微信缩放、B站首页宽度、原生规则持久化、冷启动路线 |
| [测量方法](measurement.md) | 真实桌面点击、快速上滑打断、FrameTimeline/TimeStats、容易误判的指标 |
| [构建与首启](build-and-first-boot.md) | 动态分区、APK容器、编译伴随文件、校验链、Magisk初始化后的服务域 |
| [原生笔与通信](pen-and-communication.md) | CTN730、BLE会话、系统输入、通信后台恢复及v17逐文件对照 |
| [相机](camera.md) | v7完成回调、v8历史试验、真实帧率和API测试边界 |
| [内核与音频](kernel-and-audio.md) | #43构建源码、IRQ/唤醒所有权、四扬方向与通话归还 |
| [界面与系统适配](ui-and-system.md) | 密度、原生键盘、投屏、AI停用、隐私密码与未完成的人脸支线 |
| [已知问题](known-issues.md) | 当前缺口、下一步需要的证据、不要重复的失效路线 |
| [数据与材料](evidence/README.md) | 24组帧指标、35份源材料指纹、对照条件和最终包运行结果 |
| [研究代码](../research/README.md) | 未保留的离线候选补丁源、采样配置和SQL；不参与默认构建 |

## 怎样理解状态

“在代码里修正”“能开机”“软件接口就绪”“用户实际可用”是不同层级。例如笔的原生事件桥已经启动，仍没有真实笔的书写、压感或充电验收；通信服务能自动恢复，也不等于手机流量、短信与通话已联测。

历史记录里的 ENABLED、候选或 pending 只描述当时现场。当前发布状态以 [v23最终验收](../release/v23/TESTING.md)和[最终运行摘要](evidence/v23-runtime.json)为准。下文保留失败与回退经过，避免旧候选因单个漂亮数字重新成为“推荐优化”。

## 公开材料的范围

公开移植代码、可重建补丁、构建脚本、技术经过及经过选取的数值数据。原始会话、账号数据库、完整屏幕录制和原始trace没有整包上传；对应技术摘要保留材料名与SHA256，见[材料索引](evidence/source-artifacts.json)。指标可以复查来源，不能把未公开的原始现场假装成仓库内已有文件。

内核是[独立的完整源码仓库](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc)，其许可、配置和构建说明与本仓库分开。ColorOS原厂闭源输入需自行准备。
