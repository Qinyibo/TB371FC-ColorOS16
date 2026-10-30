#!/system/bin/sh
set -eu
test "$(getprop ro.product.board)" = spinel
test "$(sha256sum /my_product/priv-app/IPeManager/IPeManager.apk | cut -d ' ' -f 1)" = fd9344d373d008cb297ffadb46227e8a819db3cbe9db7fcea95514d081787b8b
test "$(sha256sum /system_ext/priv-app/WirelessSettings/WirelessSettings.apk | cut -d ' ' -f 1)" = c612a418d6638f6703853da23b9ba41fa74a6ca32d53cc86366f3a7932ba2956
cmd activity force-stop com.oplus.ipemanager >/dev/null 2>&1
cmd activity force-stop com.oplus.wirelesssettings >/dev/null 2>&1
umount /system_ext/priv-app/WirelessSettings
umount /my_product/priv-app/IPeManager
am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1
echo ORIGINAL_PACKAGES_RESTORED
