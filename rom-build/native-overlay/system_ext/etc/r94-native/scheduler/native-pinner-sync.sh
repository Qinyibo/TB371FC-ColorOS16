#!/system/bin/sh
# Reconcile native Pinner with the actual launcher after late deployment.
# No extra pinning daemon, quota override, APK/cache replacement or restart.
set -eu
export PATH=/system/bin:/system/xbin:/debug_ramdisk
test "$(getprop ro.product.board)" = spinel || exit 20
test "$(getprop ro.build.version.sdk)" = 36 || exit 20
boot=$(cat /proc/sys/kernel/random/boot_id)
case "$boot" in *[!0-9a-f-]*|'') exit 20;; esac
state=/data/adb/r94-performance-runtime/native-pinner
test ! -L "$state" || exit 20
umask 077
mkdir -p "$state"
chmod 700 "$state"
test "$(stat -c %u "$state")" = 0 || exit 20
result="$state/$boot-fd-v6-result.txt"
started="$state/$boot-fd-v6-started.txt"
test ! -e "$started" || exit 0
ss=$(pidof system_server || true)
home=$(pidof com.android.launcher || true)
case "$ss:$home" in *[!0-9:]*|:*|*:) exit 20;; esac
test -n "$ss" && test -n "$home" || exit 20
apk=/system_ext/priv-app/OplusLauncher/OplusLauncher.apk
identity=$(stat -Lc '%d:%i' "/proc/$ss/root$apk")
test "$identity" = "$(stat -Lc '%d:%i' "/proc/$home/root$apk")" || exit 21
device=${identity%:*}; inode=${identity#*:}
case "$device:$inode" in *[!0-9:]*|:*|*:) exit 21;; esac
# Android mksh has 32-bit arithmetic: shifting by 32 wraps and corrupts
# the major number. Decode bounded dev_t values without shell bit shifts.
devtag=$(awk -v d="$device" 'BEGIN {
 if (d<0 || d>=4294967296) exit 1;
 printf "%02x:%02x", int(d/256)%4096, d%256+int(d/1048576)*256
}') || exit 21
check_pin() {
 awk -v iid="$inode" -v dev="$devtag" -v path="$apk" '
 /^[0-9a-f]+-[0-9a-f]+ / {selected=($3=="00000000" && $4==dev && $5==iid && $NF==path)}
 selected && /^Locked:/ {if ($2>0) found=1}
 END {exit !found}' "/proc/$ss/smaps"
}
printf 'boot=%s ss=%s home=%s identity=%s\n' "$boot" "$ss" "$home" "$identity" > "$started"
if check_pin; then
 echo "NATIVE_PINNER_CURRENT_INODE_ALREADY_LOCKED boot=$boot identity=$identity" > "$result"
 exit 0
fi
# Supported native shell endpoint queues unpin/repin; command success alone
# is insufficient. Verify locked mapping of this actual inode afterwards.
command_log="$state/$boot-fd-v6-command.txt"
{ cmd pinner repin </dev/null 2>&1; echo "PINNER_NATIVE_RC:$?"; } | cat > "$command_log"
grep -qx PINNER_NATIVE_RC:0 "$command_log" || { echo NATIVE_PINNER_COMMAND_FAILED > "$result"; exit 22; }
count=0
while test "$count" -lt 40; do
 test "$(cat /proc/sys/kernel/random/boot_id)" = "$boot" || exit 23
 test "$(pidof system_server)" = "$ss" && test "$(pidof com.android.launcher)" = "$home" || { echo NATIVE_PINNER_IDENTITY_CHANGED > "$result"; exit 23; }
 if check_pin; then
  echo "NATIVE_PINNER_CURRENT_INODE_LOCKED_AFTER_REPIN boot=$boot identity=$identity" > "$result"
  exit 0
 fi
 count=$((count+1)); sleep 0.25
done
echo "NATIVE_PINNER_ACTUAL_LOCK_NOT_VERIFIED boot=$boot identity=$identity" > "$result"
exit 24
