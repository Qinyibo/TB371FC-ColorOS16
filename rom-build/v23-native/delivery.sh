#!/system/bin/sh
set -eu
if test "${2:-}" != --ash; then
    exec /data/adb/magisk/busybox sh "$0" "${1:-reconcile}" --ash
fi
export PATH=/system/bin:/system/xbin:/debug_ramdisk
source=/system_ext/etc/r94-native/module-delivery
state=/data/adb/r94-module-delivery
test "$(getprop ro.product.board)" = spinel
test "$(getprop ro.build.version.sdk)" = 36
test ! -L "$state"
umask 077
mkdir -p "$state"
exec 8>"$state/boot.lock"
flock -n 8 || exit 0
(cd "$source"; sha256sum -c SHA256SUMS) > "$state/assets-check.txt" 2>&1
seed_modules() {
    test ! -L /data/adb/modules
    mkdir -p /data/adb/modules
    if test ! -e "$state/seed-v1-complete"; then
        for name in r94_ai_transaction_candidate r94_speaker_direction r94_foreground_schedtune r94_privacy_password_test; do
            target=/data/adb/modules/$name
            test ! -L "$target"
            if test ! -e "$target" && test ! -e "/data/adb/modules_update/$name"; then
                stage="$state/stage-$name"
                test ! -e "$stage" && test ! -L "$stage"
                cp -a "$source/modules/$name" "$stage"
                chown -R 0:0 "$stage"
                find "$stage" -type d -exec chmod 755 {} \;
                find "$stage" -type f -exec chmod 644 {} \;
                chmod 755 "$stage"/*.sh
                if test -f "$stage/directionctl"; then
                    chmod 755 "$stage/directionctl"
                fi
                if test "$name" = r94_privacy_password_test; then
                    for binary in pms-backing pms-gateway owner-back owner-gate; do
                        chmod 755 "$stage/bin/$binary"
                    done
                fi
                chcon -R u:object_r:system_file:s0 "$stage"
                mv "$stage" "$target"
                echo "MODULE_FIRST_INSTALL:$name"
            fi
        done
        touch "$state/seed-v1-complete"
    fi
}
case "${1:-reconcile}" in
    provision-market)
        target=/data/adb/r94-marketguard
        test ! -L "$target"
        mkdir -p "$target"
        for f in guard.dex market-apk-tail.bin; do
            test ! -L "$target/$f"
            if test ! -e "$target/$f"; then
                cp "$source/market-guard/$f" "$target/$f.next"
                chmod 600 "$target/$f.next"
                mv "$target/$f.next" "$target/$f"
            fi
            test "$(sha256sum "$target/$f" | cut -d ' ' -f 1)" = "$(sha256sum "$source/market-guard/$f" | cut -d ' ' -f 1)"
        done
        echo MARKET_ASSETS_PROVISIONED
        ;;
    seed-only)
        seed_modules
        echo MODULE_SEED_COMPLETE
        ;;
    reconcile)
        test "$(getprop sys.boot_completed)" = 1
        setup=$(settings get secure user_setup_complete 2>&1)
        test "$setup" = 1
        seed_modules
        ai=/data/adb/modules/r94_ai_transaction_candidate
        if test -f "$ai/module.prop"; then
            if test -e "$ai/disable" || test -e "$ai/remove"; then
                sh "$ai/restore.sh" 8>&- || echo AI_RESTORE_PENDING
            else
                sh "$ai/service.sh" 8>&- || echo AI_APPLY_PENDING
            fi
        fi
        speaker=/data/adb/modules/r94_speaker_direction
        if test -f "$speaker/module.prop" && test ! -e "$speaker/disable" && test ! -e "$speaker/remove"; then
            nohup sh "$speaker/service.sh" 8>&- >/dev/null 2>&1 </dev/null &
        fi
        scheduler=/data/adb/modules/r94_foreground_schedtune
        if test -f "$scheduler/module.prop"; then
            sh "$scheduler/control.sh" reconcile 8>&- || echo SCHEDULER_CONTROL_PENDING
        fi
        # Bili/WeChat rules are native ROM configuration; no rules watcher.
        privacy=/data/adb/modules/r94_privacy_password_test
        if test -f "$privacy/module.prop" && test ! -e "$privacy/disable" && test ! -e "$privacy/remove"; then
            nohup sh "$privacy/service.sh" 8>&- >/dev/null 2>&1 </dev/null &
        fi
        sh "$source/comm-defaults.sh" 8>&- || echo R94_COMM_DEFAULTS_PENDING
        echo MODULE_DELIVERY_RECONCILED
        ;;
    *) exit 2;;
esac
