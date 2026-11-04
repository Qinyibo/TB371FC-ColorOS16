# 新自然黑屏：r107 上 SystemUI 自退出，触控 REK 通过

**hardware_success_claimed=false；本轮没有补丁/刷写/重启/软件唤醒。** 用户自然报告不能唤醒，立即尝试采集时 USB 在 Windows/ADB 均未枚举、旧无线入口不可用。电脑采集等待器先就绪；用户重新插回已验证后置USB口后，7项并行读取成功。

## 必须保留的时序边界

**插入USB本身触发系统 WAKE_REASON_PLUGGED_IN**，所以12:51:21后首批状态是插线唤醒后的状态，不能冒称保住了断线前的完全原现场。用户当时是否物理恢复显示仍待其回答。电脑没有发电源键/输入命令或重启。此前按电源的历史保留在日志里，可独立审阅。

## 新的真实证据

- 12:48:24.617 用户按电源，系统收到 WAKE_REASON_POWER_BUTTON。
- 12:48:30.325 SystemUI旧进程死亡；12:48:30.396 ApplicationExitInfo 记录 **EXIT_SELF，status=10**；12:48:30.426 系统自行重建SystemUI。不是 Codex 杀进程，不是已经证实Java崩溃/OOM/ANR。旧进程专门logcat读取没有得到明确退出栈。
- 本次亮屏软件流程报告耗时5833ms，接近SystemUI退出时刻；因果方向尚未证实。
- 对应保留的内核唤醒转换（id22）触控先 PREPARED，之后显示PREPARED，REK=0xA1并IRQ_OPEN；本段 retained dmesg 未命中INIT0x9D／R96／PANEL_DEAD。**不能把这次直接归并到原9D硬件链，也不能据此排除所有面板电气问题。**
- 12:48:42.748 由于timeout再次休眠。12:51:21.456 插入USB触发唤醒，1053ms完成软件screen-on；这次触控同样REK通过。
- 插线后第一批快照：Awake、screen ON、请求亮度约6220、触控stage13/failed0/IRQ1；Launcher keyguard flags、canStartSystemGesture=false、TYPE_NO_OP，因此不能把锁屏期间不能Home直接判断为五指输入遗漏。之后12:52:57的另一次读取已是正常超时休眠stage2/failed0，背光0/bl_power4；这不是首批状态，不能混在一起。

脱敏依据：[SystemUI/电源时序](power-systemui-timeline.txt)、[退出记录](systemui-current-exit.txt)、[内核转换](kernel-transition-excerpt.txt)。完整dmesg、logcat、input/window、power/display、regulator、SurfaceFlinger与崩溃目录清单仅留本地。未公开原始应用信息、设备标识或整段私密日志。

## 给 Grok 的接续

优先对 **SystemUI在亮屏卡顿约5.8秒时EXIT_SELF status10** 的具体触发点提出可核验问题，区分厂商锁屏绘制超时/主动恢复与原INIT/REK失败。需要实际SystemUI方法时点名，Codex补当前文件摘录；不要先添加内核重试、强开IRQ或改输入resetState。

这是有现场时间戳的新证据，仍不是根因定论，也不是已修复。无线/USB断线前没有持续数据，不能补写当时输入消费者、背光或物理显示状态。
