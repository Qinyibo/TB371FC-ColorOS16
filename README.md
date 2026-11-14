# 联想 TB371FC · ColorOS 16 移植

当前整包是 **v27 / r108 KB50 R5 候选版（2026-11-12）**，基于 `OPD2413_16.0.0.210(CN01)`，适用于已解锁、使用 A 槽的 Lenovo TB371FC（Bootloader 产品名 `spinel`）。仓库收录移植源码、内核补丁、打包脚本和刷入说明。完整 ROM 使用归档的刷机 ZIP，配套内核源码见 [android_kernel_lenovo_tb371fc](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc)。

- [R5 归档入口](rom-build/release-v27-r108-KB50-R5/INDEX.md) · [刷入说明](rom-build/release-v27-r108-KB50-R5/刷入说明.md) · [镜像与版本清单](rom-build/release-v27-r108-KB50-R5/manifest.json)。
- R5 将支持堆叠最近任务的桌面预置到系统镜像，在 vendor 中内置 Tinno 磁吸键盘与触控板配置，并预装相机。包内 Magisk 31.1 管理器按普通用户应用安装，首次打开可能提示重启以完成环境设置。
- **实机记录。** R5 已通过 Fastboot 写入 385 个 super 分片并清空数据。用户完成开机引导后确认首次进入桌面即可看到堆叠卡片。偶发黑屏无法唤醒及触控失灵仍缺少长期复测结果，R5 保留候选标记。
- B 站视频详情全屏规则单独提交于 R5 打包之后。见 [规则变更](https://github.com/Qinyibo/TB371FC-ColorOS16/commit/797a858695a64539bf6e0c8c732782265b8a5b46)。

## 历史维护版本

[v27 / r106 打包记录](rom-build/release-v27/README.md)、[v26 / r104 构建记录](rom-build/release-v26/README.md)和 [2026-11-03 维护记录](docs/maintenance-20261103.md)保留早期候选的构建与验收范围。[r107 黑屏交接和供电证据](docs/black-screen-handoff-20261103.md)记录了触控恢复与面板供电的排查过程。

## 历史唤醒候选（2026-10-31）

[wake-cache-r1 已刷入版本与审阅入口](docs/wake-cache-r1.md)：缓存首次校验成功的触控固件，保留正常恢复顺序。双击亮屏仍失败；用户反馈长时间放置后电源键正常亮屏，但未确认根因。原v23完整包没有替换。

## 开发记录与经验

此前维护构建入口为 [v25/r102](rom-build/release-v25/README.md)：以持有的v24镜像合入r102、充电查询兼容及两处vendor启动规则，保留原分区布局和刷机入口。四份候选镜像已通过现有TWRP离线写入、完整分区回读、双清首启及Magisk初始化后普通重启的原生启动检查；仍未发布。原fastboot大块USB传输在本机未解决，不能据此宣称原入口实刷通过。键盘候选未包含；硬件验收边界见[实机记录](rom-build/release-v25/device-validation-20261102.json)。公开v23及历史包仍按原始记录追溯。

后续已修正动画出厂默认被my_manifest覆盖为2的问题，单字段修正重启后加载4；另修复HANS未就绪时后台应用仅虚拟冻结的问题，真实应用冻结、广播解冻及前台服务生命周期通过。两项已生成独立 `animation-default-r1-freezer-fallback-r1` 完整候选，镜像回读、启动校验链、文件系统、原离线入口及154个归档成员校验通过。新包尚未整包首启，续航增益未量化；原v25 ZIP保持原样。见[新变体记录](rom-build/release-v25/freezer-variant-20261103.json)、[动画说明](native-animation/README.md)及[后台冻结修复](native-freezer/README.md)。

[完整阅读入口](docs/README.md)包含从早期八项修复、v16/v17首启故障到v23的经过，并说明为什么保留或撤回各条路线。

- [性能排障与失败试验](docs/performance.md)：窗口生命周期、GPU、绑核、GC、桌面手势与合成对照。
- [平行视窗与原生规则](docs/parallel-windows.md)：微信缩放、B站首页1149px和双窗保留。
- [构建与首启事故](docs/build-and-first-boot.md)：APK容器/对齐、EXT4标签、校验链及Magisk服务域。
- [原生笔/通信](docs/pen-and-communication.md)、[相机](docs/camera.md)、[内核/音频](docs/kernel-and-audio.md)、[界面适配](docs/ui-and-system.md)。
- [测量方法](docs/measurement.md)、[24组对照数据](docs/evidence/README.md)及[仍未解决的问题](docs/known-issues.md)。

历史试验代码放在[research](research/README.md)，不会自动进入发布构建。公开失败过程，是为了能复查和接续，不是建议把所有候选装一遍。

## 目录

- `native-pen/`：原生笔生命周期、BLE/GATT、系统手势桥接、补丁生成与init集成源码。
- `patches/`：本次SystemUI/B站框架修改脚本及微信/B站规则。
- `camera/`：相机 v7 修正与系统投放脚本。
- `baseline/`：当前安全键盘宽度、投屏Surface和原生系统资源补丁。
- `rom-build/`：实际镜像修改、校验链、首启和打包脚本。
- `flash/`：包内原始CMD/PowerShell入口；依赖完整发布包的镜像和配套工具，单独克隆本库不能刷机。
- `release/v23/`：完整包清单、哈希与本次实际测试结论。
- `docs/`：版本沿革、技术记录、数值证据与接续方向。
- `research/`：未保留候选的补丁源、采样配置与分析SQL。

## 构建与输入

脚本来自实际本地构建环境，Windows、WSL Linux、Python3、JDK21、Android SDK/build-tools36、smali/baksmali、e2fsprogs是相关依赖。保留历史绝对路径用于追溯，使用时按本机位置调整。v23以v22b镜像为输入，保留原LP布局，替换system/system_ext的列明文件，并修正vendor中的r91-rom初始化服务域；其余分区与 #43 boot保持原样。输入/输出SHA见清单。单独克隆本库并不能从零构建完整ColorOS系统。

ColorOS及联想原厂应用、framework、vendor和固件含闭源组件，本库不声称拥有或公开其完整源码。公开范围是已持有的内核及本项目可编辑源码、补丁与构建资料。原厂二进制需自行准备对应基线；本地签名私钥、账号、用户数据不上传。

## v23 历史测试范围

v23 完整包已通过实际双清首启及 Magisk 初始化后的正常重启；同一组代码的连续打断采样和用户手测通过，详见 `release/v23/TESTING.md`。残余掉帧、极端连续打断及偶发黑屏不宣称根治；真笔和配对手机通信共享需要对应硬件实测。

## 许可与来源

新增可编辑帮助代码和原生笔适配沿用GPL-3.0，见LICENSE；保留文件原有许可与版权。内核遵循其自身COPYING及各文件许可。原生笔方案参考 ACLaniakea/coloros-pad-fixes，commit 97a4024b875d22d3eea4d811da045765fd4388ed，见 native-pen/NOTICE.txt。厂商组件保持原有权属；不代表上游作者测试或认可本机移植。

## 待机唤醒更新

[查看 wake-r4 修复和验证情况](docs/wake-hardreset-r4.md)。
