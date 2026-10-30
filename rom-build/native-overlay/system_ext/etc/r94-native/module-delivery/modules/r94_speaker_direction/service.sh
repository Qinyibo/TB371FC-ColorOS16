#!/system/bin/sh
set -u
if test "${1:-}" != --ash; then exec /data/adb/magisk/busybox sh "$0" --ash; fi
export PATH=/system/bin:/system/xbin:/debug_ramdisk
MODDIR=${0%/*}
STATE=/data/adb/r94-speaker-direction-v19
umask 077
test ! -L "$STATE" || exit 20
mkdir -p "$STATE" || exit 20
chmod 700 "$STATE"
# The first-install caller is an init oneshot service. Its descendants
# are killed when that service exits, even after nohup/setsid. Ask the
# existing Magisk daemon to own the long-running supervisor instead.
if test "${2:-}" != --managed-root; then
    test "$MODDIR" = /data/adb/modules/r94_speaker_direction || exit 20
    test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || exit 0
    /debug_ramdisk/su -M -c 'nohup /data/adb/magisk/busybox sh /data/adb/modules/r94_speaker_direction/service.sh --ash --managed-root >/data/adb/r94-speaker-direction-v19/launch.log 2>&1 </dev/null &' 8>&- 9>&-
    exit $?
fi
exec 9>"$STATE/supervisor.lock"
flock -n 9 || exit 0
exec >> "$STATE/runtime.log" 2>&1
test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || exit 0
test "$(getprop ro.product.board)" = spinel || exit 20
# API19 companion: requires inspected kernel35/36/37/38/39/40/41/42/43 and exact QS firmware.
uname -a | grep -E "#(35|36|37|38|39|40|41|42|43) SMP PREEMPT" >/dev/null || exit 20
test "$(cat /sys/module/tfa98xx_dlkm/parameters/fw_name)" = tfa98xx_QS.cnt || exit 20
test "$(sha256sum /vendor/firmware/tfa98xx_QS.cnt | cut -d ' ' -f 1)" = a3f641609cbb617ea2c3169e5a9edc6c04f89a342e99fd96dacc44f216cdfa81 || exit 20
test "$(sha256sum "$MODDIR/direction.jar" | cut -d ' ' -f 1)" = d11f3cf3e9fb8739c1a25c2e48a5cd266a4f07a1d97fdf3b820d606bfe835add || exit 20
test "$(sha256sum "$MODDIR/direction.so" | cut -d ' ' -f 1)" = c32f9b49c8a1e4aadd06ea72bcefdc8283f321c71a06a14d7e0b4a705f4aa675 || exit 20
test "$(sha256sum "$MODDIR/directionctl" | cut -d ' ' -f 1)" = a4cdf0686a98d8dc455b3543b8bb71c27d3bef0b74d538c9741645ff67b7d679 || exit 20
count=0
while test "$(getprop sys.boot_completed)" != 1; do count=$((count+1)); test "$count" -lt 90 || exit 20; sleep 2; done
test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || exit 0
rm -f "$STATE/stop"
echo NATIVE_TRANSACTION_API19_START
echo "MANAGED_ROOT_SUPERVISOR pid=$$ parent=$PPID"
cat /proc/self/cgroup
env CLASSPATH="$MODDIR/direction.jar" app_process /system/bin R94SpeakerDirection "$MODDIR/direction.so" 9>&- &
child=$!
printf '%s
' "$(cat /proc/sys/kernel/random/boot_id)" "$child" > "$STATE/owner.txt"
wait "$child"
rc=$?
echo "CALLBACK_SERVICE_EXIT:$rc"
# The child has exited and released route.lock. Recover native ownership even
# after an unexpected Java exit. A failed recovery keeps its record on disk.
if "$MODDIR/directionctl" --restore; then rm -f "$STATE/owner.txt"; else
    touch "$MODDIR/disable"; echo NATIVE_RECOVERY_PENDING; exit 21
fi
# No restart loop. Unexpected exit disables only this candidate.
if test "$rc" != 0; then touch "$MODDIR/disable"; fi
