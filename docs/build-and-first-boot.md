# 构建、APK容器与首启：实际出现过的问题

## 构建输入与分区

v23使用经过核验的v22b私测镜像为输入，保持LP元数据与分区布局。最终修改system_a、system_ext_a及vendor_a；boot继续为 #43。README早先只写system/system_ext，漏写了vendor初始化服务域修正，现已更正。

| 分区 | 最终新增/替换内容 |
|---|---|
| system_a | oplus-services.jar；两份原生窗口配置XML |
| system_ext_a | SystemUI.apk；r91-rom/apply.sh；ROM与module-delivery两层SHA清单；delivery.sh |
| vendor_a | /etc/init/r91-rom.rc，将遗留KernelSU域改为现有Magisk域 |

精确输入/输出哈希见 [manifest](../release/v23/manifest.json)，逐文件替换见 [v23镜像记录](../release/v23/image-changes.json)。不是从公开仓库独立编译完整ColorOS；仍需自己持有对应的厂商输入。

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
