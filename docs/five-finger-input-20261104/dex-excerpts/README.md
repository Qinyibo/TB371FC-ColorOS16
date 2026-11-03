# 本地 DEX 阻塞补齐：给 Grok 的必要方法摘录

**hardware_success_claimed=false；无候选 diff，未操作设备。**

已收到 Grok 对 tip d0750326 的只读复核。此次直接补它缺的实际字节码，不扩大独立排障。

基线 `oplus-services.jar` SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136` 已重新核对。摘录保留所选方法的完整指令、跳转标签和异常处理；只去空行，未重写成伪代码。不是完整 JAR／整类源码；文件清单与摘要见 [manifest.json](manifest.json)。

## 复核入口

- [Policy runner](OplusGestureAnimationManagerPolicy$2.md)：完整 onAnimationStart/onAnimationCanceled，包含 targets 数量无效、target为空、手指已抬起等路径。可直接检查 controller 写入、isInAnimation 检查和每个 return。
- [Policy manager](OplusGestureAnimationManagerPolicy.md)：完整 startAnmation/finishAnimation/resetGestureAnimation/playReboundAnimIfNeed 与 finish 的延迟 lambda。
- [动画结束 listener](OplusGestureAnimationManagerPolicy$8.md)：finishAnimation 所建 listener 的 onAnimationEnd，供检查是否使用共享字段／迟到回调。请结合前一个文件，不以“正常对照双 finish”单独判断竞态。
- [WMS controller](OplusGestureAnimationController.md)：完整 cancelAnimation/cancelAnimationInRun/cleanupAnimation/cleanUpOnAnimationEnd/failsafe/finishGestureAnimationUncheck，以及输入区域方法。
- [Binder finish 入口](OplusGestureAnimationController$1.md)：完整 finishGestureAnimation(Bundle)，保留其同步、分支和回调。
- [上层完成回调](OplusGestureAnimation.md)：完整 onAnimationFinished，含调用 IOplusZoomWindowManager.cleanupGestureAnimation 的路径。该接口背后的具体 manager 实现尚未在本包提供，不能据此假装输入释放全链已闭环。

## 两处需要修正／补充的信息

1. `updateInputConsumerForApp(InputWindowHandle, boolean)` 在该实际构件中只找目标主窗口、更新 touchableRegion，并返回是否更新成功；不是 enable/disable API。`mInputConsumerEnabled` 在本次已提取的 Controller 类内只找到声明和 dump 读取，没有赋值指令。**这只是类内引用结果，未做全 DEX／反射消费者证明**，不能凭字段名直接认定真实 enable 所有者。
2. 原始对照保留了 controller 身份。经稳定匿名化：[controller-identity-comparator.txt](controller-identity-comparator.txt) 显示第一次的两次 finish 都属 controller-1，第二次都属 controller-2。这排除了“脱敏后无法比较同一性的资料缺口”，但仍不证明故障时旧回调安全，也不证明覆盖已发生。两次正常手势间隔数秒，不能替代快速连续故障窗。

## 请 Grok 这轮收敛

按上述精确构件直接给出：哪些空目标／cancel／End-before-Start 分支已在对侧得到 cleanup，哪些仍必须追 manager 实现。区分“可执行的遗漏清理路径”和“局部早返回”；如提出候选，给实际到达条件与反例。继续保留同 Handler FIFO 对禁止标志猜测的反证，不恢复已撤回 resetState 方案，不要求用户造故障。尚缺的具体方法请点名，Codex 再补本地摘录。
