# API19 四扬旋转配套

此目录的 Java/JNI 已对齐实机 v0.29 配套：Java 保留 v0.24 通话归还确认与失败重试，JNI 保留 API19 控制接口形状检查和 #35–#43 内核兼容范围。启动监督脚本仍位于 `rom-build/native-overlay/system_ext/etc/r94-native/module-delivery/modules/r94_speaker_direction`。

2026-11-02 使用归档原始源码重编，三个产物均与实机逐字节一致：

| 产物 | SHA256 |
|---|---|
| direction.jar | d11f3cf3e9fb8739c1a25c2e48a5cd266a4f07a1d97fdf3b820d606bfe835add |
| direction.so | c32f9b49c8a1e4aadd06ea72bcefdc8283f321c71a06a14d7e0b4a705f4aa675 |
| directionctl | a4cdf0686a98d8dc455b3543b8bb71c27d3bef0b74d538c9741645ff67b7d679 |

在 Windows 使用 JDK21、Android SDK36 / build-tools36.0.0、NDK r30 构建，输出目录放在仓库外：

```powershell
python speaker/build.py --jdk 'C:/Program Files/Java/jdk-21' --sdk C:/android-sdk --ndk 'E:/TB371FC-ROM/工具链/android-ndk-r30' --out C:/temp/tb371fc-speaker
```

脚本仅构建，不安装、不重启服务。通话真实声音和方向听感仍需实机验收；四颗功放的 API19 应答不代表四个独立音源声道。当前旋转控制是在现有双声道输入间分配，未包含参考仓库的四路 DSP 矩阵。
