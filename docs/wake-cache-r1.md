# 2026-10-31 · 已刷入的 wake-cache-r1

这是v23之后单独更换boot的唤醒候选，不是新的完整ROM。公开的是当前已刷入版本，尚未完成的后续双击调查没有混入源码。

**最新反馈：双击亮屏仍然失败；较长时间放置后电源键正常亮屏，暂不能认定长待机黑屏已根治。**

## 代码与材料入口

- [内核本版完整说明与审阅重点](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/blob/wake-cache-r1-20261031/docs/tb371fc/wake-cache-r1/README.md)
- [本版内核完整源码](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/tree/wake-cache-r1-20261031)
- [相对上一版公开源码的完整差异](https://github.com/Qinyibo/android_kernel_lenovo_tb371fc/compare/9bed5276d6526438208cd488b71292a725b68d4d...wake-cache-r1-20261031)
- [构建/刷入结果及用户反馈](../release/wake-cache-r1/validation.json)

改动只有触控固件引用缓存与只读状态记录，涉及nt36xxx.c、nt36xxx.h、nt36xxx_fw_update.c。首次成功校验后复用文件数据，后续仍完整下载并经过原有CRC/INIT/REK和面板恢复顺序。工厂测试固件不替换正常缓存；初始化失败、移除和关机时释放。

现有#43配置与驱动导出接口保持相同，boot保留原ramdisk、DTB及其余载荷。没有动微信/B站平行视窗、B站首页宽度、144Hz、现有框架和流畅度设置；没有双清，也未重新打包v23完整ROM。

完整内核编译、12项ASan/UBSan函数测试和boot载荷核验通过。已刷入、正常启动、root可用，一次短时软件唤醒命中缓存，文件请求计数仍为1。

实机双击复现没有收到有效手势上报，计数仍0；当时手势、IRQ与IRQ Wake均开启，Hall为开，PM超时为0。该证据还不能区分芯片未产生手势中断和包读取/解析未通过，因此不能直接把问题归为Android拦截按键。

较长待机后的电源键恢复是用户实际反馈。未严格记录待机时长和USB/深睡条件，读取时成功深睡计数为0，所以这部分与受控长待机验收分开记录。

## 产物指纹

- Image：58ffeb6e5776d622bd45f917bae4760c4fbb34229506a68e9df28b9769c8a0de
- 本版boot：8e0a355571cfdc04b749906b1056189fa94937d0e10f4d6f6e072a2c96a8cb8a
- 原版回滚boot：09d3c1bd67946575de8b0dad434f651e746747da2686fa227719142ad47cfbbe

构建时状态见build-receipt.json，其中“未刷入”仅描述打包当时；validation.json和本页补充刷入后的状态。旧v23完整包及原有发布标签没有替换。
