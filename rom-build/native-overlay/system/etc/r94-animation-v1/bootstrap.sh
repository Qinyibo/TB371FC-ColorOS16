#!/system/bin/sh
set -eu
assets=/system/etc/r94-animation-v1
cache=/data/local/r94-animation-v1
mkdir -p "$cache"
chmod 755 "$cache"
setprop debug.r94.animation_active_level "$(getprop persist.sys.oplus.anim_level)"
CLASSPATH="$assets/bootstrap.jar" app_process /system/bin org.tb371fc.animation.NativeAssets "$assets" "$cache"
for k in launcher settings assistant; do
    chmod 755 "$cache/$k"
    chmod 644 "$cache/$k/"*.apk
    chcon u:object_r:system_file:s0 "$cache/$k" "$cache/$k/"*.apk
done
run_cli() { local result rc=0; result=$("$@" 2>&1) || rc=$?; printf '%s\n' "$result"; return "$rc"; }
run_cli am force-stop com.android.settings
run_cli am force-stop com.android.launcher
run_cli am force-stop com.coloros.assistantscreen
# The previous assistant's ART files describe its old dex; never keep them bound.
prefix=/data/dalvik-cache/arm64/my_stock@app@AssistantScreen@AssistantScreen.apk@classes
for s in art dex vdex; do umount -l "$prefix.$s" 2>/dev/null || true; done
bind_apk() {
    mount -o bind "$1" "$2"
    "$assets/bind-readonly" "$2"
}
if [ ! -f "$cache/launcher/OplusLauncher.apk.prof" ]; then
    cp /system_ext/priv-app/OplusLauncher/OplusLauncher.apk.prof "$cache/launcher/"
    chmod 644 "$cache/launcher/OplusLauncher.apk.prof"
    chcon u:object_r:system_file:s0 "$cache/launcher/OplusLauncher.apk.prof"
fi
# Bind the launcher directory so ART cannot select the donor's stale read-only oat directory.
bind_apk "$cache/launcher" /system_ext/priv-app/OplusLauncher
if [ ! -f "$cache/settings/Settings.apk.prof" ]; then
    cp /system_ext/priv-app/Settings/Settings.apk.prof "$cache/settings/"
    chmod 644 "$cache/settings/Settings.apk.prof"
    chcon u:object_r:system_file:s0 "$cache/settings/Settings.apk.prof"
fi
bind_apk "$cache/settings" /system_ext/priv-app/Settings
bind_apk "$cache/assistant" /my_stock/app/AssistantScreen
if [ ! -f "$cache/compiled-b21cb3bc5aa7998e" ]; then
    complete=1
    for package in com.android.launcher com.android.settings com.coloros.assistantscreen; do
        result=$(run_cli cmd package compile --primary-dex -m speed -f "$package") || complete=0
        printf '%s\n' "$result"
        printf '%s\n' "$result" | grep -q '^Success' || complete=0
    done
    if [ "$complete" = 1 ]; then touch "$cache/compiled-b21cb3bc5aa7998e"; fi
fi
run_cli cmd pinner repin || true
# One-time recovery from the old unsupported-tier preferences; later respect the user.
if [ ! -f "$cache/defaults-v2" ]; then
    run_cli settings --user 0 put secure key_recent_style stacked
    run_cli settings --user 0 put secure disable_assistant_screen 0
    touch "$cache/defaults-v2"
fi
# Discard any Launcher relaunched while the APK directories were being bound.
# Its classes and cached stack support must come from the final mounted APK.
run_cli am force-stop com.android.launcher
if [ "$(run_cli am get-started-user-state 0)" = RUNNING_UNLOCKED ]; then
    run_cli am start -a android.intent.action.MAIN -c android.intent.category.HOME
fi
setprop debug.r94.animation_ready 1
echo R94_ANIMATION_MODES_READY
