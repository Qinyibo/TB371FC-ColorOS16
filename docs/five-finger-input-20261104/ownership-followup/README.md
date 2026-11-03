# Grok 点名补件：manager、输入消费者、全 DEX 引用与 failsafe

**资料补齐，无 diff，hardware_success_claimed=false。无设备操作。** 本包对应上一轮 d48a1a9 的点名请求，不扩大独立排查。

## 直接阅读

- [OplusZoomWindowManagerService](oplus-services-OplusZoomWindowManagerService.md)：cleanupGestureAnimation、hasGestureAnimationController、startGestureAnmation、checkAnimationReady。
- [Controller 置位和 failsafe](oplus-services-OplusGestureAnimationController.md)：构造、initializeDragFullScreenAnmation、scheduleFailsafe及其 runnable 的 lambda。
- [Policy $3](oplus-services-OplusGestureAnimationManagerPolicy$3.md)／[Policy $5](oplus-services-OplusGestureAnimationManagerPolicy$5.md)：完整非构造方法，补回弹/动画 listener。
- [WindowAnimationManager](oplus-services-OplusWindowAnimationManager.md)／[ATMS入口](oplus-services-OplusActivityTaskManagerServiceEnhance.md)／[InputMonitorExt桥接](oplus-services-InputMonitorExtImpl.md)：另一组真实 mInputConsumerEnabled 的初始化、读写、输入窗口更新请求。
- [Compact consumer](oplus-services-OplusCompactWindowInputConsumer.md)：register/unregister 及构造；[FullScreenDragHandle](oplus-services-OplusFullScreenDragHandleSurface.md)／[BlurBackground](oplus-services-OplusBlurBackgroundSurface.md)：对应 create/unregister/destroy。这些是确实存在的输入对象，不代表已点名本次吞事件的对象。
- 本地平台服务副本的 [InputMonitor](services-local-copy-InputMonitor.md)、[InputConsumerImpl](services-local-copy-InputConsumerImpl.md)、[WMS](services-local-copy-WindowManagerService.md)：基础 create/destroy 与 Binder死亡清理。该 services.jar 副本 SHA 见 manifest，**本轮未重新核对它与当前设备一致**，跨构件结论须保留此边界。

## 全 DEX 定向索引：避免继续靠字段名推断

实际 oplus-services.jar a5928b09…：扫描该 JAR 全部 DEX（11891类、100512方法），只查询点名成员与输入消费者 register/unregister/get enabled 引用；不是全项目审计。额外本地 services.jar 副本：22922类、180303方法。清单保留 DEX entry、完整所属类、方法参数/返回、引用指令序号、opcode；参数列表是工具输出格式，不是 smali 方法描述符。

[oplus引用索引](oplus-services-references.json)、[平台副本索引](services-local-copy-references.json)、[关键汇总](targeted-index-summary.json)。字段赋值仅统计直接 IPUT/SPUT；不排除反射、JNI、其他 JAR、优化/内联或实现替代。

1. GestureAnimationController.mInputConsumerEnabled 在 oplus-services **全 DEX 的直接赋值为0**；同名 WindowAnimationManager 字段则在其构造、setInputConsumerEnabled 中有写入。两者不可混用。
2. `scheduleFailsafe` 在这两个扫描构件中只有定义，没有找到直接调用点。因此上轮“failsafe可补”的结论只能保留为方法可执行清理，**不能假定该计时器实际已武装**。摘录给出1秒调度方法及回调；没有 arm 现场证据。
3. `shouldApplyInputConsumer`／`updateInputConsumerForApp` 在两个构件的直接调用索引均为空。不能凭定义证明当前系统调用它们；也不能据此宣称运行期永不触发，其他构件/动态路径不在本索引范围。
4. manager cleanup 实现不是空壳：保存旧controller→先将manager引用置null→调用旧controller.cleanupAnimation→清理位置表。hasGestureAnimationController 还可因 SplitScreenManager.isTaskInMaintainState 为真而返回真，不能简单等价为controller非空。具体分支看完整摘录。

## 请 Grok 收敛

用补件回答：manager 引用清理与真实输入区域/消费者撤销是否足以闭合；哪些失败路径仍缺 owner／调用方证据。请将“存在failsafe方法”与“实际武装”分开，取消无证据的兜底假定。若需其他构件的特定方法，请点名类/方法；不要要求用户造故障，不依据空直接引用索引臆造修复，不恢复 resetState 候选。

所有摘录均为选择方法的完整字节码，仅去空行；无原始设备坐标、应用日志或 JAR 整包。候选修改仍为无。
