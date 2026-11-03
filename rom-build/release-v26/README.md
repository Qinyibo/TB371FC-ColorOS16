# v26 / r104 本地升级候选

以已核验 v25 animation-default/freezer 完整包及独立镜像为输入。合入 r103 冻结退出修复、r104 既有死屏供电恢复路径修正和通用取消动画任务截图映射修正，精简六项推广预装。汽水由用户确认可用；无临时计时、异步统计或加载器试验。USB 未修复，黑屏 INIT 根因未确认。

依次运行 prepare.py <工作区> <不存在的构建目录>；在 TB371FC-Builder 运行 build_images.py <WSL构建目录>；Windows 运行 package_rom.py <构建目录> <工作区> 和 archive.py <构建目录>。保留旧包和源镜像，脚本不自行刷机。

输出 D:/TB371FC-release/R94T-v26-r104-20261103-CANDIDATE 及 ColorOS16_TB371FC_v26_r104_20261103_CANDIDATE.zip。镜像回读、权限标签、启动 SHA 闭包、原刷入入口和压缩包逐成员核验不替代实机。实机记录保存在当前工作区 outputs/v26-recovery。

2026-11-03 完成保留数据升级和四分区回读，原生启动、动画4、框架及桌面载荷通过。当前已恢复r104。16MiB随机文件的USB读取失败，无线同文件完整SHA通过；临时v23旧内核下相同USB测试亦失败。一次普通息屏亮屏未见驱动失败，异常恢复分支未触发，不能宣称根治黑屏。详见 device-validation-20261103.json，ZIP保持生成时原样。
