# ColorOS16 TB371FC v27 / r108 KB50 R5

当前候选是 `ColorOS16_TB371FC_v27_r108_KB50_20261112_R5_CANDIDATE`，系统基线 `OPD2413_16.0.0.210(CN01)`。本目录只收录打包脚本、刷入说明、校验清单和内核补丁，不收录 ROM 镜像、super 分片、boot 镜像或工具二进制。完整刷机包请使用本地 outputs 或网盘中的 ZIP。

根据用户在 2026-11-14 补充的实机反馈，堆叠卡片、偶发黑屏无法唤醒和触控失灵均已修复。用户在 R5 清刷后首次进入桌面时已确认堆叠卡片可用。下方镜像清单保留打包时的验证状态。

- 刷入步骤见 `刷入说明.md`
- 镜像校验和内核标识见 `manifest.json`（内核 `#50 r108-force-rek-keyboard-bias-wake-idle-ab`）
- 键盘补丁见 `verification/0001-TB371FC-restore-native-keyboard.patch`
- 打包脚本见 `packaging/`
- 开源仓库：标准包 https://github.com/Qinyibo/TB371FC-ColorOS16 ；内核 https://github.com/Qinyibo/android_kernel_lenovo_tb371fc
