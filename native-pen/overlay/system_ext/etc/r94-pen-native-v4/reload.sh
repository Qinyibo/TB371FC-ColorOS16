#!/system/bin/sh
set -eu
test "$(sha256sum /my_product/priv-app/IPeManager/IPeManager.apk | cut -d ' ' -f 1)" = 43585b82be1f50899ae50e378439655c3947d2bae2e64bad0de456148883d94b
test "$(sha256sum /system_ext/priv-app/WirelessSettings/WirelessSettings.apk | cut -d ' ' -f 1)" = 2e7327f1b4bdc4b504ad076a86684fd46c2891436b1e7a4bfd1abcb1754d1cce
cmd activity force-stop com.oplus.ipemanager >/dev/null 2>&1
cmd activity force-stop com.oplus.wirelesssettings >/dev/null 2>&1
if [ "$(am get-started-user-state 0 2>&1)" = RUNNING_LOCKED ]; then
    exit 0
fi
am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1
