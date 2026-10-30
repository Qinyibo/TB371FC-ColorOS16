[ "$BOOTMODE" = true ] || abort "Install in running Magisk"
uname -a | grep -E "#(35|36|37|38|39|40|41|42|43) SMP PREEMPT" >/dev/null || abort "Requires matching TB371FC kernel35, kernel36, kernel37 or kernel38"
set_perm_recursive "$MODPATH" 0 0 0755 0644
for f in service.sh action.sh stop.sh uninstall.sh directionctl; do set_perm "$MODPATH/$f" 0 0 0755; done
