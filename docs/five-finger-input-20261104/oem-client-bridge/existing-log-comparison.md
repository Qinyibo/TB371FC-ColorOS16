# 已有运行日志核对：没有故障窗 setter 证据

对应 Grok 对 a5f191c 的下一条区分建议。只读搜索已有三个日志文件；未操作设备、未开启常驻采集、未修改日志开关、未造故障。精确关键字命中数与原始文件 SHA（不上传私密全文）见 [existing-log-comparison.json](existing-log-comparison.json)。

- 23:29 事后日志：无 RecentsViewAnimUtil enabled/reason/call trace，无 WAM `setInputConsumerEnabled from launcher enabled=`，无 cleanup/空目标命中。它本来就不覆盖触发瞬间，不能因此断言无调用。
- 后续恢复日志：仅有23:34:40.699 ShellRecents `RecentsController.setInputConsumerEnabled: skip, cb?=false enabled?=false`。这是恢复后的另一条链，不能改写成故障时 OEM setter false 卡住。
- 23:54 正常对照：两次 manager cleanup 分别在23:54:14.198和23:54:18.435。无上述 setter 关键字或空目标/gesture-had-up 命中。配合已上传的两次Start/End，可确认正常cleanup进入；不证明故障时也进入。

日志可见性边界：实际接受版 [RecentsViewAnimUtil 方法](RecentsViewAnimUtil.md) 的 call trace 明确受 LogUtils.isLoggableDebug 条件保护，enabled/reason 使用 LogUtils.d。当前日志配置/封装可见性未证明；“没有该行”不等于“没有调用”。WAM也经过自己的logD封装，同样不能作反向执行证明。没有为收集这些行开启任何属性或修改系统。

**本轮没有可执行遗漏、没有修复 diff，hardware_success_claimed=false。** 静态材料与现有日志已查到此边界；不继续扩大无目标JAR扫描。下一条有效输入是自然故障发生时的现成输入分发/焦点/consumer与日志快照。用户报告后优先立即抓现场，不能再先问一轮操作、等恢复才采集；不要求重复五指、不主动熄屏、不重启。
