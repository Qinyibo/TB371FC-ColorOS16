# 本次保留的系统修改

SystemUI：FullscreenCaptionHandleViewHolder 辅助触摸窗口延后400ms创建；失焦、隐藏和销毁时取消待创建任务。保留已有窗口拖动行为。脚本位于 work/，先用 smali/baksmali 拆解自己持有的原厂 classes2.dex，再运行补丁和封装。原厂 APK 不在源码库内，首次扫描与签名策略取决于完整移植基线。

oplus-services：CompactWindowBoundsCalculator.calculateBoundsInPosition 中仅 B站居中首页路径使用1.6比例；左右双窗路径保留。原始JAR SHA256 7ea250fb0b7b00830a48b6ad111c795dc3adfcbb0d7b8c5a261f63d309b29762；本包输出 ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467。

native-window-rules.json 是微信/B站的原生配置目标。合并到自己持有的对应 sys_fantasy_window_managed / sys_full_orientation_managed XML，更新内部版本与校验。仅替换列出的应用；不要复制其他用户的运行时数据库。ROM构建将配置放到 /my_product/etc/fantasy/，不默认运行旧B站规则模块。

这些脚本记录实际改动，不是跨版本通用补丁；历史脚本中的机器路径需按本机输入位置调整。未接受的调度、GPU、GC和桌面实验不包含在本次有效修改里。
