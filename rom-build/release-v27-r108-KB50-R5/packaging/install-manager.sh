#!/system/bin/sh
set -eu

manager=com.topjohnwu.magisk
apk=/system/etc/r94-magisk-manager/Magisk-v31.1.apk
digest=89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7
state=/data/adb/r91-rom
complete="$state/magisk-manager-v1-complete"

test "$(id -u)" = 0
test "$(getprop ro.product.board)" = spinel
test "$(getprop sys.boot_completed)" = 1
test "$(settings --user 0 get secure user_setup_complete 2>&1)" = 1
test -d "$state" && test ! -L "$state"
test "$(stat -c '%u:%g' "$state")" = 0:0
test ! -L "$complete"
if test -f "$complete"; then
    echo R94_MAGISK_MANAGER_PROVISIONED
    exit 0
fi

system_packages=$(/system/bin/pm list packages --user 0 -s -u "$manager" 2>&1)
if printf '%s\n' "$system_packages" | grep -Fxq "package:$manager"; then
    echo R94_MAGISK_MANAGER_UNEXPECTED_SYSTEM_APP
    exit 1
fi

packages=$(/system/bin/pm list packages --user 0 "$manager" 2>&1)
if printf '%s\n' "$packages" | grep -Fxq "package:$manager"; then
    echo R94_MAGISK_MANAGER_EXISTING_USER_APP
else
    test -f "$apk" && test ! -L "$apk"
    test "$(stat -c '%s' "$apk")" = 10679283
    test "$(sha256sum "$apk" | cut -d ' ' -f 1)" = "$digest"
    # Binder receives ordinary pipe FDs even when the service logs to /data/adb.
    result=$(cat "$apk" | /system/bin/pm install --user 0 -S 10679283 2>&1) || {
        printf '%s\n' "$result"
        exit 1
    }
    printf '%s\n' "$result" | grep -Fxq Success
    path=$(/system/bin/pm path --user 0 "$manager" 2>&1)
    case "$path" in
        package:/data/app/*/base.apk) ;;
        *) echo R94_MAGISK_MANAGER_UNEXPECTED_PATH; exit 1 ;;
    esac
    test "$(sha256sum "${path#package:}" | cut -d ' ' -f 1)" = "$digest"
    echo R94_MAGISK_MANAGER_USER_APP_VERIFIED
fi

umask 077
next=$(mktemp "$state/magisk-manager-v1.XXXXXXXX")
printf 'provisioned\n' > "$next"
mv -f "$next" "$complete"
