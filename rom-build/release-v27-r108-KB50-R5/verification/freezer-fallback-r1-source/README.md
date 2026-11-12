# HANS 未就绪时交还 Android 缓存冻结

当前 TB371FC 的 4.19 内核不支持 HANS 所选的旧 Netlink 协议 29：实机只执行 socket/close 的探针返回 errno 93。HANS 服务停止，`sys.hans.enable=false`。原 `CachedAppOptimizerExtImpl.checkFreezeProc` 仍可设置 pending/virtualFreeze 并否决 Android 的冻结入队，造成缓存应用显示“虚拟冻结”而继续执行。不能把这个状态误判为 Handler 卡住。

修复只改这个方法的一处入口：HANS `isReady()` 为 false 时，复用本类原有的 permission-disabled 分支，把普通缓存进程交还 Android。没有修改全局权限开关。原有 quota 例外、HANS 就绪后的全部路径、Android 上层冻结资格和解冻方法保持原样；不增加服务或轮询器。这里使用的是现有 HANS 就绪判定，并非另行猜测守护进程状态。

输入固定为已含充电接口兼容修复的 E73 JAR，拒绝其他基线。Windows 需要项目现用的 JDK21、Android SDK dexlib2：

```powershell
python native-freezer/build.py <E73-oplus-services.jar> <新构建目录>
python native-freezer/prepare_overlay.py rom-build/native-overlay/system_ext/etc/r91-rom <新构建目录>/oplus-services.freezer-fallback.jar <新组件目录>
```

产物 JAR SHA256：`a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`。组件目录同时生成新的 apply.sh 和 SHA256SUMS，必须一起整合，不能只替换 JAR。模式、属主和 SELinux 标签见 component.json。生成工具只写新目录，不直接修改镜像或设备。

2026-11-02 已在 r102 内核上完成组件安装和一次正常重启：当前启动原生组件 READY/exit0，root/Enforcing 和动画等级4保留。完整 DEX 语义比较共49,753个方法，仅目标方法变化；独立 ART 的12个用例及后端丢失转换通过。真实测试应用进入缓存后停止执行，广播使同一进程解冻并再次冻结；前台服务持续运行，停止后约21.69秒恢复缓存冻结。原采样曾被 Athena 开机清理打断，另一次采样早于实际冻结；均保留原始失败记录，没有用修改产品时序来满足测试。

摘要见 [validation-20261102.json](validation-20261102.json)。测试应用已卸载。没有进行真消息推送、媒体等多应用兼容验收，也没有测得离线待机续航改善。基本 Binder/cgroup 合约通过不代表所有新 Binder 特性都已支持。

原 v25 镜像、ZIP及 E73 基线闭环保持不变。本组件已接入 release-v25 的可选 `--freezer-fallback-r1` 构建入口：同时选入这三个文件，保留动画默认值修复，输出新的独立变体。镜像回读、文件系统和归档完成状态见该次构建结果；新完整包尚无首启或全部应用兼容验收，不能沿用原 ZIP 的实机结论。

本次设备回退文件只备份一次，位于 `/data/local/tmp/r94-freezer-fallback-r1-20261102/`。rollback.sh 恢复 E73 JAR、原 apply.sh、原 SHA256SUMS，逐项校验并恢复只读挂载；恢复后需要正常重启。不要对其他版本沿用该脚本。当前候选保留待后续兼容验收；源代码、参数和内核没有顺带扩改。
