# 一次性交接入口：当前构件＋完整相关类＋所有既有证据

用户要求停止逐方法补件。本包一次给出能提供的整套材料，不再以“缺下一小段DEX”重复来回。

## 先读的新结论与边界

1. 最新自然事件：按电源→约5.8秒→SystemUI EXIT_SELF status10并被系统重建。同窗保留触控REK0xA1/IRQ_OPEN，不是已命中旧INIT9D。完整脱敏现场在 [事件入口](../black-screen-20261104/README.md)。
2. 实机当前SystemUI文件SHA **8ad70cc7…**，新进程31266命名空间下文件SHA相同；之前3079已死亡，其映射未能重核，**不能反推旧进程必然使用当前文件字节**。
3. 当前SystemUI全DEX定向exit/halt/killProcess索引中，唯一直接System.exit调用位于flags.SystemExitRestarter.restartSystemUI，传0。不能把EXIT_SELF10直接归给这个方法。
4. 当前platform framework中 RuntimeInit$KillApplicationHandler.uncaughtException 含const10并在多处finally路径执行killProcess后System.exit(10)；还提供其他exit调用索引。**存在该路径不等于本次命中它**；没有异常栈/调用证据就不声称Java崩溃已定根因。
5. ApplicationExitInfo的reason=EXIT_SELF与status字段是不同信息。status10是本次退出状态数值，没有在本轮证据里找到“10专门等于锁屏超时恢复”的语义表；禁止发明该映射。
6. 用户不在Pad前，插USB后物理是否恢复显示为**未知**。USB插入自身触发PLUGGED_IN唤醒，首批快照是插线后；后续正常超时睡眠与首批分开。

## 这次完整给什么

- [全部相关完整类 ZIP](complete-related-classes.zip)，逐类路径和SHA见 [class-inventory.json](class-inventory.json)。由六个当前构件提取，完整类及其所有方法，不再裁成单个早返回。包括SystemUI/Oplus锁屏、ScreenOn/Off、生命周期、PowerBlock、Restarter/异常/Watchdog、平台RuntimeInit/ApplicationExitInfo、PMS/DisplayPowerController/DisplayPowerState/PhoneWindowManager、Gesture/Zoom/InputConsumer/WindowAnimationManager及OEM ATMS桥。
- 另将全DEX退出索引涉及的类加入包中，避免漏掉不符合关键字类名的退出实现。提取按类名定向，不等于完整反编译整个ROM；**原始六构件也已放本地私有全量包，可补查任何其他类，不再依赖摘录**。
- 五份完整定向退出调用索引＋DEX扫描范围；六个构件精确SHA见 [artifacts.json](artifacts.json)。本次对设备核对了framework、services、oplus-framework、oplus-services；SystemUI与接受版Launcher已只读复制且SHA一致。
- 复现索引/导出工具Java源码一并提供。使用既有dexlib2/baksmali API35；没有改动原指令或重新签名/安装任何构件。

## 所有前序证据集中入口

- [完整五指材料树](../five-finger-input-20261104/README.md)：包括事后/正常对照、FIFO反证、完整cleanup路径、真实consumer/字段所有者、全DEX跨构件索引、接受版Launcher和OEM Binder桥、既有日志可见性。resetState试验已撤回，不再重推。
- [r107/供电接续](../black-screen-handoff-20261103.md) 与 [供电所有权证据](../panel-power-ownership-20261103.json)。
- [当前r107内核全源码分支](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/recovery-state-r107)；功能提交41082098d，不能看仍旧的main误认当前设备。

## Grok 一次性审阅范围

在完整类和原始构件可用的条件下，直接交叉SystemUI退出、RuntimeInit异常、锁屏绘制阻塞、PhoneWindowManager与DisplayPowerController/PMS screen-on等待链。尽可能提出一条有实际日志/可达性支撑的故障链与可反驳条件；分清源码可达、日志命中、因果证实。若无法定位，明确唯一还缺的运行期证据，不再按一个方法一轮地索要摘录。

仍无可证实根因/修复diff，hardware_success_claimed=false。状态码10和5.8秒相关不等于因果；不要先改内核、造五指故障、做唤醒压力测或重启平板。

## 私有全量包

另交付本地 `TB371FC_GROK_COMPLETE_20261104_PRIVATE.zip`：六个准确APK/JAR、全部完整类/索引、整套前序公开材料、本次原始输入/窗口/电源/内核/退出/崩溃日志以及既有五指采集。含原始应用/设备信息，供用户直接转交，**不上传公开GitHub**。包内附文件SHA清单。公开包提供脱敏资料与源代码审阅上下文。
