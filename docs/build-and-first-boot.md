# 构建、APK容器与首启：实际出现过的问题

## 构建输入与分区

v23使用经过核验的v22b私测镜像为输入，保持LP元数据与分区布局。最终修改system_a、system_ext_a及vendor_a；boot继续为 #43。README早先只写system/system_ext，漏写了vendor初始化服务域修正，现已更正。

| 分区 | 最终新增/替换内容 |
|---|---|
| system_a | oplus-services.jar；两份原生窗口配置XML |
| system_ext_a | SystemUI.apk；r91-rom/apply.sh；ROM与module-delivery两层SHA清单；delivery.sh |
| vendor_a | /etc/init/r91-rom.rc，将遗留KernelSU域改为现有Magisk域 |

精确输入/输出哈希见 [manifest](../release/v23/manifest.json)，逐文件替换见 [v23镜像记录](../release/v23/image-changes.json)。不是从公开仓库独立编译完整ColorOS；仍需自己持有对应的厂商输入。

## v26/r104 维护候选（2026-11-03）

[当前构建入口](../rom-build/release-v26/README.md)继承已核验的动画等级4与冻结回退变体，加入 r103 冻结退出修复、r104 既有死屏供电恢复条件修正、通用取消动画任务截图映射修正，并移除六项推广预装。

精确 v26 镜像已完成 TWRP 保留数据升级、四分区完整回读和正常开机。未完成精确 v26 整包双清首启及完整 fastboot 刷入，不能套用下文 v25 验收。USB 与偶发黑屏无法唤醒仍是严重已知问题。身份与范围见[维护记录](maintenance-20261103.md)。

## v25/r102 本地维护候选（2026-11-02）

[构建脚本](../rom-build/release-v25/README.md)以已核验v24镜像的新副本为输入，只替换system的充电兼容框架、system_ext的r91脚本与SHA清单、vendor的无线诊断及工厂服务启动定义，并使用已实机验证的r102 boot。原LP布局、AVB载荷、7个刷机入口和其余分区/文件载荷保留基线。旧整包仍含r6及旧框架，不能用旧文件重装后期待本轮修正继续存在。

已完成5个文件的回读、权限/属主/SELinux标签、原生启动SHA闭包、扬声器原载荷和过期框架伴随文件检查，三个修改镜像的e2fsck通过；super内每个逻辑分区与清单哈希相符。原离线入口通过，调用时没有Execute/CheckDevice，不连接或修改平板。149个ZIP成员解压后分别通过SHA及CRC，候选约7.49GB。

上述是构建阶段的离线记录。随后实际使用无线暂存镜像和设备已安装的TWRP 3.7.1_12-0，在系统逻辑分区未挂载时写入super、vbmeta_a、vbmeta_system_a、boot_a；四个完整分区的回读SHA与候选一致。data格式化、未挂载metadata全分区清零及回读校验通过。首启完成引导后，当前boot的原生脚本READY/rc0；Magisk初始化后再普通重启，新的boot记录也READY/rc0，root与Enforcing保留。[实机记录](../rom-build/release-v25/device-validation-20261102.json)按候选ZIP的SHA标识这次载荷。

原fastboot入口在本机的首块USB下载仍失败；Linux小块RAM传输成功不足以保证整包可靠，未将这条路径记为通过。清装后的Android单次11.6MB只读USB传输大小和SHA正确，但不证明间歇问题消失，也不能据此解释引导器故障。本次Android读测没有写入分区或修改驱动，未将数据线判为根因。

候选ZIP和原七个入口未被改写，包内manifest仍保留生成时的 `OFFLINE_VERIFIED_DEVICE_PENDING`；后续实机证据单独追加，ZIP仍未发布。真笔/键盘、配对手机、独立四声道听测、功率/充放电和长期可靠性尚未验收。原包普通重启的默认等级2随后已定位为my_manifest配置覆盖，并完成单字段修正启动验证；见[动画说明](../native-animation/README.md)。新完整变体尚未构建或重新双清，原包与修正验证不能混用。设备暂存备份随双清删除，后续回退须用电脑保留的v24整包或对应组件镜像。

## 两种不同的SystemUI包装失败

v16的问题发生在预装首次扫描：缺少APK v2签名容器，SystemUI没有登记，最终黑背景、状态栏和手势不可用。已有数据环境热替换通过，不能覆盖首次安装路径。

后续触摸层试验第一次包装又遇到原生库偏移变化：替换DEX使stored .so的ZIP数据偏移错开632字节，SystemUI报 `UnsatisfiedLinkError`。这轮是包装失败，不应拿失败运行的帧数据评价算法。重新封装时保持未改成员、校验CRC/DEX头，并补齐偏移差，使本机所需的4096对齐成立。

早期部分笔APK又曾按16KiB要求验证。**ZIP entry对齐、ELF段对齐、设备实际页大小是三个相关但不同的检查**，不能把其中一个通过写成所有环境兼容。参考[Android页大小与打包说明](https://developer.android.com/guide/practices/page-sizes)。

保留原签名块不意味着DEX改变后仍有OEM完整内容签名。本项目依靠指定可信系统分区的预装路径做了实际首次扫描验收；不能把这个SystemUI当成普通可侧载APK，也没有关闭系统签名校验作为通用修复。

## 编译伴随文件与原生标签

更改APK/JAR时，旧odex/vdex/art/profile可能不再对应新DEX。v23仅移除两个已改文件的过期编译伴随产物，让ART生成匹配代码，不清全系统缓存，不套用其他包的OAT。

debugfs替换EXT4文件会创建新inode，要回填root属主、0644及原security.selinux字节；不是拷贝文件就算完成。修改后回读文件、核对两层SHA清单，再做 `e2fsck -fn`。这里只改自有构建镜像，原基准保留。

Windows Python默认编码曾把“使用说明.md”转坏，导致SHA清单引用不存在的路径。已改成显式UTF-8并按镜像内容回读校验。中文路径错误可以表现为首启脚本中途退出，不能一律归成权限问题。

## 首启校验链的遗漏

原生r91-rom脚本对framework检查精确SHA。框架加了B站宽度改动，但旧SHA仍在，出现 `R91_ROM_BASE_GUARD_FAILED_4`、EXIT1，后续默认初始化没有完整执行。

修复不仅是改一个常量，还更新本层SHA、引用delivery.sh的外层SHA和delivery自身清单。最终日志要真正走到 `R91_ROM_READY`、`R91_ROM_EXIT rc=0`，不能以某个前段“身份核验通过”替代整个服务完成。

桌面按一次性标志做 `cmd package compile -m speed -f com.android.launcher`。原后台dexopt使用speed-profile，不新增全机强制编译或每次开机重编。编译状态以设备实际 `pm art dump` 为准；ART策略含义见 [ART Service](https://source.android.com/docs/core/runtime/configure/art-service)。

## 首启通过、重启却失败的服务域

第一轮v23实刷首启正常；Magisk管理器初始化后再重启，r91-rom甚至没有产生新boot.log。dmesg显示：

```
cannot setexeccon('u:r:ksu:s0') for r91-rom: Invalid argument
Service 'r91-rom' ... received signal 6
```

服务定义还保留KernelSU域，而环境已是Magisk。最终改 `/vendor/etc/init/r91-rom.rc` 的seclabel到已有 `u:r:magisk:s0`，其他用户/组/启动条件不改。它仅适用于当前已带Magisk的包，不是无Root ROM通用域。使用不存在域时，在执行脚本前就会失败，脚本内的重试修不了。

修正后把vendor重新纳入super，重新生成最终ZIP，再实际双清、完成引导、初始化Magisk并正常重启，两个启动周期都验证READY/rc0。该机制的定义见 [AOSP init文档](https://android.googlesource.com/platform/system/core/+/refs/heads/main/init/README.md)。

## 原生笔生成的目录与权限

原厂签名应用先扫描，再按精确配方生成已修改代码并绑定；不是直接把不能正常首次扫描的修改APK塞进去。专用缓存用可信属主，生成在两份校验通过后一起发布。v22b修过077继承下的目录0755/文件0644、ipe/ws子目录的system_file标签，同时保留父目录原标签。

测试“旧系统已存在缓存”不等于冷生成；冷生成也不等于完整双清。最终包分别验证，避免把阶段性成功写成全部首启链已闭环。

## 刷入与打包后的记录

原七个CMD/PowerShell入口逐字保留，按文件核验、连接、刷前检查、清空刷入执行。fastboot product应为spinel；Android供体属性可能显示OPD2413，不能据此判断连错硬件。原流程检查解锁、A槽、分区容量、电量，再写super/vbmeta/boot、清userdata/metadata并重启。

包中manifest刻意保留打包当时的pending状态，实际清刷发生在ZIP生成后；最新实机结论在[最终验收页](../release/v23/TESTING.md)与[运行摘要](evidence/v23-runtime.json)。不能为改一个说明字段重新发一份哈希不同却没刷过的ZIP冒充同一包。
