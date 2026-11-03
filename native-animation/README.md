# 原生动画双档

出厂默认配置修正 animation-default-r1（2026-11-02）：原v25只在 `/system/build.prop` 写入4，实机OEM init随后按扩展目录顺序读到 `/my_manifest/build.prop` 的2，覆盖了前值；用户确认没有选过动画风格，且该属性没有持久化选择。`patch_default_property.py` 对已核验的原始my_manifest属性文件只改默认项2→4（1字节），不改框架、APK、运行时属性或开机脚本。当前设备在没有保存动画选择的条件下重启，期望和实际加载等级均为4，原生启动READY/rc0。用户以后保存的选择仍由原有属性机制处理。

release-v25的prepare现在生成 `animation_default_r1` 标志，镜像构建沿用原有文件权限、属主、SELinux标签及回读检查。新包目录和ZIP追加 `-animation-default-r1`，不覆盖原v25及其验收记录。旧计划不带此标志时保留原镜像行为。本修正已完成单字段实机验证；2026-11-03已与后台冻结修复合成完整候选，通过镜像及归档检查，见[组合变体记录](../rom-build/release-v25/freezer-variant-20261103.json)。该新包尚未重新双清首启，不能沿用原v25的整包通过结论。

设置 → 显示与亮度 → 屏幕刷新率下方的“动画风格”：

- 动画质量：原 2 档。
- 动画流畅：4 档，恢复堆叠后台所需的原生过渡时序及卡片点击间隔。
- 两档的负一屏背景统一使用高质量壁纸模糊分支（背景 GPU tier 3）；其他卡片、动画能力判断保持原样。此前将两档设为低质量纯色背景的版本已被用户否定。
- 堆叠后台的停留判定上限为 120 毫秒；流畅档进入堆叠后台的 700 毫秒过渡缩为 280 毫秒，质量档保留原过渡时长。补齐后台控件的原生过渡分支。
- 桌面上滑采用独立的 SwipeToRecentMotionPauseDetector，其覆盖 addPosition 后没有沿用基类的静止超时。流畅档堆叠布局补上原生 Alarm 的 120 毫秒静止判定，仅在有效上滑区域内计时，手势清理由原生 clear 取消计时；质量档保持原判定。
- 四档启用堆叠时，OplusUiFactoryInjector 创建系统现有的 SwipeToRecentTouchController，与二档保持同一手势入口；原先四档的 FlingAndToggleTouchController 是简化后台路径。保留系统原生的堆叠动画和收尾流程。已删除横滑开始/结束时补写状态、重置位移的候选兜底及全部自定义反射诊断。
- 四档的图标打开/关闭过渡按原生曲线放慢 25%，窗口、桌面缩放及透明度保持原时序比例；二档不受这项时长调整影响。
- 取消 Assistant 对平板 4 档的禁用判断。原系统 APK 也同步修正该判断，防止启动覆盖代码加载前就把负一屏开关关闭；用户仍可手动关闭负一屏。
- 设置行、单选弹窗、重启提示均使用当前 Settings 自带的 COUI 控件。切换后重启生效。

`source/work/animation-modes` 包含 Java 补丁器、运行代码和构建脚本；原系统 APK 不在这里重新分发。三个输入的精确 SHA-256 见 overlay 内 manifest.properties，未覆盖的原始 AssistantScreen 身份见 assistant-boot-patch.json。将原版 Launcher、Settings 与已适配的 AssistantScreen 放到 build.py 指定位置，原始 AssistantScreen 放到 inputs/AssistantScreen-stock.apk，用 Android SDK 36、Java 21 执行 build.py、build_boot.py（需要 androguard），再执行 build_native.py 生成原生镜像覆盖文件。build_boot.py 只改一个方法，APK 大小及其他 DEX 偏移不变，精确变化为 63 字节；字节补丁也已公开。

覆盖文件已同步到 rom-build/native-overlay。生成的 my_stock/app/AssistantScreen/AssistantScreen.apk 也必须放入 system_a 镜像根目录对应位置；仅更新晚期挂载会遗漏启动禁用问题。APK 和 bootstrap.jar 是本地生成文件，仓库默认忽略，构建脚本与配方保留。现有 r91 原生启动服务完成基础适配后，顺序调用新 bootstrap；不新增 Magisk 模块。缓存按 APK 身份生成，目录只读挂载，清除旧负一屏 ART 挂载后完成三包 speed 编译；不清除应用数据。原服务的基础身份判断及自身校验清单同步更新。

手势测试不能用自动注入未复现代替用户反馈。前期错位候选被用户否定；加入横滑边界回填后用户一度回复正常，随后仍反馈错位并突然拉回。回填与反射诊断已完全撤销，但用户仍能在四档复现；切到原生二档对照则回复“二档正常”。查源码确认四档在 OplusUiFactoryInjector 中原本创建 FlingAndToggleTouchController，而二档创建 SwipeToRecentTouchController：此前仅开放堆叠显示能力，没有同步完整手势入口。当前版本在入口处选择系统已有的完整控制器，不做滑动后的几何补偿。第 27 版已加载并完成 speed 编译，运行记录确认 SwipeToRecentTouchController 负责手势与原生堆叠状态切换；用户快速左右滑后台卡片后回复“现在正常了”。图标放慢后的速度也已获用户认可，保留当前四档版本。 随后用户反馈重启后堆叠消失，重新加载桌面后已观察到堆叠恢复；bootstrap 增加在绑定与编译完成后重新加载桌面，避免加载期间启动的进程沿用旧代码，重启验证结果另见项目记录。此轮确认不代表已经排除所有间歇问题。未重新打包发布，也不包含待机黑屏内核变更。

桌面停顿的早期候选有过一次 VerifyError（MotionEvent 参数在方法尾被原代码复用为 Float），已改为方法入口读取并验证加载。稳定桌面的旧注入测试没有触发 SwipeToRecentMotionPauseDetector，不能将其作为手势判定的有效对照；现在已找到四档控制器选择差异。

图标动画帧率：本机 144Hz 设置下采集三次桌面点击打开便签的 FrameTimeline，预期动画调度约 6.94 毫秒一帧；部分窗口缩放区间实际约 13.9 毫秒更新一次（约 72 帧），伴随 SurfaceFlinger GPU Deadline Missed / Stuffing。并非当前流畅档固定锁 60 帧，但不能把屏幕 144Hz 写成动画稳定 144fps。此次仅诊断，没有修改刷新率、内核或图标动画帧率策略。

## 当前集成状态（2026-11-03）

v26/r104 已集成上述默认值、冻结修复和通用取消动画任务截图映射修正，完成保留数据升级和正常开机；精确整包双清首启尚未完成。用户确认汽水收纳效果可用，停止专项优化。历史计时、异步及加载器试验不进入当前构建，黑条由用户手测。见 [v26 记录](../rom-build/release-v26/README.md)。
