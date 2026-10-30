#!/system/bin/sh
test "$(getprop ro.product.board)" = spinel || abort 'Only spinel is supported.'
test "$(getenforce)" = Enforcing || abort 'SELinux Enforcing is required.'
test "$(sha256sum /system/framework/oplus-framework.jar | cut -d ' ' -f 1)" = c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99 || abort 'Framework is not the inspected version.'
test -x /data/adb/magisk/busybox && test -x /debug_ramdisk/su || abort 'Expected Magisk runtime is absent.'
for n in default r94prod r94_pms r94_gate r94_gate2; do
 answer=$(service check vendor.oplus.hardware.cryptoeng.ICryptoeng/$n 2>&1)
 test "$answer" = "Service vendor.oplus.hardware.cryptoeng.ICryptoeng/$n: not found" || abort 'Existing or unreadable CryptoEng service; stop instead of replacing it.'
done
(cd "$MODPATH" && sha256sum -c SHA256SUMS) || abort 'Candidate checksum failed.'
set_perm_recursive "$MODPATH" 0 0 0755 0644
set_perm "$MODPATH/bin/pms-gateway" 0 0 0755
set_perm "$MODPATH/bin/pms-backing" 0 0 0755
set_perm "$MODPATH/bin/owner-back" 0 0 0755
set_perm "$MODPATH/bin/owner-gate" 0 0 0755
for n in service.sh runner.sh guard.sh control.sh action.sh uninstall.sh policy-bootstrap.sh; do set_perm "$MODPATH/$n" 0 0 0755; done
ui_print 'Test candidate prepared. Reboot required for policy and services.'
ui_print 'Keep the data directory when disabling/removing this candidate.'
