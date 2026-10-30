#!/system/bin/sh
if test "${1:-}" != --ash; then exec /data/adb/magisk/busybox sh "$0" --ash; fi
set -eu
export PATH=/system/bin:/system/xbin:/debug_ramdisk
umask 077
MODDIR=/data/adb/modules/r94_privacy_password_test
STATE=/data/adb/r94pms
test "${0%/*}" = "$MODDIR" || exit 20
test ! -L /data/adb/r94pms-launch.lock || exit 20
if test -e /data/adb/r94pms-launch.lock; then test "$(stat -c '%u:%a:%h' /data/adb/r94pms-launch.lock)" = 0:600:1 || exit 20; fi
exec 9>>/data/adb/r94pms-launch.lock
flock -n 9 || exit 0
. "$MODDIR/config.sh"
. "$MODDIR/guard.sh"
count=0
while test "$(getprop sys.boot_completed)" != 1; do
    count=$((count+1)); test "$count" -lt 90 || exit 20; sleep 2
done
r94_gate
r94_profile_check
test "$(sha256sum "$MODDIR/bin/pms-backing" | cut -d ' ' -f 1)" = "$BACKEND_SHA" || exit 20
test "$(sha256sum "$MODDIR/bin/pms-gateway" | cut -d ' ' -f 1)" = "$GATEWAY_SHA" || exit 20
test "$(sha256sum "$MODDIR/bin/owner-back" | cut -d ' ' -f 1)" = "$OWNER_SHA" || exit 20
test "$(sha256sum "$MODDIR/bin/owner-gate" | cut -d ' ' -f 1)" = "$OWNER_SHA" || exit 20
. "$MODDIR/policy-bootstrap.sh"
r94_policy_prepare || exit 20
if test ! -e "$STATE"; then
    mkdir -m 700 "$STATE"
    mkdir -m 700 "$STATE/d" "$STATE/p" "$STATE/r"
    printf 'R94_PMS_SOFTWARE_PRIVACY_V1\n%s\n%s\n' "$BACKEND_SHA" "$SERIAL_DIGEST" > "$STATE/profile"
    chmod 600 "$STATE/profile"
fi
# Existing profile/key files are never removed, reset or migrated here.
chcon -R u:object_r:r94_pms_data:s0 "$STATE"
chcon u:object_r:r94_pms_exec:s0 "$MODDIR/bin/pms-backing"
chcon u:object_r:r94_pms_gate_exec:s0 "$MODDIR/bin/pms-gateway"
chcon u:object_r:r94_pms_exec:s0 "$MODDIR/bin/owner-back"
chcon u:object_r:r94_pms_gate_exec:s0 "$MODDIR/bin/owner-gate"
pid_start() { sed 's/^.*) //' "/proc/$1/stat" | cut -d ' ' -f 20; }
backend=0; gateway=0; backend_start=''; gateway_start=''; reason=stopped
stop_child() {
    p=$1; start=$2; binary=$3
    test "$p" -gt 1 || return 0
    if test -r "/proc/$p/stat" && test "$(pid_start "$p")" = "$start" && test "$(readlink "/proc/$p/exe")" = "$binary"; then
        kill -TERM "$p" 2>/dev/null || true
    fi
}
cleanup() {
    trap - EXIT TERM INT HUP
    stop_child "$gateway" "$gateway_start" "$MODDIR/bin/pms-gateway"
    stop_child "$backend" "$backend_start" "$MODDIR/bin/pms-backing"
    for p in "$gateway" "$backend"; do
        test "$p" -gt 1 || continue
        n=0
        while kill -0 "$p" 2>/dev/null && test "$n" -lt 25; do n=$((n+1)); sleep .2; done
    done
    # Last resort only for the exact owned executable and unchanged process
    # start time; never kill by a global name or stale PID alone.
    for name in gateway backend; do
        if test "$name" = gateway; then p=$gateway; s=$gateway_start; binary="$MODDIR/bin/pms-gateway"; else p=$backend; s=$backend_start; binary="$MODDIR/bin/pms-backing"; fi
        if test "$p" -gt 1 && test -r "/proc/$p/stat" && test "$(pid_start "$p")" = "$s" && test "$(readlink "/proc/$p/exe")" = "$binary"; then kill -KILL "$p" 2>/dev/null || true; fi
        wait "$p" 2>/dev/null || true
    done
    printf '%s\n' "R94_PRIVACY_$reason" > "$STATE/r/status"
    rm -f "$STATE/r/owner"
}
trap cleanup EXIT
trap 'reason=stopped; exit 0' TERM INT HUP
env CRYPTOENG_STORAGE_DIR="$STATE/d" CRYPTOENG_PERSIST_DIR="$STATE/p" CRYPTOENG_DEVICE_ID="$R94_PMS_DEVICE_SERIAL" CRYPTOENG_DEVICE_SERIAL="$R94_PMS_DEVICE_SERIAL" RUST_LOG=error \
    runcon u:r:r94_pms_backend:s0 "$MODDIR/bin/owner-back" "$$" "$MODDIR/bin/pms-backing" </dev/null >/dev/null 2>&1 9>&- &
backend=$!; backend_start=$(pid_start "$backend")
wait_service() {
    n=0
    while test "$n" -lt 30; do
        answer=$(service check "$1" 2>&1) || return 1
        test "$answer" = "Service $1: found" && return 0
        kill -0 "$2" 2>/dev/null || return 1
        n=$((n+1)); sleep .2
    done
    return 1
}
if ! wait_service vendor.oplus.hardware.cryptoeng.ICryptoeng/r94prod "$backend"; then reason=backend_start_failed; exit 21; fi
# Check again immediately before registration; ServiceManager offers no atomic
# absent-only add operation. This known-ROM candidate never replaces an
# already observed foreign/default service and never retries registration.
test "$(service check vendor.oplus.hardware.cryptoeng.ICryptoeng/default)" = 'Service vendor.oplus.hardware.cryptoeng.ICryptoeng/default: not found' || exit 21
runcon u:r:r94_pms_gateway:s0 "$MODDIR/bin/owner-gate" "$$" "$MODDIR/bin/pms-gateway" </dev/null >/dev/null 2>&1 9>&- &
gateway=$!; gateway_start=$(pid_start "$gateway")
if ! wait_service vendor.oplus.hardware.cryptoeng.ICryptoeng/default "$gateway"; then reason=gateway_start_failed; exit 21; fi
test "$(cat "/proc/$backend/attr/current")" = 'u:r:r94_pms_backend:s0' || exit 21
test "$(cat "/proc/$gateway/attr/current")" = 'u:r:r94_pms_gateway:s0' || exit 21
printf '%s\n%s\n%s\n' "$(cat /proc/sys/kernel/random/boot_id)" "$$" "$(pid_start $$)" > "$STATE/r/owner"
printf '%s\n' R94_PRIVACY_READY > "$STATE/r/status"
# Event-driven supervision. No recurring property polling or restart loop.
set +e
wait -n "$backend" "$gateway"
set -e
reason=child_exited
touch "$MODDIR/disable"
exit 21
