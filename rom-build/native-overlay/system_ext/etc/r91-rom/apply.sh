#!/system/bin/sh
# Launcher is directly preinstalled. This existing service retains only its
# Assistant bindings and once-only initial setup defaults. OTA is a static notice app.
set -eu
umask 077
rom=${R91_ROM_ROOT:-/system_ext/etc/r91-rom}
base=/data/adb/r91-rom
mkdir -p "$base"
chmod 700 "$base"
chcon u:object_r:adb_data_file:s0 "$base"
exec >> "$base/boot.log" 2>&1
trap 'echo R91_ROM_EXIT rc=$? >> $base/boot.log' EXIT
echo "R91_ROM_START $(date) boot=$(cat /proc/sys/kernel/random/boot_id)"
# The distributor checks fastboot product=spinel and partition geometry. Runtime
# checks the platform and exact base code, allowing other TB371FC serials.
test "$(getprop ro.board.platform)" = kona
test "$(getprop ro.boot.hardware)" = qcom
test "$(getprop sys.boot_completed)" = 1
test ! -e "$base/disabled"
(cd "$rom"; sha256sum -c SHA256SUMS)
# Binder shell commands reject passing an adb_data_file log FD to system_server.
# Capture both output FDs in a pipe, then append ordinary text to our own log.
run_cli() { local result rc=0; result=$("$@" 2>&1) || rc=$?; printf '%s\n' "$result"; return "$rc"; }
run_am() { run_cli /system/bin/am "$@"; }
cmd() { run_cli /system/bin/cmd "$@"; }
settings() { run_cli /system/bin/settings "$@"; }
wm() { run_cli /system/bin/wm "$@"; }
assistant_target=/my_stock/app/AssistantScreen/AssistantScreen.apk
ota_target=/system_ext/app/OTA/OTA.apk
assistant_prefix=/data/dalvik-cache/arm64/my_stock@app@AssistantScreen@AssistantScreen.apk@classes
# A changed base ROM must never receive stale candidates or stale ART files.
test "$(sha256sum /system_ext/priv-app/OplusLauncher/OplusLauncher.apk | cut -d ' ' -f 1)" = 1f04f79c4564c58b03673f4ca575e270f08bc10d926ccc6509797aef15cb5024 || { echo R91_ROM_BASE_GUARD_FAILED_1; exit 1; }
test "$(sha256sum "$assistant_target" | cut -d ' ' -f 1)" = c8e7396f691b146d630764e3037e7a41f92170c725e1661272406c41c7c6a628 || { echo R91_ROM_BASE_GUARD_FAILED_2; exit 1; }
test "$(sha256sum "$ota_target" | cut -d ' ' -f 1)" = ce7d4a1ed6b34f23c7fc972a86974ebf53be53c1627c623c826a4b852e0b0d9c || { echo R91_ROM_BASE_GUARD_FAILED_3; exit 1; }
test "$(sha256sum /system/framework/oplus-services.jar | cut -d ' ' -f 1)" = ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467 || { echo R91_ROM_BASE_GUARD_FAILED_4; exit 1; }
echo R91_ROM_NATIVE_BASE_IDENTITIES_OK

# Preserve the accepted launcher speed compilation after a clean installation.
# A failed optimization must not prevent the existing ROM setup from continuing.
launcher_aot_state=/data/adb/r94-launcher-aot-v23
mkdir -p "$launcher_aot_state"
if [ ! -f "$launcher_aot_state/complete" ]; then
    aot_result=$(cmd package compile -m speed -f com.android.launcher 2>&1) || aot_result=failed
    printf '%s
' "$aot_result"
    if printf '%s
' "$aot_result" | grep -q '^Success'; then
        touch "$launcher_aot_state/complete"
        cmd pinner repin || echo R94_LAUNCHER_PIN_PENDING
    else
        echo R94_LAUNCHER_AOT_PENDING
    fi
fi


sh /system_ext/etc/r94-native/module-delivery/delivery.sh provision-market || echo R94_MARKET_ASSET_PROVISION_FAILED
copy_asset() {
    if [ ! -f "$2" ]; then cp "$1" "$2"; fi
    test "$(sha256sum "$1" | cut -d ' ' -f 1)" = "$(sha256sum "$2" | cut -d ' ' -f 1)" || { echo "R91_ROM_ASSET_IDENTITY_FAILED $1"; return 1; }
}
mkdir -p /data/adb/r91-assistant/aot
copy_asset "$rom/assistant/AssistantScreen.apk" /data/adb/r91-assistant/AssistantScreen.apk
copy_asset "$rom/assistant/bind-readonly" /data/adb/r91-assistant/bind-readonly
chmod 700 /data/adb/r91-assistant/bind-readonly
chcon u:object_r:adb_data_file:s0 /data/adb/r91-assistant/bind-readonly
chmod 644 /data/adb/r91-assistant/AssistantScreen.apk
chcon u:object_r:system_file:s0 /data/adb/r91-assistant/AssistantScreen.apk
for s in art dex vdex; do
    copy_asset "$rom/assistant/AssistantScreen.$s" /data/adb/r91-assistant/aot/AssistantScreen.$s
done
chown 1000:1000 /data/adb/r91-assistant/aot/*
chmod 644 /data/adb/r91-assistant/aot/*
chcon u:object_r:dalvikcache_data_file:s0 /data/adb/r91-assistant/aot/*

rollback() {
    echo "R91_ROM_ROLLBACK $1"
    for s in art dex vdex; do umount -l "$assistant_prefix.$s" || true; done
    umount -l /my_stock/priv-app/KeKeMarket/KeKeMarket.apk || true
    umount -l "$assistant_target" || true
    touch "$base/disabled"
    run_am force-stop com.coloros.assistantscreen || true
    exit 1
}
cache_target() {
    if [ ! -f "$1" ]; then touch "$1" || rollback cache_target; fi
    chown 1000:1000 "$1" || rollback cache_owner
    chmod 644 "$1" || rollback cache_mode
    chcon u:object_r:dalvikcache_data_file:s0 "$1" || rollback cache_label
}
mkdir -p /data/dalvik-cache/arm64
# Settings are initial defaults, not forced on every boot. Never copy user data,
# accounts, Wi-Fi credentials, package restrictions or ADB authorization keys.
apply_defaults() {
    settings put system font_scale 0.9
    wm density reset
    settings put secure icon_size_range '[38,42,46]'
    settings put secure layout_icon_size 42.0
    settings put secure launcher_layout_parameter '{"layout_cellcount_x":8,"layout_cellcount_y":5}'
    settings put secure is_oplus_launcher_zoom 0
    settings put secure key_recent_style stacked
    settings put secure oplus_customize_screen_refresh_rate 4
    settings put system peak_refresh_rate 144.00002
    settings put system recommender_split_screen_enable 0
    settings put system accelerometer_rotation 1
    settings put system user_rotation 0
    settings put system font_variation_settings 4618
    settings put global auto_update_system 0
    settings put global can_update_at_night 0
    # Retain the two already accepted optional-background reductions.
    cmd package disable-user --user 0 com.oplus.statistics.rom
    cmd package disable-user --user 0 com.oplus.logkit
}
first_defaults=0
if [ ! -e "$base/defaults-v1-complete" ]; then
    first_defaults=1
    apply_defaults
fi
# The donor updater has been replaced in the image, before first package scan.
# This notice APK has zero requested permissions/services/receivers/providers.
# No late bind and no boot-time component-disable window remains.
echo R94_OTA_NATIVE_NOTICE_ONLY_NO_DONOR_UPDATER

# Stop only Assistant before replacing its previously accepted code.
run_am force-stop com.coloros.assistantscreen || rollback stop_assistant
mount -o bind /data/adb/r91-assistant/AssistantScreen.apk "$assistant_target" || rollback assistant_apk
for s in art dex vdex; do
    cache_target "$assistant_prefix.$s"
    mount -o bind /data/adb/r91-assistant/aot/AssistantScreen.$s "$assistant_prefix.$s" || rollback assistant_cache
done
/data/adb/r91-assistant/bind-readonly --paired || rollback assistant_readonly

# Market update-guard: same tested mechanism the retired r93_patch_guard
# module provided (bind patched market APK + R93PatchGuard policy). All
# failures skip only this section; assistant/OTA binds above are unaffected.
market_target=/my_stock/priv-app/KeKeMarket/KeKeMarket.apk
mg=/data/adb/r94-marketguard
mg_fail() { echo "R91_ROM_MARKET_GUARD_FAILED_$1"; umount -l "$market_target" 2>/dev/null || true; return 1; }
do_market_guard() {
    [ "$(sha256sum "$mg/market-apk-tail.bin" 2>/dev/null | cut -d ' ' -f 1)" = 4a6cc7a2f9f11afcde4baaf6a6e3d09aef5505ae002f307ab73145f088c0e78b ] || return 1
    [ "$(sha256sum "$mg/guard.dex" 2>/dev/null | cut -d ' ' -f 1)" = b04e456277dbb65338c7647c78c58b9d8b1bb458048f8a964a59a321fb5a9741 ] || return 1
    if [ ! -f "$mg/Market.apk" ] || [ "$(sha256sum "$mg/Market.apk" | cut -d ' ' -f 1)" != a0765f28cd526dace8e9670ce86ecf8fbc8ccd9a6b51c7b63eb93c99e4ac2713 ]; then
        cat "$market_target" "$mg/market-apk-tail.bin" > "$mg/Market.apk.tmp" || { mg_fail build; return 1; }
        [ "$(sha256sum "$mg/Market.apk.tmp" | cut -d ' ' -f 1)" = a0765f28cd526dace8e9670ce86ecf8fbc8ccd9a6b51c7b63eb93c99e4ac2713 ] || { mg_fail candidate; return 1; }
        chmod 644 "$mg/Market.apk.tmp"
        chcon u:object_r:system_file:s0 "$mg/Market.apk.tmp" || { mg_fail label; return 1; }
        mv "$mg/Market.apk.tmp" "$mg/Market.apk" || { mg_fail rename; return 1; }
    fi
    run_am force-stop com.heytap.market || { mg_fail stop; return 1; }
    mount -o bind "$mg/Market.apk" "$market_target" || { mg_fail bind; return 1; }
    mg_ro=1
    for mg_try in 1 2 3 4 5; do
        mount -o remount,bind,ro "$market_target" && { mg_ro=0; break; }
        sleep 3
    done
    if [ "$mg_ro" = 1 ]; then
        # The patched APK stays bound (update protection active); only the
        # read-only hardening could not be applied while PMS still holds it.
        echo R91_ROM_MARKET_GUARD_READONLY_PENDING
    fi
    [ "$(sha256sum "$market_target" | cut -d ' ' -f 1)" = a0765f28cd526dace8e9670ce86ecf8fbc8ccd9a6b51c7b63eb93c99e4ac2713 ] || { mg_fail invisible; return 1; }
    CLASSPATH="$mg/guard.dex" app_process /system/bin R93PatchGuard apply || { mg_fail policy; return 1; }
    echo R91_ROM_MARKET_GUARD_BOUND_AND_POLICY_READBACK_OK
    return 0
}
if [ "$(sha256sum "$market_target" 2>/dev/null | cut -d ' ' -f 1)" = 391a2fb1e9bd5d22331656b44d42837ef9048ab754b1a72996f24daeb0a49179 ]; then
    do_market_guard || echo R91_ROM_MARKET_GUARD_SKIPPED
else
    echo R91_ROM_MARKET_BASE_CHANGED_SKIP
fi

echo "R91_ROM_BINDS_OK $(date)"

# SetupWizard owns the screen until the user finishes it. No device_provisioned
# or user_setup_complete setting is written by this service.
while [ "$(settings get secure user_setup_complete)" != 1 ]; do sleep 3; done

sh /system_ext/etc/r94-native/module-delivery/delivery.sh reconcile || echo R94_MODULE_DELIVERY_PENDING
# SetupWizard can reset density/display size. Commit defaults only after it
# finishes, exactly once; subsequent boots preserve the user's adjustments.
if [ "$first_defaults" = 1 ]; then
    apply_defaults
    touch "$base/defaults-v1-complete"
    echo "R91_ROM_DEFAULTS_COMMITTED $(date)"
fi
cmd package set-home-activity --user 0 com.android.launcher/.Launcher
sh /system/etc/r94-camera-v7/install-once.sh || echo R94_CAMERA_PRELOAD_PENDING

echo "R91_ROM_READY launcher_native=1 $(date)"
