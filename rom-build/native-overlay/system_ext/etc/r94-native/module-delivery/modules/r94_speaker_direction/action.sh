#!/system/bin/sh
set -eu
MODDIR=${0%/*}
if [ -e "$MODDIR/disable" ]; then
    rm -f "$MODDIR/disable"
    nohup sh "$MODDIR/service.sh" >/dev/null 2>&1 </dev/null &
    echo 四扬旋转已启用，等待外放媒体事件
else
    exec sh "$MODDIR/stop.sh"
fi
