#!/system/bin/sh
MODDIR=${0%/*}
exec > "$MODDIR/status.txt" 2>&1
i=0
while [ "$(getprop sys.boot_completed)" != 1 ] && [ "$i" -lt 90 ]; do sleep 2; i=$((i+1)); done
if [ -e "$MODDIR/disable" ] || [ -e "$MODDIR/remove" ]; then
    exec sh "$MODDIR/restore.sh"
fi
exec sh "$MODDIR/apply.sh"
