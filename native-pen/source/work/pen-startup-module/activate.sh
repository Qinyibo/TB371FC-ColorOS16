#!/system/bin/sh
set -eu
test "$(getprop ro.product.board)" = spinel
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a
test "$(getenforce)" = Enforcing
assets="$1/assets"
cache=/data/system/r94-pen-native-v2
if [ "$(sha256sum /my_product/priv-app/IPeManager/IPeManager.apk | cut -d ' ' -f 1)" = fd9344d373d008cb297ffadb46227e8a819db3cbe9db7fcea95514d081787b8b ] &&
   [ "$(sha256sum /system_ext/priv-app/WirelessSettings/WirelessSettings.apk | cut -d ' ' -f 1)" = c612a418d6638f6703853da23b9ba41fa74a6ca32d53cc86366f3a7932ba2956 ] &&
   grep -q '/system/r94-pen-native-v2/ipe /my_product/priv-app/IPeManager ro,' /proc/1/mountinfo &&
   grep -q '/system/r94-pen-native-v2/ws /system_ext/priv-app/WirelessSettings ro,' /proc/1/mountinfo; then
    echo ALREADY_ACTIVE
    exit 0
fi
test ! -e "$cache" || test -d "$cache"
mkdir -p "$cache"
chown root:root "$cache"
chmod 0755 "$cache"
/apex/com.android.art/bin/dalvikvm64 -cp "$assets/bootstrap.jar" org.tb371fc.pen.NativePayloadV2 "$assets" "$cache"
chown -R root:root "$cache"
find "$cache" -type d -exec chmod 0755 {} \;
find "$cache" -type f -exec chmod 0644 {} \;
chcon -R u:object_r:system_file:s0 "$cache"
# Both payloads are complete before either package is stopped or mounted.
cmd activity force-stop com.oplus.ipemanager >/dev/null 2>&1
cmd activity force-stop com.oplus.wirelesssettings >/dev/null 2>&1
mount --bind "$cache/ipe" /my_product/priv-app/IPeManager
if ! mount --bind "$cache/ws" /system_ext/priv-app/WirelessSettings; then
    umount /my_product/priv-app/IPeManager
    exit 1
fi
if ! "$assets/pen-mount-ro" /my_product/priv-app/IPeManager || ! "$assets/pen-mount-ro" /system_ext/priv-app/WirelessSettings; then
    umount /system_ext/priv-app/WirelessSettings
    umount /my_product/priv-app/IPeManager
    exit 1
fi
sha256sum /my_product/priv-app/IPeManager/IPeManager.apk /system_ext/priv-app/WirelessSettings/WirelessSettings.apk
am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1
echo LIVE_PEN_CODE_ACTIVE_PHYSICAL_FUNCTIONS_PENDING
