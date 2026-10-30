#!/system/bin/sh
MODDIR=${0%/*}
exec sh "$MODDIR/control.sh" reconcile > "$MODDIR/status.txt" 2>&1
