#!/system/bin/sh
# Retain password/key/profile files; uninstall is never a password reset.
sh "${0%/*}/control.sh" stop || true
