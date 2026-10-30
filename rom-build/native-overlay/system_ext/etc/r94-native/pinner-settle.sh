#!/system/bin/sh
# Finite reconciliation after the accepted launcher file identity settles. Platform Pinner
# owns mappings and quota. No module hook, su, private cache or pinning daemon.
set -eu
setprop debug.r94.pinner_ready 0
exec > /data/local/tmp/r94-native-pinner.log 2>&1
apk=/system_ext/priv-app/OplusLauncher/OplusLauncher.apk
expected=1f04f79c4564c58b03673f4ca575e270f08bc10d926ccc6509797aef15cb5024
last=""
stable=0
count=0
while [ "$count" -lt 120 ]; do
    count=$((count+1))
    identity=$(stat -Lc %d:%i:%s "$apk")
    hash=$(sha256sum "$apk" | cut -d ' ' -f 1)
    if [ "$hash" = "$expected" ] && [ "$(getprop init.svc.r91-rom)" != running ]; then
        if [ "$identity" = "$last" ]; then stable=$((stable+1)); else last=$identity; stable=0; fi
        [ "$stable" -ge 5 ] && break
    else
        stable=0
        last=""
    fi
    sleep 1
done
[ "$stable" -ge 5 ] || { echo LAUNCHER_VERSION_OR_LIFECYCLE_NOT_READY; exit 20; }
# Capture Binder replies in a pipe, not an FD owned by the startup shell.
reply=$(cmd pinner repin 2>&1) || { printf '%s\n' "$reply"; exit 21; }
printf '%s\n' "$reply"
setprop debug.r94.pinner_ready 1
echo NATIVE_PINNER_RECONCILED_APK_IDENTITY:$last
