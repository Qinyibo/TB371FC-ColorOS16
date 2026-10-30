#!/system/bin/sh
set -eu
MODDIR=/data/adb/modules/r94_privacy_password_test
STATE=/data/adb/r94pms
test "$(id -u)" = 0 || exit 20
test "${0%/*}" = "$MODDIR" || exit 20
case "${1:-status}" in
start)
    test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || exit 20
    exec sh "$MODDIR/service.sh";;
stop)
    test ! -L "$STATE" && test ! -L "$STATE/r" && test ! -L "$STATE/r/owner" || exit 20
    if test -f "$STATE/r/owner"; then
        boot=$(sed -n '1p' "$STATE/r/owner"); pid=$(sed -n '2p' "$STATE/r/owner"); started=$(sed -n '3p' "$STATE/r/owner")
        case "$pid:$started" in *[!0-9:]*|:|:*|*:) exit 20;; esac
        if test "$boot" = "$(cat /proc/sys/kernel/random/boot_id)" && test -r "/proc/$pid/stat"; then
            test "$(sed 's/^.*) //' "/proc/$pid/stat" | cut -d ' ' -f 20)" = "$started" || exit 20
            test "$(readlink "/proc/$pid/exe")" = /data/adb/magisk/busybox || exit 20
            tr '\000' '\n' < "/proc/$pid/cmdline" | grep -Fx "$MODDIR/runner.sh" >/dev/null || exit 20
            kill -TERM "$pid"
        fi
    fi
    touch "$MODDIR/disable"
    printf '%s\n' 'Candidate stopped/disabled; password profile retained.';;
status)
    if test -r "$STATE/r/status"; then cat "$STATE/r/status"; else echo R94_PRIVACY_NOT_STARTED; fi;;
*) exit 20;;
esac
