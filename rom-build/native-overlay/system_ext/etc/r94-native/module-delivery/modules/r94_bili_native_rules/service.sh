#!/system/bin/sh
set -eu
base=${0%/*}
bb=/data/adb/magisk/busybox
if test "${1:-}" != --locked; then exec "$bb" sh "$0" --locked; fi
test ! -e "$base/disable" && test ! -e "$base/remove"
test "$(getprop ro.product.board)" = spinel
state=/data/misc/r94-bili-native
test ! -L "$state"
umask 077
mkdir -p "$state"
exec 9>"$state/service.lock"
"$bb" flock -n 9 || exit 0
for i in $(seq 1 120); do test "$(getprop sys.boot_completed)" = 1 && break; sleep 1; done
test "$(getprop sys.boot_completed)" = 1
test "$(sha256sum "$base/rules.dex" | cut -d ' ' -f 1)" = f20c62a4c8715ca9005b02aaefa682d41610bbd0de2409e4cb353c898874a3f2
cp "$base/rules.dex" "$state/rules.dex"
chown -R 1000:1000 "$state"
chmod 0700 "$state"; chmod 0600 "$state/rules.dex"
chcon -R u:object_r:system_data_file:s0 "$state"
/debug_ramdisk/su -M 1000 -c 'CLASSPATH=/data/misc/r94-bili-native/rules.dex app_process /system/bin R94BiliRules /data/misc/r94-bili-native' >> "$state/service.log" 2>&1
