#!/system/bin/sh
set -eu
export PATH=/system/bin:/system/xbin:/debug_ramdisk
MODDIR=${0%/*}
state=/data/adb/r94-performance-runtime
native=/system_ext/etc/r94-native/scheduler
test "$(id -u)" = 0
test "$(getprop ro.product.board)" = spinel
test "$(sha256sum "$native/mapper" | cut -d ' ' -f 1)" = fd2f0f18ef7449e820c92eeae878740f5901552d2257e30d98bdd441b1fd935b
test ! -L "$state"
umask 077
mkdir -p "$state"
owned_pids() {
    for p in $(pidof mapper 2>/dev/null || true); do
        test "$(readlink /proc/$p/exe 2>/dev/null || true)" = "$native/mapper" || continue
        echo "$p"
    done
}
stop_owned() {
    touch "$state/user.disabled" "$state/live.stop"
    n=0
    while test -n "$(owned_pids)" || test -e "$state/controller.lease"; do
        n=$((n+1)); test "$n" -le 100 || { echo SCHEDULER_CLEAN_STOP_PENDING; return 21; }
        sleep 0.1
    done
    setprop ctl.stop r94-native-scheduler
    echo SCHEDULER_STOPPED_AND_OWNERSHIP_RETURNED
}
start_owned() {
    test ! -e "$MODDIR/remove" || { echo MODULE_REMOVE_PENDING; return 20; }
    test ! -e "$native/disable" || { echo NATIVE_FAULT_DISABLE_PRESERVED; return 20; }
    rm -f "$MODDIR/disable" "$state/user.disabled" "$state/live.stop"
    setprop ctl.start r94-native-scheduler
    echo SCHEDULER_START_REQUESTED
}
case "${1:-status}" in
    stop) touch "$MODDIR/disable"; stop_owned;;
    start) start_owned;;
    reconcile)
        if test -e "$MODDIR/disable" || test -e "$MODDIR/remove"; then stop_owned; else start_owned; fi;;
    toggle)
        if test -e "$MODDIR/disable" || test -e "$state/user.disabled"; then start_owned;
        else touch "$MODDIR/disable"; stop_owned; fi;;
    status)
        echo "init=$(getprop init.svc.r94-native-scheduler) owners=$(owned_pids | tr '\n' ' ')"
        test ! -e "$MODDIR/disable" || echo MODULE_DISABLED
        test ! -e "$state/user.disabled" || echo USER_DISABLED
        test ! -e "$native/disable" || echo NATIVE_FAULT_DISABLED;;
    *) exit 2;;
esac
