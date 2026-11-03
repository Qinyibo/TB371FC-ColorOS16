# 已撤回：手势拦截器清理试验 r1

当前为已撤回的试验候选。曾在实机确认加载候选，之后用户仍报告应用可点但 Home 手势失效，继而出现内核 INIT/REK 恢复失败的黑屏。原版桌面 bdd74 已恢复，未重启平板、未刷分区；撤回后一次正常唤醒仍未通过触控 REK。不能证明桌面候选与黑屏的因果关系，也不能宣布交互异常已解决；未集成到 v27 ZIP。

隔离真实 ART/Handler 验证为 80 项、原版失败 20 项、候选全部通过，仅证明局部清理行为。实际 UI 套件因旧 runner 缺少 android.test.RepetitiveTest，在测试前中止；其打印的 OK 不算通过。测试脚本已增加运行库和全部 CASE 标记校验，但修正后的 UI 套件尚未执行。当前不继续安装或推广本候选。

## 修改

原厂 `OplusInputInterceptHelper.resetState()` 在 Handler 非空、但 `timeoutRunnable` 已不在队列时提前返回，跳过释放旧 Handler、监听器、借用的 VelocityTracker 引用和恢复阈值。超时已经执行、被取消或未排队均可进入该分支；`timeoutRunnable` 和新输入消费者构造路径都会调用 resetState。新消费者随后会重绑回调，但旧阈值未必在进入普通手势前恢复。

只将这条 `return-void` 改为跳转至本方法既有清理段。回调仍在队列时照旧移除，已不在队列时只跳过移除；不新增超时、线程、重建输入通道、应用白名单或输入注入。借用的 VelocityTracker 只释放引用，不代替其所有者回收。CUI 与普通平板阈值沿用原方法。

固定输入 Launcher SHA256 `bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d`；候选 `97ac1b9d0ab1f0986b8b25d41b39a0d5dd378a7518239bae4acf02173080bf55`，87,798,739 字节。APK 仅 classes5.dex 变化；序列化后对该 DEX 的 54,946 个方法比较，只有目标方法的一条指令改变。其他 ZIP 成员相同。

## 对照验证

抽取实际生产 resetState、resetThreshold 与静态初始化字节码，使用 [Enjarify](https://github.com/Storyyeller/enjarify/tree/6364dfb30f7862873b84ec5fad1d1286c526ba0b) 转成 JVM 字节码执行；没有手写一份相似实现代替生产方法。隔离构造器及 Handler、MotionEvent 等环境为 stub，不能替代 Android ART 与真实输入分发验证。

120 项断言覆盖回调仍排队、已执行、已取消、从未排队、Handler 为空，两种 CUI 状态，以及重复清理、对象回收和阈值恢复。原版失败 30 项，候选 120 项全部通过。独立使用生产 `NativeAssets.apply()` 生成候选 APK，完整字节回读一致。详见 validation.json。

Windows，使用现有 JDK21、SDK dexlib2：

```text
python build.py <当前Launcher.apk> <不存在的构建目录>
python test.py <构建目录> <Enjarify源码目录>
python prepare_overlay.py <原始Launcher源APK> <构建目录> <原生动画资产目录> <不存在的组件目录>
```

## 原生集成与实机边界

曾离线准备的组件仅涉及既有 `r94-animation-v1` 的 launcher.recipe.gz、manifest.properties、bootstrap.sh，未纳入产品资产。source APK、设置和负一屏输出保持原样；沿用原协议的 AOT 完成标识。没有另建启动服务或永久临时挂载方案。

用户报告普通触摸和回桌面暂失效，多指缩小窗仍有效，随后恢复。现场未捕获完整失败区间，不能证明与此缺口存在因果关系。后续必须检查实际加载候选及正常、取消、多指接管等真实流程；实机验证前不得标记交互异常已修复。

本次已完成试装、现场复发和撤回。若重新研究，需要先证明输入消费者、阈值和清理动作的真实生命周期及故障因果，不能只沿用局部契约测试宣布修复。当前原 Launcher 为上述 bdd74 基线，原 v27 包与 r107 均不含此试验。
