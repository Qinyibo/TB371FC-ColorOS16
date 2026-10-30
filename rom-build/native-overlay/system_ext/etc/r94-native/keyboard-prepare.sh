#!/system/bin/sh
# Original signed package is scanned first; verify exact build before native runtime bind.
# Android ART regenerates matching code as needed; no archived OAT/VDEX mounts.
set -eu
setprop debug.r94.keyboard_ready 0
test "$(sha256sum /my_stock/app/OplusSecurityKeyboard/OplusSecurityKeyboard.apk | cut -d ' ' -f 1)" = 9a9304f50497dc8566c72d79f9366f7cde3718f8b1545c72e97195e4eeac91e2
test "$(sha256sum /system_ext/etc/r94-native/keyboard/OplusSecurityKeyboard.apk | cut -d ' ' -f 1)" = b9db02a031e88d2c4fa7c13638d488c6f0df61ec4678b6636a092337199ddf10
reply=$(am force-stop com.oplus.securitykeyboard 2>&1) || { printf '%s\n' "$reply"; exit 20; }
setprop debug.r94.keyboard_ready 1
