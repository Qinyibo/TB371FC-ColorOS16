[ "$BOOTMODE" = true ] || abort "Install in running Magisk"
set_perm_recursive "$MODPATH" 0 0 0755 0644
for f in apply.sh restore.sh service.sh action.sh uninstall.sh; do set_perm "$MODPATH/$f" 0 0 0755; done
