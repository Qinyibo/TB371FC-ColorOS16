#!/system/bin/sh
MODDIR=${0%/*}
exec >"$MODDIR/startup.log" 2>&1
test "$(getprop ro.product.board)" = spinel || exit 0
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a || exit 0
test "$(getenforce)" = Enforcing || exit 1
count=0
while [ "$(getprop sys.boot_completed)" != 1 ]; do
  [ "$count" -lt 120 ] || exit 1
  [ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ] || exit 0
  sleep 1
  count=$((count+1))
done
exec /system/bin/sh "$MODDIR/activate.sh" "$MODDIR"
