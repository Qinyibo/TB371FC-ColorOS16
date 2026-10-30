#!/system/bin/sh
MODDIR=${0%/*}
. "$MODDIR/common.sh"
set -eu
umask 077
acquire_lock
if restore_locked; then echo AI_TRANSACTION_RESTORED; else exit 26; fi
