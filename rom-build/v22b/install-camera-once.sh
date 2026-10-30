#!/system/bin/sh
# Restore the exact signed system-camera update once after initial setup.
# PackageManager owns app permissions, labels and signature verification.
set -eu
if test "${1:-}" != --ash; then
    exec /data/adb/magisk/busybox sh "$0" --ash
fi
test "$(id -u)" = 0
test "$(getprop ro.product.board)" = spinel
test "$(getprop ro.build.version.sdk)" = 36
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a
test "$(getprop sys.boot_completed)" = 1
assets=${R94_CAMERA_ASSETS:-/system/etc/r94-camera-v7}
state=${R94_CAMERA_STATE:-/data/adb/r94-camera-preload-v7}
bb=/data/adb/magisk/busybox
apk_hash=0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e
archive_hash=47c319d28086f0d9819ecb8404f27c5694c90d8dc843a01bdf67f6a4f753793c
base_hash=3019d0e8d7815a5e0a5b60dafed7803172954e42883e5ae17c109401e020d511
legacy_hash=beaa56d744387613661f198849679fd9963a66fc8efddeb38e5b76671db220bc
test -x "$bb"
test ! -L "$assets" && test -d "$assets"
test ! -L "$state"
umask 077
mkdir -p "$state"
test "$(stat -c '%u:%g' "$state")" = 0:0
chmod 0700 "$state"
exec 8>"$state/install.lock"
"$bb" flock -n 8 || exit 0
test ! -L "$state/complete"
test ! -L "$state/complete.next"
# Preserve an intentional later user uninstall; factory reset removes this mark.
if test -f "$state/complete"; then
    test "$(cat "$state/complete")" = "$apk_hash"
    echo R94_CAMERA_ALREADY_PROVISIONED
    exit 0
fi
asset="$assets/ZuiCamera.apk.xz"
test ! -L "$asset" && test -f "$asset"
test "$(sha256sum "$asset" | cut -d ' ' -f 1)" = "$archive_hash"
base=/system/app/ZuiCameraSeed/ZuiCameraSeed.apk
test -f "$base" && test ! -L "$base"
test "$(sha256sum "$base" | cut -d ' ' -f 1)" = "$base_hash"
paths=$(/system/bin/pm path --user 0 com.zui.camera 2>&1)
current=$(printf '%s\n' "$paths" | sed -n 's/^package://p')
test "$(printf '%s\n' "$current" | wc -l)" = 1
case "$current" in
    /system/app/ZuiCameraSeed/ZuiCameraSeed.apk|/data/app/*/base.apk) ;;
    *) echo R94_CAMERA_UNEXPECTED_PACKAGE_PATH; exit 22;;
esac
current_hash=$(sha256sum "$current" | cut -d ' ' -f 1)
if test "$current_hash" != "$apk_hash"; then
    # Do not downgrade or overwrite an unknown user camera update.
    if test "$current_hash" != "$base_hash" && test "$current_hash" != "$legacy_hash"; then
        echo R94_CAMERA_USER_UPDATE_PRESERVED
        exit 0
    fi
    decoded_hash=$("$bb" xz -dc "$asset" 8>&- | sha256sum | cut -d ' ' -f 1)
    test "$decoded_hash" = "$apk_hash"
    # Keep Binder stdout/stderr on a pipe, never an adb_data_file log FD.
    result=$("$bb" xz -dc "$asset" 8>&- | /system/bin/pm install -r --user 0 -S 235702464 8>&- 2>&1)
    printf '%s\n' "$result"
    printf '%s\n' "$result" | grep -q '^Success'
fi
paths=$(/system/bin/pm path --user 0 com.zui.camera 2>&1)
current=$(printf '%s\n' "$paths" | sed -n 's/^package://p')
case "$current" in /data/app/*/base.apk) ;; *) exit 23;; esac
test "$(sha256sum "$current" | cut -d ' ' -f 1)" = "$apk_hash"
printf '%s\n' "$apk_hash" >"$state/complete.next"
mv "$state/complete.next" "$state/complete"
echo R94_CAMERA_SYSTEM_UPDATE_EXACT_APK_READY
