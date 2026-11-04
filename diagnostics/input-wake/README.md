# 电脑端只读日志环形记录

`record_until_incident.py --adb <adb.exe> --serial <设备> --out <不存在的目录> --minutes 120`

保存main/system/events/crash到电脑，8×4MiB环形文件。默认2小时，上限8小时；断线等待重连。SystemUI死亡记录或输出目录出现capture-now文件时，先冻结此前日志，再并行读取input/window/power/display/kernel/触控/退出信息，续存30秒后停止。创建stop文件可停止。

不发按键/触摸，不主动亮灭屏，不重启、不改属性/日志级别、不刷写。会有ADB读取开销；USB连接本身可能改变系统休眠条件，不用来验收离线续航。仅保存日志实际已输出的内容，不能恢复已覆盖日志或强行打开debug门控。只有日志环形保存持续运行；本工具不做周期性input/window快照，因此没有承诺捕获任意瞬间的输入状态。强触发仅覆盖已记录的SystemUI死亡，普通五指失灵需报告后立即标记采集。

数据只留本地，含应用/设备信息，不自动上传。时间戳/文件槽/触发前冻结目录一并保留。
