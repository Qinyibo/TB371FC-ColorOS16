# 旧充电 HAL 的可选查询兼容

本机 ODM `ICharger` 为 V3，冻结事务表为1至126；ColorOS V9 Java代理的 `getChgConfig()` 使用事务128。原电池服务每次收到电池更新都重复发送不支持的事务，捕获异常后返回已有字符串 `-1`。

补丁仅在 `OplusBatteryServiceFeature.getChgConfig()` 的实际调用前查询接口版本。V3及以前直接返回已有未知值；更新接口继续原调用、原参数和原异常处理。版本读取沿用现有Binder代理缓存，连接替换后使用新代理，不新增永久失败状态。没有假定V4已经实现此方法，V4及以上仍保留原有异常回退。没有更改通用AIDL代理、充电控制、阈值或任何遥测值。

`ChargerCompatPatch.java` 为DEX源码补丁器。`build.py <原始oplus-services.jar> <输出目录>` 使用Android SDK cmdline-tools中的dexlib2、Java21及Python3；默认路径与本项目已有构建工具一致。输入严格要求当前已适配的 `ab25a362…30467`，不会覆盖其他版本。输出保留其余ZIP载荷，原有窗口、显示、笔和通信适配必须保持。需要将输出JAR放进system镜像，并更新当前r91启动脚本对应的精确身份和校验清单；历史发布包记录不随此修改。

`ChargerCompatTest.java` 用动态假HAL运行真实补丁方法，绕过会连接真实设备的构造函数。已在平板ART验证七类输入与临时失败，并在完整DEX的49,753个可执行方法中确认仅此方法指令/捕获表发生变化。隔离测试不代替system_server实际加载验证，也不代表真实充电、快充或续航验收。
