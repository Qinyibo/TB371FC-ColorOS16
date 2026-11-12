# TB371FC 通信与原生笔集成源 v0.4

这是指定系统版本的 ROM 覆盖层与源码，不是可刷固件。本轮已在当前平板用两个一次性启动模块部署同一套软件内容并通过正常重启；尚未重新打包完整ROM、刷分区或清数据。不存在真笔/手机联测通过记录。

集成目标：spinel / TB371FC / SM8250 / SDK36，增量 V.2e733a1-dda927-df323a，实际内核4.19.325-perf+ #39。本覆盖层不带内核，不适配附件5.10/6.1模块，不改变已验收的其他功能。

1. 将 overlay 合并到原ROM工程。services.jar必须基于 manifest.json 所列 base_sha256，其他版本必须重新定点适配，不能盲覆写。
2. 保留原签名 IPeManager.apk 和 WirelessSettings.apk 用于包管理器首次扫描。补丁资源在开机完成后从原APK精确复原生成代码，再只读绑定；不要把生成APK当签名原包直接替换。
3. 以本包同名 r94-pen-native-v1.rc 替换旧文件，不能并行保留旧v1/v2/v3启动服务。资源root:root，目录0755，文件0644，system_file标签；由/system/bin/sh执行脚本无需文件可执行位。
4. 把 integration/file_contexts.append 合并入既有标签源并重新编译标签数据库，不能替换整个file_contexts。init创建root拥有的专用缓存，避免/data/local/tmp可由shell重命名的问题。
5. vendor侧只删除当前r94-commcenterd服务的oneshot一行，保留其余用户/组、接口、seclabel和启动条件，交由init恢复异常退出。虚拟RIL无需同类修改。
6. 正式原生集成后停用 r94_pen_bootstrap_v2 与 r94_commcenter_recovery 两个阶段性模块，避免重复挂载；系统服务直接读取框架新代码，init完成一次生成与挂载，无LSPosed，无Root常驻轮询。
7. 正常锁屏重启不读取用户凭据、不绕过解锁。USER_UNLOCKED原生接收器会启动已有CoreService；开机阶段不假装应用已在凭据加密存储可用前运行。
8. 使用原工程打包和包内原始刷写脚本。此覆盖层的完整首启、升级、禁用回退、SELinux标签集成仍需ROM验收，本轮没有执行这些刷写步骤。

源码在 source/；保留基线APK、services.jar和原始补丁工具，故本包较大。JDK21、Android SDK36/build-tools36.0.0及NDK r30为构建依赖。先运行source/work/pen-system/build.py、source/work/pen-v3/build.py，再运行source/work/build_pen_loader.py pen-v3/loader-rebuilt <新APK目录>。构建脚本中的SDK/JDK路径可按实际位置调整。不要复用已有hash不同的生成缓存；APK封装时间可导致重建文件哈希变化，需同时更新配方与manifest。

对应新源码参考GPL-3.0上游，保留LICENSE与NOTICE；原厂系统文件保持其原有权属。
