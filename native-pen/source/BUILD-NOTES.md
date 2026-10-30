构建目录结构已保留。JDK/SDK/NDK路径可调整为本机路径。
先运行work/pen-system/build.py与work/pen-v3/build.py；然后在source目录运行python work/build_pen_loader.py pen-v3/loader-v4 work/pen-v3/build，最后运行work/pen-v3/package.py。每次改源码重新生成配方，不复用哈希不同的loader缓存。
pen-loader-v2/build-result.json仅为模板旧哈希替换所需元数据，不是推荐的运行版本。pen-startup-module也是构建模板，最终版本由package.py输出。
两个极小只读挂载工具附带C源码与已编译二进制，重建示例：NDK clang.exe --target=aarch64-linux-android35 -O2 work/pen_mount_ro.c -o work/pen-loader-v2/pen-mount-ro；另一个同法编译work/pen-v3/pen_framework_ro.c到work/pen-v3/module/assets/pen-framework-ro。
新生成module目录中保留LICENSE/NOTICE并打包即为阶段性模块；原生ROM集成依据根目录README，不依赖该模块。
