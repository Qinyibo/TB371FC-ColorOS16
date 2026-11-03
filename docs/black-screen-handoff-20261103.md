# 给 Grok 的当前接续：r107 已安装，黑屏起因未解决

最新新增：[五指收拢触摸／Home失效资料与并行任务](five-finger-input-20261104/README.md)。含有效正常对照、无效采集说明及待核对的异步清理路径。

当前运行内核的功能源码是 [`41082098d`](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/commit/41082098de91855a809239bf64f339a16d39effe)，完整接续分支为 [recovery-state-r107](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/recovery-state-r107)。不要只看仍停在 r104 的 kernel main。**hardware_success_claimed=false**。

## 已做什么，实际验证到哪里

r107 修正三个已证实的恢复契约缺口：dead 状态保留到 native UNBLANK/触控 REK 成功后；KMS 不再丢掉通知失败；完整 ON→ON modeset 即使 DPMS/FPS 相同也要提交触控就绪。合并通知不丢掉后续 active 故障的电源恢复资格。沿用 panel_lock/故障序号/sticky 合并，无新增重试线程、轮询、强开 IRQ 或伪造 REK。

35 项新增生产函数检查：r106 失败21项，r107通过；原35项回归也通过。完整 Image、配置/Module.symvers、启动镜像、分区完整回读和一次正常启动通过；原生 READY/退出0、Enforcing、触控 failed=0/IRQ1、原版 Launcher全局及进程命名空间核对通过。没有罕见故障恢复成功或长期稳定性结论。源码与可复现回归见 [r107 记录](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/recovery-state-r107/docs/tb371fc/late-readiness-r107)。

boot100663296B SHA256 `372004d3e4ad7985c58f9eade4961aa89a30ef8a5605e57e09eea0309e7129de`；Image SHA256 `bfe1eb72f48503560051b5307fa009431cf43c087fc34086130ed9112752e8ff`。回退 r106 boot SHA256 `899860494f70ec1b63241a9ebbd25946502bdb7e932558bc114632f908ae0920`。v27整包仍是r106，未重新打包。

## 新的自然故障证据

r106 自然黑屏：六次 INIT=0x9D 失败（含 GPIO/eng reset 重试）→ PANEL_DEAD / R97 sticky → R104 POWER_OFF/ON → 固件下载/INIT 成功 → native completion 的 REK 连续51次读到 `A0 D1 00 32 20` 后失败。后续一次普通唤醒仍相同；普通重启才恢复。见[脱敏现场节选](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/blob/recovery-state-r107/docs/tb371fc/late-readiness-r107/r106-natural-failure-excerpt.txt)。这是 INIT 失败和恢复后 REK 失败两个阶段，不能混为同一个错误，也不能将“下载成功”当触控恢复。

DLM primary-header与golden/result不一致在正常亮屏也存在；ILM和CRC标志通过，不再以此指认缓存损坏。0x9D/D1具体固件内部阶段没有厂家定义，不命名猜测。

## 供电所有权：需要共同复核的新重点

事实与边界见 [供电证据 JSON](panel-power-ownership-20261103.json)：

1. 实机 FDT 的触控复位GPIO56、IRQ68、面板复位69、TE66都有配置。`gpioinfo` 实际显示56由NVT-tp-rst持有且为output，69由reset_gpio持有且为output；不能再推断“根本没配置复位GPIO”。这不证明脉冲宽度/电气成功。
2. 主显示的 `vddio-supply` 缺失，启动明确报 `supply vddio not found, using dummy regulator`。主显示lab/ibb映射到PM8150L LCDB ldo/ncp。恢复日志和regulator框架调用不能证明真实触控VDDIO断电，禁止猜着借用secondary显示的L14电源。
3. 同一FDT声明KTZ8866 A/B均使用 HWEN54、ENP77、ENN78；当前源码没有这些GPIO属性的消费者，实机gpioinfo三条线均unused，描述符显示input。GPIOINFO只读驱动元数据，不能当作电压或实际引脚电平测量。
4. [`ktz8866b.c`](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/blob/41082098de91855a809239bf64f339a16d39effe/drivers/video/backlight/ktz8866b.c#L257) 的 `lcd_set_bias()`只有定义/导出/头文件声明，没有内核源码调用者。probe给0x09写0x9F；不假装这个函数已经在power_on/off运行。
5. [Kinetic官方资料](https://www.kinet-ic.com/uploads/web/KTZ8866/KTZ8866-04b.pdf) Rev04b的22/29页说明：0x09[0]=1时偏压由ENP/ENN控制，OUTP_EN/OUTN_EN位不负责开关。因此不能直接把现有0x9D→0x9F／0x99 helper接入后就声称有真实断电。0x0F故障寄存器读后清除；全量regdump需要保存首次值，第二次为0不代表从未故障。
6. 原机DTBO与9月20日备份SHA一致；未误改新的供电脚。实机ON命令表有88条（800B），包含厂家页配置及0x11/0x29，不是缺整个初始化表；DSC宽度在panel-count=2时有配对除2，未发现“每次亮屏无条件翻倍”的证据。CONFIG_DEBUG_FS未启用，不建议尝试挂载一个并不存在的GPIO调试节点。

**待验证推断：现有LCDB/dummy供电接口与真实KTZ偏压/触控供电之间可能没有建立正确的恢复所有权。** 不是已证实“LCDB完全没接线”，也不是已定位0x9D的唯一根因。此次只读核对，没有切GPIO、改电压、读清KTZ故障寄存器、刷补丁或做唤醒压力测试。

## 请 Grok 优先碰撞这三点

- 用同设备厂商/移植源码和实际DT资源确认真实LCD偏压与触控VDDIO的控制关系；区分“寄存器/供电框架对象存在”与板上确实由其供电。哪个节点/源码证据能反驳上述所有权缺口？
- 若ENP/ENN确实是正确恢复入口，先给使用既有regulator/pinctrl接口的最小接入方案：双KTZ共享HWEN单一所有者、正常休眠保电、失败恢复的顺序、错误回退和Bootloader状态接管。不直接抄别的平板GPIO号、延时或电压，不先加入新的重试服务。
- 继续解释“9D经原生恢复变INIT成功但REK=A0”这一现场链。另有PREPARE失败后立即unprepare、随后DRM再次disable/unprepare并报PLL -110的线索；clock请求失败的计数虽不自行回滚，后续unprepare可能释放它们，**尚未证明持久泄漏**。请针对同一次故障的真实资源所有权核对，别把它直接升级成根因或又堆时序重试。

## 独立的交互问题

普通触摸/回桌面偶发失效仍未根治。旧现场多指缩窗可用，不能归类为触控IRQ全死。Launcher resetState清理试验只有局部host/ART契约通过，实机仍有Home失败；UI套件在测试前因旧runner依赖缺失中止，其打印的OK无效。候选已撤回，原版bdd74已恢复；源码存放[已撤回研究](../research/input-lifecycle-r1/)，不进入产品资产或v27/r107。

本轮USB不再动，固定主板后置口；不重新测试已被用户接受的其他硬件功能。请回传源码证据、反例或明确缺口，不写hardware_success_claimed=true，不把r107或未落地的供电方案描述为黑屏已治愈。

下次自然黑屏可用[只读采集入口](../diagnostics/black-screen/)，已覆盖R107与REK/A0。不会自动运行、唤醒或重启；未验证下一次自然故障的完整采集。
