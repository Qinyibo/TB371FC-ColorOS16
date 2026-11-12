# v16 黑背景、状态栏和手势失效的原因

已在本机 HA1W0JA3 使用未改动的 v16 原始入口脚本，清除 userdata 和 metadata 后复现。刷写命令全部成功，完成初始化后屏幕全黑。`boot_completed=1` 仍不能作为验收通过。

首次扫描日志明确记录：

```
Failed to scan /system_ext/priv-app/SystemUI: No APK Signature Scheme v2 signature in package /system_ext/priv-app/SystemUI/SystemUI.apk
```

随后包管理器查不到 `com.android.systemui`，也没有该进程。因此状态栏和系统导航/手势服务缺失。这次故障不能归因为数据线、刷机者操作或触控硬件。

打包时重新生成 ZIP，丢失了原预装 APK 的 v2/v3 签名容器。SystemUI 的 targetSdk 为 36，首启包扫描要求至少 v2。之前的临时挂载试验利用了系统已经登记的包信息，未覆盖清空后的重新扫描，是验证遗漏。

v17 恢复与原 v15 预装包一致的证书容器。所有 ZIP 成员内容与 v16 相同，包括经典通知卡片布局 DEX、全部资源和八个原生库，原生库仍按 16KiB 对齐，配套 ODEX/VDEX 不变。没有降低 targetSdk、修改框架验签政策或改动分离式控制中心。

这是移植 ROM 的预装镜像修正，保留其原有受信任分区证书收集路径；不是重新生成厂商的合法签名，不能当作普通可旁加载 APK。实际首启验收结果以同目录 `physical-acceptance.json` 为准。

包保留 #38 内核、HWC 等待退让、WLAN 详情位置、四扬 0.25、AI 停用和前台调度。没有加入已取消的哔哩哔哩首页实验。通信共享、真实通话音频和其他机器上独立的触控/启动问题未因此关闭。

这次排查前发生过的 AutoLayout 缓存实验异常，以及早上的原生库对齐试验异常，均已恢复并被双清移除，不能用作 v16 整包故障原因；本次结论来自全新刷入 v16 的独立首启证据。
