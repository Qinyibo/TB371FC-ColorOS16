#!/system/bin/sh
set -eu
if [ "${1:-}" != --ash ]; then
    exec /data/adb/magisk/busybox sh "$0" --ash
fi
export PATH=/system/bin:/system/xbin:/debug_ramdisk
state=/data/adb/r94-comm-defaults
key=VCOMM_SHARE_NETWORK

# Binder shell commands cannot receive an adb_data_file log FD. Capture both
# provider output FDs in a pipe, then append plain text to the caller's log.
settings() {
    local text rc=0
    text=$(command settings "$@" 2>&1) || rc=$?
    printf '%s\n' "$text"
    return "$rc"
}

[ "$(getprop ro.product.board)" = spinel ] || exit 20
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 20
[ "$(settings get secure user_setup_complete)" = 1 ] || exit 20
[ ! -L "$state" ] || exit 20
umask 077
mkdir -p "$state"
chmod 700 "$state"
exec 9>"$state/seed.lock"
flock -n 9 || exit 0
[ ! -L "$state/network-default-v1-complete" ] || exit 20
if [ -e "$state/network-default-v1-complete" ]; then
    echo COMM_NETWORK_DEFAULT_ALREADY_RECONCILED
    exit 0
fi
value=$(settings get global "$key") || exit 20
case "$value" in
    0|1)
        # An explicit user choice always wins, including an explicit off.
        printf 'preserved=%s\n' "$value" > "$state/network-default-v1.next"
        mv "$state/network-default-v1.next" "$state/network-default-v1-complete"
        echo "COMM_NETWORK_EXPLICIT_VALUE_PRESERVED:$value"
        exit 0
        ;;
    null) ;;
    *) echo COMM_NETWORK_VALUE_UNREADABLE; exit 20;;
esac
# Persist the pre-change value before any provider write. A second read narrows
# the UI race; this is not an atomic SettingsProvider compare-and-set operation.
printf 'previous=null\nintended=1\n' > "$state/network-default-v1-before"
value=$(settings get global "$key") || exit 20
case "$value" in
    null) ;;
    0|1)
        printf 'preserved=%s\n' "$value" > "$state/network-default-v1.next"
        mv "$state/network-default-v1.next" "$state/network-default-v1-complete"
        echo "COMM_NETWORK_CHANGED_VALUE_PRESERVED:$value"
        exit 0
        ;;
    *) echo COMM_NETWORK_REREAD_UNREADABLE; exit 20;;
esac
settings put global "$key" 1 || { echo COMM_NETWORK_DEFAULT_WRITE_FAILED; exit 21; }
value=$(settings get global "$key") || exit 21
case "$value" in
    1) result=seeded_missing_to_ui_default_1;;
    0) result=user_off_after_write_preserved;;
    *) echo COMM_NETWORK_DEFAULT_VERIFY_PENDING; exit 21;;
esac
printf '%s\n' "$result" > "$state/network-default-v1.next"
mv "$state/network-default-v1.next" "$state/network-default-v1-complete"
echo "COMM_NETWORK_DEFAULT_RECONCILED:$result"
