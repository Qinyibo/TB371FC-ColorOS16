# OEM 客户端桥已补：当前实机构件与接受版 Launcher

**hardware_success_claimed=false；无修复候选。** 本轮只读复制两个现有文件、读取 SHA；没有切应用、输入注入、主动亮灭屏、重启或新建触发瞬间采集。

## 直接阅读：Binder 桥不再缺字节码

当前实机 `/system/framework/oplus-framework.jar` SHA256 `c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99`，10,535,923B，设备文件与本地完整复制的 SHA 一致。当前 oplus-services 设备文件仍为 `a5928b09…f46136`。来源见 [provenance.json](provenance.json)。

1. [OplusActivityManager.setInputConsumerEnabled](OplusActivityManager.md) 调 OplusActivityTaskManager 同名包装。
2. [OplusActivityTaskManager.setInputConsumerEnabled](OplusActivityTaskManager.md) 通过 getService 得到 IOplusActivityTaskManager，调用 void setter，随后直接 return true。
3. [IOplusActivityTaskManager Proxy](IOplusActivityTaskManager$Stub$Proxy.md)：描述符 `android.app.IOplusActivityTaskManager`，writeBoolean，事务 `0xA0`，reply=null，flag=1（oneway）。该 true 不是服务端状态/执行完成确认。
4. [Stub transaction160 分支](IOplusActivityTaskManager-transaction160.md)：readBoolean→enforceNoDataAvail→虚调用 setInputConsumerEnabled。实际 packed-switch 入口到该 label 的索引已核对为160，提供相关常量和完整分支，不上传整个巨大 onTransact。
5. [ATMSEnhance](OplusActivityTaskManagerServiceEnhance.md) 的类头明确继承该 Stub，其覆盖方法调 IOplusWindowAnimationManager.setInputConsumerEnabled；再到上一轮已提供的实际 WindowAnimationManager setter→updateInputWindowsLw。

因此“跨JAR缺少谁把客户端 setter 分派到 ATMSEnhance”的**静态 Binder 桥证据已补齐**。尚不能证明故障窗哪个 App 调用了什么值、是否实际执行，也不能因 oneway 就指认竞态根因。

## 取消 Launcher 副本限制

只读复制当前全局命名空间 `/system_ext/priv-app/OplusLauncher/OplusLauncher.apk`，完整文件 SHA 为接受版 `bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d`；本轮未重启桌面、未重新验证进程 maps。见 [来源](accepted-launcher-provenance.json)。

对当前接受版做同样全 DEX 定向引用索引：[accepted-launcher-references.json](accepted-launcher-references.json)，42690类/291255方法。点名成员引用与旧研究副本索引完全相同，此次证据无需借用撤回 APK。[RecentsViewAnimUtil](RecentsViewAnimUtil.md)／[RecentsAnimationControllerCompat](RecentsAnimationControllerCompat.md) 摘录现在也来自接受版。

接受版 Launcher 里命中的同名 setter 仍为 Recents Binder 链；未找到直接调 OEM OplusActivityManager／OplusActivityTaskManager setter 的引用。这不排除动态调用、其他构件、进程或其他代码路径。

## 其他点名范围

当前 OEM framework 索引：[oem-framework-references.json](oem-framework-references.json)，7296类/56885方法。没有直接引用 GestureController.shouldApplyInputConsumer、updateInputConsumerForApp 或 scheduleFailsafe。此前平台副本索引仍保留其版本边界，不将此次 OEM jar 当全运行时覆盖。未造故障，故没有触发瞬间 InputConsumers 新证据；已有23:29快照仍只是事后。

## 请 Grok 本轮收敛

Binder 包装／事务／继承分派已提供，不再卡在“没有OEM client jar”。请明确：新增桥是否支持一个可执行的真实遗漏路径；若仍没有，保留根因未证实，并指出下一条能区分上下层的具体既有日志或点名方法。不要把 oneway、同名字段、无武装 failsafe 或事后 consumer 状态直接升级为补丁理由。目标仍是跨 App 长期稳定；不重推 resetState，不要求用户造故障。

本轮只上传方法摘录和定向索引，没有上传 JAR/APK 整包、设备标识或原始私密日志。
