# v27 / r106 完整候选包

以精确 v26/r104 完整包目录及当前已刷入的 r106 boot 为输入，只替换 boot 分区镜像。super、vbmeta、vbmeta_system、原七个 CMD/PowerShell 入口和所有现有体验保持对应字节与哈希。原包与已有产物不覆盖。

Windows / Python 3.11+：

```text
python package_rom.py <工作区> <不存在的构建目录> <v26包目录> <不存在的v27包目录>
python archive.py <构建目录>
```

输出 `ColorOS16_TB371FC_v27_r106_20261103_CANDIDATE.zip`、同名 `.sha256` 和 `.validation.json`。执行原离线入口核验、归档逐成员 SHA/CRC 和完整 ZIP 哈希。仅打包，不操作设备。

r106 源码功能提交 `4b397325943e70d3dbaaff63b5f622ab48668d62`，维护记录提交 `5920918c017ded5440f2a974956b21cf02cdb0f2`，分支 `recovery-state-r106`。35 项源码回归、内核构建、配置/Module.symvers 对照、实机 boot 分区回读和正常开机已通过。没有增加 Gemini 建议的状态写入或新复位实验。

USB 使用已验证的主板后置口。双向 16 MiB 和 fastboot 刷入同版 96 MiB boot 通过；完整 ROM 脚本尚未重测。黑屏 INIT=0x9D 根因未修，异常恢复未实际触发；用户正常使用观察。现有整包未完成双清首启验收，保留候选标识。

打包期间用户报告普通触摸与回桌面暂时无响应，当时四指或五指缩小窗仍有效，之后恢复。未重启、重刷或重启系统界面。现场快照 DispatchEnabled=true / DispatchFrozen=false，驱动自报 awake=1 / failed=0，不能据此证明故障期间普通触摸正常。后续采集记录了有效多点事件和 IRQ 增长，覆盖恢复阶段；未获得整个失效过程，不能认定硬件全失灵或确定窗口拦截根因。见同目录 known-issues.json。用户游戏期间停止设备操作。

回退内核使用保留的 v26/r104 boot，SHA256 `f29c32c15c7276d777f243a322ca35495099c25d6e41e402dd4eacb77121f85b`。清空数据刷入入口会删除用户数据，须先备份。
