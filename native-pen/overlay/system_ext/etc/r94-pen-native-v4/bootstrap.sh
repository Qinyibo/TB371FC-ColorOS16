#!/system/bin/sh
set -eu
assets=/system_ext/etc/r94-pen-native-v4
cache=/data/local/r94-pen-native-v4
setprop debug.r94.pen_v4_ready 0
export CLASSPATH="$assets/bootstrap.jar"
/system/bin/app_process /system/bin org.tb371fc.pen.NativePayloadV2 "$assets" "$cache" >"$cache/bootstrap.log" 2>&1
setprop debug.r94.pen_v4_ready 1
