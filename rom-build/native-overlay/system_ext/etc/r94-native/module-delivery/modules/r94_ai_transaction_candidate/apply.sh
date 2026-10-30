#!/system/bin/sh
MODDIR=${0%/*}
. "$MODDIR/common.sh"
set -eu
umask 077
[ "$(getprop ro.build.version.sdk)" = 36 ] || exit 20
[ "$(getprop ro.product.board)" = spinel ] || exit 21
[ "$(getprop sys.boot_completed)" = 1 ] || exit 22
acquire_lock
fail() {
    local code=$1
    echo "AI_APPLY_FAILED:$code"
    restore_locked || echo AI_ROLLBACK_PENDING
    exit "$code"
}
trap 'fail 31' HUP INT TERM
validate_backup || { echo INVALID_BACKUP; exit 25; }
# Validate all names before making the first package-state change.
while IFS= read -r pkg; do
    [ -n "$pkg" ] || continue
    allowed "$pkg" || { echo "INVALID_PACKAGE:$pkg"; exit 23; }
done < "$MODDIR/packages.txt"
while IFS= read -r pkg; do
    [ -n "$pkg" ] || continue
    # Do not disable again if a user re-enabled a module-owned package.
    if grep -q "^$pkg " "$MODDIR/state.txt" 2>/dev/null; then
        echo "ALREADY_RECORDED:$pkg"; continue
    fi
    old=$(state_of "$pkg") || fail 24
    [ -n "$old" ] || { echo "NOT_INSTALLED:$pkg"; continue; }
    case "$old" in 0|1) ;; 2|3|4) echo "ALREADY_DISABLED:$pkg:$old"; continue;; *) fail 24;; esac
    : > "$MODDIR/state.next" || fail 26
    if [ -f "$MODDIR/state.txt" ]; then cat "$MODDIR/state.txt" > "$MODDIR/state.next" || fail 26; fi
    printf '%s %s\n' "$pkg" "$old" >> "$MODDIR/state.next" || fail 26
    mv "$MODDIR/state.next" "$MODDIR/state.txt" || fail 26
    run_pm disable-user --user 0 "$pkg" || fail 24
    current=$(state_of "$pkg") || fail 24
    [ "$current" = 3 ] || fail 24
done < "$MODDIR/packages.txt"
trap - HUP INT TERM
echo AI_TRANSACTION_APPLIED
