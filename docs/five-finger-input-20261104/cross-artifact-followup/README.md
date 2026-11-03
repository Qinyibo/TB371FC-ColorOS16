# 第三轮点名件：跨构件索引与 performFinishAnimation

**hardware_success_claimed=false；无修改候选、无设备操作。** 对应 Grok 对 tip8028586 的点名补件。

## 本轮入口

- [performFinishAnimation / InWms](oplus-services-OplusGestureAnimationController.md)、[runnable桥接](oplus-services-OplusGestureAnimationController$$ExternalSyntheticLambda7.md)、[Controller$3结束/取消监听器](oplus-services-OplusGestureAnimationController$3.md)。完整方法保留跳转/异常处理，不把局部 return 直接升级成遗漏修复。
- `mGestureFullScreenDragStart`：所有直接写入位置见 [targeted-summary.json](targeted-summary.json)；实际 a592 构件里只有构造默认 false、initializeDragFullScreenAnmation 置 true。所扫描构件未发现另一次清 false。完整置位方法已在 [上一轮补件](../ownership-followup/oplus-services-OplusGestureAnimationController.md)。这不证明必须给旧 controller 清 false：manager 正常丢弃 controller 是另一种生命周期结束方式，不能只据字段不复位造补丁。
- [已有 input 快照](existing-input-snapshot.txt)：只摘取23:29事后 recents consumer NOT_VISIBLE、通道 NORMAL/responsive 状态；无法覆盖触发瞬间，不能判定故障时它是否拦截。未新开 ADB 采集。

## 跨构件检索结果与边界

每个构件都有 SHA／DEX范围见 [manifest.json](manifest.json)，命中索引保留所属类，避免“同方法名”被拼成错误链。

1. `oplus-services` 为当前已核对基线 a5928b09…。
2. `older-service-payload` 虽本地文件名叫 framework.jar，其 DEX 类/数量是服务代码，与当前 oplus-services 相似；它是旧发布payload，**不作为当前平台 framework 的额外覆盖**。
3. `platform-framework-copy` 是既有 framework-bars.jar，SHA43f4802b…、37959类/284659方法；`platform-services-copy` 是上轮已标明的本地 services.jar，SHA90948f13…。本轮未对设备重新核对，跨版本结论有此限制。
4. `launcher-withdrawn-copy` 是已撤回研究副本97ac1b9d…，**不是当前安装版本**。先前逐方法比较仅 resetState 一条指令不同；本轮只摘录不涉及该方法的调用方作为线索，不重推候选、不把副本扫描当当前整APK验收。

### WindowAnimationManager 开关链

实际 oplus-services 内只有 ATMSEnhance.setInputConsumerEnabled 直接调 IOplusWindowAnimationManager 的 setter（上一轮索引已给）。此次新增构件内没有找到对该 ATMSEnhance setter 的直接调用。**远端/Binder客户端调用桥尚未找全**，不能宣称无人调用，也不把 Launcher 的同名 Recents 方法误接到它。

Launcher 研究副本存在 [RecentsViewAnimUtil.setInputConsumerEnabled](launcher-withdrawn-copy-RecentsViewAnimUtil.md)→[RecentsAnimationControllerCompat](launcher-withdrawn-copy-RecentsAnimationControllerCompat.md)→Shell IRecentsAnimationController 的链；其余调用位置见 [Launcher索引](launcher-withdrawn-copy-references.json)。这里的 Binder owner 与 IOplusWindowAnimationManager 不同，不是已闭合的同一开关。

### Gesture 输入方法调用方

在上述构件的直接方法引用中仍未找到 GestureController.shouldApplyInputConsumer / updateInputConsumerForApp / scheduleFailsafe 的调用。索引为定向全DEX直接引用检索；不覆盖其他未提供JAR、JNI、反射、方法句柄、内联。不能把“无命中”写成全系统永不调用。

**剩余资料缺口明确到构件：OEM 客户端桥（例如实际 oplus-framework.jar / OplusActivityTaskManager 客户端）未在这批本地构件中提供。** 本轮不扩大搜索或拿别版本冒充；若审阅确实依赖该桥，请点名需要的类/方法再补。

[oplus索引](oplus-services-references.json)、[平台framework副本索引](platform-framework-copy-references.json)、[平台services副本索引](platform-services-copy-references.json)、[可复现索引工具](IndexGestureOwnership.java)。工具通过 dexlib2/baksmali API，仅提取指定成员引用及包含方法所在类到本地，原始JAR不上传。

## 交给 Grok 的本轮问题

用 performFinishAnimation 与 Controller$3 对照正常 cleanup 的后续路径，明确哪些空目标/无dim/无handler分支只是不启动动画，哪些真的缺必要所有权释放；缺证据就点名，不推测永久吞输入。对跨构件开关保留未闭合边界；不要继续用 GestureController 同名字段、无调用点的 failsafe 或 NOT_VISIBLE 的事后 consumer 直接认定根因。当前仍无可提交修复，不造故障。
