#!/system/bin/sh
set -eu
MODDIR=${0%/*}
if [ -e "$MODDIR/disable" ]; then
    sh "$MODDIR/apply.sh"
    rm -f "$MODDIR/disable"
    echo 七项AI已停用
else
    sh "$MODDIR/restore.sh"
    touch "$MODDIR/disable"
    echo 已恢复模块记录的原状态
fi
