#!/system/bin/sh
set -u
# mksh closes fd9 at exec; the supervisor must keep the lock fd across the
# log redirect, so re-exec under busybox sh exactly like the retired module.
if test "${1:-}" != --supervised-ash; then
 exec /data/adb/magisk/busybox sh "$0" --supervised-ash
fi
export PATH=/system/bin:/system/xbin:/debug_ramdisk
NDIR=/system_ext/etc/r94-native/scheduler
state=/data/adb/r94-performance-runtime
umask 077
mkdir -p "$state/mount" || exit 20
chmod 700 "$state" "$state/mount"
exec 9>"$state/supervisor.lock"
/system/bin/flock -n 9 || exit 0
exec >> "$state/native-runtime.log" 2>&1
echo NATIVE_SUPERVISOR_V1_START
test "$(getprop ro.product.board)" = spinel || exit 20
test "$(getprop ro.build.version.sdk)" = 36 || exit 20
count=0
while test "$(getprop sys.boot_completed)" != 1; do
 count=$((count+1)); test "$count" -lt 90 || exit 20
 sleep 2
done
test "$(sha256sum "$NDIR/mapper" | cut -d ' ' -f 1)" = fd2f0f18ef7449e820c92eeae878740f5901552d2257e30d98bdd441b1fd935b || exit 20
boot=$(cat /proc/sys/kernel/random/boot_id)
enabled() {
 test ! -e "$NDIR/disable" && test ! -e "$state/user.disabled" &&
 test ! -e /data/adb/modules/r94_foreground_schedtune/disable &&
 test ! -e /data/adb/modules/r94_foreground_schedtune/remove
}
enabled || exit 0
# Existing accepted QS intentionally reloads SystemUI after density/launcher
# settle. Wait for this boot's terminal receipt instead of spending retries
# on its expected lifecycle. This is read-only coordination, no QS changes.
echo BOOT_DEPENDENCIES_SETTLED
# Keep native pinning coherent with the settled late-bound launcher.
if test "$(sha256sum "$NDIR/native-pinner-sync.sh" | cut -d ' ' -f 1)" = a16a272f80cdae2f7ead30ca307b7cf22144bb9f9dbf05a4957dc171ba1a3600; then
 /system/bin/sh "$NDIR/native-pinner-sync.sh" 9>&- || echo NATIVE_PINNER_SYNC_UNVERIFIED
else
 echo NATIVE_PINNER_HELPER_HASH_MISMATCH
fi
if test -e "$state/controller.lease"; then
 test -f "$state/controller.lease" && test ! -L "$state/controller.lease" || exit 21
 test "$(stat -c %u:%a "$state/controller.lease")" = 0:600 || exit 21
 leaseboot=$(head -n 1 "$state/controller.lease")
 if test "$leaseboot" != "$boot"; then
  test "$(tail -n 1 "$state/controller.lease")" = R94_PERFORMANCE_V11 || exit 21
  test "$(wc -l < "$state/controller.lease")" = 2 || exit 21
  # Kernel cgroups disappear on real reboot. Never discard same-boot state.
  grep -F " $state/mount " /proc/self/mountinfo >/dev/null && exit 21
  test ! -e "$state/mount/r94_foreground" || exit 21
  mv "$state/controller.lease" "$state/lease.previous-$boot" || exit 21
  echo PREVIOUS_BOOT_LEASE_ARCHIVED
 else
  "$NDIR/mapper" --recover-owned || { echo START_RECOVERY_REFUSED; exit 21; }
 fi
fi
rm -f "$state/live.stop"
backoff=30
while enabled && test ! -e "$state/live.stop"; do
 uiuid=$(awk '$1=="com.android.systemui" {print $2; exit}' /data/system/packages.list)
 homeuid=$(awk '$1=="com.android.launcher" {print $2; exit}' /data/system/packages.list)
 uipid=$(pidof com.android.systemui || true)
 homepid=$(pidof com.android.launcher || true)
 case "$uiuid:$homeuid:$uipid:$homepid" in *[!0-9:]*|:*|*::*) sleep 1; continue;; esac
 test -n "$uiuid" && test -n "$homeuid" && test -n "$uipid" && test -n "$homepid" || { sleep 1; continue; }
 test "$(cat /proc/sys/kernel/random/boot_id)" = "$boot" || exit 20
 # Admit only after the same UI/Home identity has remained for five
 # seconds; bound each settle window and honor user stop/disable.
 stable=0; checks=0; previous=
 while test "$stable" -lt 5; do
  enabled && test ! -e "$state/live.stop" || exit 0
  current="$(pidof com.android.systemui || true):$(pidof com.android.launcher || true)"
  case "$current" in *[!0-9:]*|:*|*:) stable=0;;
   *) if test "$current" = "$previous"; then stable=$((stable+1)); else stable=0; fi;;
  esac
  previous=$current; checks=$((checks+1))
  test "$checks" -lt 60 || { echo UI_SETTLE_TIMEOUT_STOP; exit 20; }
  sleep 1
 done
 uipid=${current%:*}; homepid=${current#*:}
 test "$(cat /proc/sys/kernel/random/boot_id)" = "$boot" || exit 20
 test ! -e "$state/controller.lease" || { echo OWNERSHIP_NOT_CLEAR; exit 21; }
 { printf '%s
' "$boot"; echo R94_PERFORMANCE_V11; } > "$state/controller.lease"
 chmod 600 "$state/controller.lease"
 run_start=$(cut -d . -f 1 /proc/uptime)
 echo "CONTROLLER_ADMIT ui=$uipid home=$homepid uptime=$run_start"
 "$NDIR/mapper" 30 live 86400 "$uiuid" "$homeuid" "$uipid" "$homepid" 9>&-
 rc=$?
 run_end=$(cut -d . -f 1 /proc/uptime)
 run_seconds=$((run_end-run_start))
 echo "CONTROLLER_EXIT:$rc seconds=$run_seconds"
 if test -e "$state/controller.lease"; then
  "$NDIR/mapper" --recover-owned 9>&- || { echo EXIT_RECOVERY_REFUSED; touch "$NDIR/disable"; exit 21; }
 fi
 enabled && test ! -e "$state/live.stop" || break
 case "$rc" in
  0) backoff=30;;
  25) if test "$run_seconds" -lt 60; then
   # UI identity changed shortly after admission (restart/reload churn).
   # That is lifecycle, not controller breakage: back off exponentially and
   # retry. Permanent self-disable stays reserved for unexpected exit codes.
   echo IDENTITY_CHANGE_BACKOFF wait=$backoff
   sleep "$backoff"
   backoff=$((backoff * 2))
   test "$backoff" -le 300 || backoff=300
  else
   backoff=30
  fi;;
  *) echo UNEXPECTED_EXIT_DISABLED; touch "$NDIR/disable"; break;;
 esac
 sleep 1
done
echo NATIVE_SUPERVISOR_V1_STOP
