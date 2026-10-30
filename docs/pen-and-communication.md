# 原生手写笔与通信共享

## 结构与来源

本地适配参考 ACLaniakea/coloros-pad-fixes 的既有思路，保留[来源和许可](../native-pen/NOTICE.txt)。执行方式转为framework事件桥、原IPeManager/WirelessSettings、init及精确代码生成；未把参考方案的LSPosed或别的设备内核模块整包照搬。

[native-pen/source](../native-pen/source/) 包含系统手势桥、会话/GATT/解析、DEX补丁与生成器。对应的init、bootstrap及缓存发布见 [native-pen/overlay](../native-pen/overlay/)。

## 笔首次生成：先修实际没有加载的代码

旧bootstrap只做verify-only，空缓存不会生成；换用旧生成模式又复现APK checksum differs。新的加载器用SHA校验过的片段和补丁精确重建字节，避开设备端ZIP重编码差异。两份文件全部校验通过后才发布/绑定，不发布一半。

测试曾覆盖主机与设备Java、shell域/UID0、重复执行、配方损坏与未知缓存。这说明生成器及发布条件有效，不等于真笔已连接。v22a/v22b又把专用目录标签和权限合入镜像，v23最终清刷验证软件ready状态。

## 现代BLE回调与状态

原IPeManager在Android13+回调里丢弃传入的byte[]，仍读旧characteristic值。修改为读取不可变快照，并补现代通知回调；拒绝过期会话和失败的服务发现。

GATT操作串行，读取/通知/指示、Lenovo充电状态与设备信息分开处理，有5秒操作超时、断连清队列。只有真实CTN730确认的MAC允许SPI书写笔不依赖BLE HID服务；仍要求真实配对和可读/可订阅服务。未知电量不伪装100%，缺充电信息不伪装“未充电”。

## 本机是CTN730，不是参考设备的GPIO

事件路径 `/devices/virtual/misc/ctn730`，缓存节点为：

```
/sys/class/misc/ctn730/attached
/sys/class/misc/ctn730/mac
/sys/class/misc/ctn730/charge_state
/sys/class/misc/ctn730/level
```

系统UEventObserver接收真实事件，再经受权限约束的接收器交原IPeManager。磁吸只说明硬件事件，不代表BLE已经连接。缓存读到Unknown/-1时保持未知，不猜私有命令，也不读取会切换触控IC模式的诊断节点来“验证”。

## 输入与按键

在PhoneWindowManager的systemReady和笔按键路径接入桥，输入观察器不抢夺书写或手指输入；识别笔设备及工具类型，不以宽泛vendor ID把键盘归为笔。单击、双击、长按接到原生广播与用户动作设置，并处理取消、灭屏、换用户与延时清理。

软件测试覆盖字节解析、畸形值、会话过期、七类按键时序与系统API契约；标志位只说明这些组件起来了。真实笔配对、压感/倾角、侧键、磁吸电量、充电重连和第三方绘画仍未实物验收。

## 通信后台退出不恢复

受控SIGTERM后，原通信中心15秒内不恢复。发现其init定义含oneshot；去掉这一行，保留原用户/组、接口、域和启动条件，约3.11秒观察到新进程、Radio/IMS会话重开。正常重启后同样测试也恢复。虚拟RIL原本可恢复，不做相同修改。

这是单后台服务恢复修复，不是手机数据/通话端到端结果，也不能推出所有拨号失败都由这一行导致。未增加一个重复常驻守护进程。

## 回到v17核对，避免越修越偏

用户提供反馈称v17能用通信共享移动数据，因此从实际v17分区提取关键文件逐一比对，而不是凭版本名猜测。

commcenterd、subsys_daemon、关键通信库、4.19用oplus_vnet.ko、默认脚本与OplusVirtualComm APK，共14份代码/载荷哈希相同。init差异只有上述oneshot删除。当前没有找到这些本机文件的回归证据，因此没有做臆测性替换。完整路径和SHA见 [communication-v17.json](evidence/communication-v17.json)。

本机4.19模块不能替换成附件5.10/6.1模块；未连手机时ovnet接口DOWN、peer为空和STATE_NOT_AVAILABLE不能单独当损坏证据。用户反馈还提到需保持平板Wi-Fi开启、断开路由器连接后共享手机流量；这是待复验的场景信息，不是本次端到端测试。

## 不要混同O+ Connect与手机通信共享

另一次电脑远控无法搜索，查到平板残留失效本机代理，清除后发现电脑并建立远桌，用户确认恢复。那是已验证的网络路径问题；它不证明电话/SIM/共享数据链也完成。遇到互联故障时，先查代理与真实对端链路，再考虑覆盖通信库。

未来需要真实手机记录配对/同账号能力协商、共享移动数据、拨出/来电、双向音频与短信的各自结果。不能用模拟SIM、强改能力标志或本机服务running来代替这些步骤。
