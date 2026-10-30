#!/system/bin/sh
# One synchronous boot admission check. Assets remain on the system partition.
set -eu
J=/system_ext/etc/r94-native/mirror/javalib/odmf.jar
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a
test "$(getprop ro.product.board)" = spinel
check() { test "$(sha256sum "$1" | cut -d ' ' -f 1)" = "$2"; }
check /system_ext/opex/odmf.opex 8195fdc423483c880571621cb986186a2b367244ce366bd205060511668c373c
check /mnt/opex/com.oplus.odmf@16002004/javalib/odmf.jar fbbac634895ef14c8168d3b955f5eb7ca11499b447d4f994f71cb137bcfc38f3
check /system_ext/framework/oplusex/com.oplus.odmf/odmf.jar fbbac634895ef14c8168d3b955f5eb7ca11499b447d4f994f71cb137bcfc38f3
check "$J" eaa0e235f437a7401f20f3e74eb28452b6968ee82c0e4a326d63bd4eabc98ca5
test ! -s /system_ext/etc/r94-native/mirror/javalib/odmf.txt
setprop debug.r94.mirror_source /system_ext/etc/r94-native/mirror/javalib
log -t R94NativeMirror 'Original OPEX verified; native decoder admitted before zygote'
