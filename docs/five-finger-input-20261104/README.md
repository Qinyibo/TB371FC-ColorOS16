# 给 Grok：五指收拢后普通触摸／Home 偶发失效，同步分析入口

最新：[实机OEM客户端Binder桥／接受版Launcher调用索引](oem-client-bridge/README.md)。

最新补件：[跨构件调用索引、fullscreen标志及performFinishAnimation](cross-artifact-followup/README.md)。

最新补件：[manager／输入消费者／全 DEX 定向引用／failsafe 武装点](ownership-followup/README.md)。

后续补齐：[实际 DEX 方法摘录、输入区域语义及 controller 身份对照](dex-excerpts/README.md)。

**尚未修复，hardware_success_claimed=false。请与黑屏线并行推进，不等待 Codex 独自完成。**

## 当前基线

- ROM 上次同步 `08b2145c86664a26ddbffc1b04f2f5e86e606898`；此目录是后续新增证据。
- Kernel 接续分支 [recovery-state-r107](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/recovery-state-r107)，已上传 tip `5bb573b6c07c152975585477a6171663ba6e03e0`；功能源码 `41082098de91855a809239bf64f339a16d39effe`。kernel main 仍旧，不要据 main 判断当前设备。
- 实机 r107；Launcher 已恢复接受版本 SHA256 `bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d`。旧 resetState 候选已撤回，不能算修复。
- 当前 oplus-services.jar SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`。下面核对来自该实际构件的 DEX 方法，不来自别版本的猜测。
- 黑屏／供电证据继续以 [r107 接续](../black-screen-handoff-20261103.md) 为准。此轮没有改内核、Framework、Launcher 或运行新补丁。

## 新现场与证据有效性

用户报告：连续两次五指收拢后，普通触摸／回桌面卡住；屏幕快熄灭前似乎又可滑两下。随后自愈。

23:29 的故障后快照：Awake；触控 awake=1、failed=0、IRQ=1；InputDispatcher enabled=true/frozen=false/filter=false，无残留 TouchStates，输入通道 responsive。焦点在小窗 App、桌面在后；Launcher canStartSystemGesture=true、TYPE_RESET_GESTURE，recents 非运行。快照只能描述当时状态，不能覆盖触发瞬间，也不能证明此前没有分发冻结。没有同步固件恢复失败的新证据，不能把这一亮屏故障直接归为 INIT9D。

早期短采集过早结束，用户操作发生在结束之后；该段“无 evdev 事件／IRQ不增长”**无效，不能用来指认驱动失灵**。原始输入包含坐标与应用信息，保留本地，不上传完整私密日志。

23:54 的持续采集确实覆盖两次多指动作与后续单指；用户明确答复“未复现，单指正常”。这是正常对照，不是修复验收。evdev约12秒、17900行；实时 Android 日志覆盖操作窗口。对应生命周期节选见 [normal-comparator.txt](normal-comparator.txt)。本轮采集均已停止，无重启、桌面重启、注入、主动熄屏或压力循环。

## 已核对的方法与一个已降级猜测

包 `com.android.server.oplus.input.exinputservice.globalgesture`：

1. `OplusMultiGestureFourStrategy.onMultiFingers(Bundle)`：>=4指进入 FOUR_ZOOM，发送暂停分发／开始消息；指针数降到4以下或 UP/CANCEL 时发送结束。实现覆盖用户说的四／五指。
2. `handleFourZoomStart()` 调 `verifyForbidFourFingersGesture()`，写 mForbidFourFingersGesture，允许后调用动画管理器 startAnmation；`handleFourZoomEnd()` 在该禁止标志为真时直接返回，否则 finishAnimation。
3. Start/Move/End 通过同一异步 Handler 消息 0x13/0x14/0x15 执行；开始注册20秒0x23超时，结束移除它。notifyAnimationEndByTimeOut 仅在 mCurrStatus==4 时收尾。
4. **“第二次开始直接覆盖禁止标志，抢在第一次队列End之前”目前不成立**：禁止标志是在 handleStart 中写入，Start/End 同队列。不要仅凭共享字段就提交去掉禁止检查的补丁。正常对照两次都有 handleStart/handleEnd 及 finishAnimation。
5. `OplusGestureAnimationManagerPolicy$2.onAnimationStart` 会写共享 mController，随后检查 isInAnimation；若手指已抬起则 resetGestureAnimation。remote targets 无效／target为空分支只清 isInAnimation 并返回；是否有另一侧自动清理，尚未追完。
6. `onAnimationCanceled()` 清 isInAnimation 并恢复帧率；`resetGestureAnimation()` 只有 mController 非空才调用 finishGestureAnimation 并清 controller/状态。不能仅据这些局部分支认定系统输入必然被卡。
7. WMS 侧存在 `OplusGestureAnimationController` 的 cleanupAnimation、cancelAnimation、scheduleFailsafe、mInputConsumerEnabled/updateInputConsumerForApp。已提取相关类供本地复核，尚未完成跨 Binder／动画监听器的所有权闭环。没有证据证明当前故障就是该 controller 残留。

## 请 Grok 直接推进的范围

- 核对全局多指 → WMS GestureAnimationController → FlexibleWindow/输入消费者的创建、正常结束、取消、空目标、Binder迟到回调、快速下一次手势各分支。谁持有输入、谁保证释放？利用实际队列顺序给反例，不泛讲竞态。
- 重点检查 End 已发出但动画 runner 迟到，或前一动画回弹未完就下一次收拢时，旧回调能否覆盖／清掉新会话；需要源码闭环或可执行反例。当前仅是待研究方向。
- 说明 input dump 还应有哪些现成字段能区分 App输入消费者、导航手势拦截与内核不出事件；先用已有资料，不再要求用户反复操作。
- 若确认真实契约缺口，回传最小候选 diff、对应原始方法／构件基线、失败反例和回退方法。目标是跨 App 长期稳定，禁止微信单独适配、固定间隔重置输入或直接关闭五指功能当修好。
- 黑屏供电／REK 根因可继续独立推进；不要把 r107 契约修正描述为黑屏已根治。

只上传脱敏事实和方法关系；未公开 OEM JAR、整段反汇编、原始私密日志或设备标识。此记录不声称 hardware 成功。
