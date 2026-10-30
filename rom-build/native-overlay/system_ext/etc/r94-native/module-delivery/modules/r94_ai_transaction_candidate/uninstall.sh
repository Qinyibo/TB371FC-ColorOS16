#!/system/bin/sh
MODDIR=${0%/*}
umask 077
if sh "$MODDIR/restore.sh"; then exit 0; fi
# Magisk may remove the module directory even when uninstall returns failure.
# Keep failed restore records and their standalone restore tool outside it.
recovery=${R94_AI_RECOVERY_DIR:-/data/adb/r94-ai-transaction-recovery}
mkdir -p "$recovery" || exit 27
chmod 700 "$recovery" || exit 27
for item in common.sh restore.sh state.txt; do
    cp "$MODDIR/$item" "$recovery/$item" || exit 27
done
chmod 700 "$recovery/common.sh" "$recovery/restore.sh" || exit 27
chmod 600 "$recovery/state.txt" || exit 27
echo "AI_RESTORE_PENDING_SAVED:$recovery"
exit 26
