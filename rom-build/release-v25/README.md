# v25/r102 本地候选构建

新增后台冻结变体时，在 Windows 的 prepare.py 命令末尾加 `--freezer-fallback-r1`，并使用新的构建目录（本次为 `D:/TB371FC-release/v25-r102-freezer-r1-build`）。该选项同时选入已验证的 a592 框架 JAR 及匹配的 apply.sh/SHA256SUMS，保持默认动画修复，输出目录和ZIP追加 `-animation-default-r1-freezer-fallback-r1`。省略选项仍使用原 E73 框架闭环。原候选和既有ZIP不会被覆盖。

build_images.py 现在记录实际构建目录对应的 Windows 镜像路径；独立变体不会引用旧 `v25-r102-build` 的镜像。镜像回读、启动校验闭环、文件标签、e2fsck及归档成员校验仍由同一条流水线完成。完整包的验收范围以新构建结果为准，组件实机通过不能替代新包的首启或全部应用兼容验收。

2026-11-03：[组合变体记录](freezer-variant-20261103.json)对应的镜像、完整目录与ZIP已实际生成，154个成员的解压SHA/CRC及原离线入口通过。ZIP SHA256为 `fbd35f74b2e46dd54dc9ca4cf09c4f0b793d09527ff7376e4bb1d6e841483321`，7,485,231,035字节。该次构建没有修改平板；两项组件实机证据仍有效，新完整包首启和离线待机验收尚未完成。

基于已持有的v24整包及其独立逻辑分区镜像，合入已分别验证的r102 boot、充电查询兼容JAR、r91启动校验链和两处vendor启动规则。原分区布局、AVB载荷、7个刷机入口及其余系统载荷保持基线；不包含r100键盘候选。需要厂商闭源输入，本目录不是独立ColorOS源码。

Windows运行 `prepare.py <当前工作区> D:/TB371FC-release/v25-r102-build`，校验并复制精确载荷。WSL的TB371FC-Builder用 `python3 build_images.py /mnt/d/TB371FC-release/v25-r102-build` 在新副本上修改镜像、回读文件及原标签、核对启动SHA闭包和扬声器载荷、运行e2fsck。然后Windows运行 `package_rom.py <构建目录> <当前工作区>` 与 `archive.py <构建目录>`。

脚本保留当前实际工具与v24路径，并要求输出目录不存在，避免覆盖已有工作。离线核验调用原入口时不传Execute或CheckDevice，既不连接也不修改平板。不要把历史verification文件中其他版本的实机结论当作此候选的验收。

后续出厂动画默认值修正：新prepare计划含 `animation_default_r1=true`，在system_a的 `/my_manifest/build.prop` 生成第6个文件修改，将实际覆盖层的2改为4；原来仅写system默认4会被该层覆盖。新输出目录和ZIP追加 `-animation-default-r1`，原候选及原ZIP保留。旧计划不含标志时保留原镜像行为。当前设备单字段修正已重启验证4/实际加载4；该新变体的整包尚未构建、实刷或发布。

输出目录及ZIP均为本地候选，未发布。ZIP逐成员解压后复核SHA及CRC；原入口离线检查完成本身不代表双清首启通过。

2026-11-02已追加[实机记录](device-validation-20261102.json)：四份原候选镜像经无线暂存并核对完整SHA，使用设备现有TWRP 3.7.1_12-0，在系统逻辑分区未挂载时写入并完整回读；data格式化和metadata全分区清零回读通过。首启及Magisk初始化后一次普通重启均验证当前boot的原生脚本READY/rc0、root与Enforcing。该证据标识精确ZIP与镜像SHA，不修改原ZIP生成时的manifest或历史verification。

本机原fastboot首块USB下载仍失败，不能把TWRP安装成功写成原入口已恢复。清装后的Android单次11.6MB只读USB读取通过；不作为长期USB稳定性的结论。TWRP客户端对不支持的 `wipe /metadata` 曾返回0并输出错误，因此清理结果以实际分区回读为准，不能只看退出码。原包普通重启观测的默认等级2已定位为my_manifest配置覆盖；后续修正与原包验收分开记录。

首启若出现Magisk管理器下载提示，可使用包内 `assets/root/Magisk-v30.7.apk` 离线安装；该APK与本轮实机完整版哈希一致，不能将网络下载或升级当作刷入成功的必要条件。对应版本为30.7，本轮未执行在线升级。

真笔/键盘、配对手机、独立四声道听测、功率/充放电和长期可靠性仍需相应实测。设备暂存回退备份随双清删除；后续恢复使用电脑保留的v24整包或相应独立组件及现有Recovery。不要引用已删除的设备暂存路径。
