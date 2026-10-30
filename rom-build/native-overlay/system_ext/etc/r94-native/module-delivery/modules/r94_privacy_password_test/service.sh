#!/system/bin/sh
test "${0%/*}" = /data/adb/modules/r94_privacy_password_test || exit 20
test ! -e /data/adb/modules/r94_privacy_password_test/disable || exit 0
exec /debug_ramdisk/su -M -c 'nohup /data/adb/magisk/busybox sh /data/adb/modules/r94_privacy_password_test/runner.sh --ash >/dev/null 2>&1 </dev/null &'
