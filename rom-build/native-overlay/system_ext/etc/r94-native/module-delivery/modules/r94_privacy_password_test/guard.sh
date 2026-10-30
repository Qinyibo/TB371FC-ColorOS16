# Sourced by the candidate controller. No credential reads or writes here.
r94_fail() { printf '%s\n' "R94_PRIVACY_STOP:$1" >&2; return 1; }
r94_ordinary() {
    test ! -L "$1" || return 1
    test -e "$1" || return 1
    case "$(stat -c '%u:%a' "$1")" in 0:700|0:600) return 0;; *) return 1;; esac
}
r94_gate() {
    test "$(id -u)" = 0 || { r94_fail root_required; return 1; }
    test "$(getprop ro.product.board)" = spinel || { r94_fail wrong_board; return 1; }
    test "$(getenforce)" = Enforcing || { r94_fail enforcing_required; return 1; }
    test "$(sha256sum /system/framework/oplus-framework.jar | cut -d ' ' -f 1)" = c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99 || { r94_fail framework_changed; return 1; }
    test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || { r94_fail module_disabled; return 1; }
    for service_name in default r94prod r94_pms r94_gate r94_gate2; do
        answer=$(service check "vendor.oplus.hardware.cryptoeng.ICryptoeng/$service_name" 2>&1) || { r94_fail service_query_error; return 1; }
        case "$answer" in "Service vendor.oplus.hardware.cryptoeng.ICryptoeng/$service_name: not found") ;; *) r94_fail service_conflict; return 1;; esac
    done
    serial=$(getprop ro.boot.serialno)
    case "$serial" in ''|unknown|*[!A-Za-z0-9_-]*) r94_fail missing_device_identity; return 1;; esac
    test "${#serial}" -ge 4 && test "${#serial}" -le 64 || { r94_fail invalid_device_identity; return 1; }
    SERIAL_DIGEST=$(printf '%s' "$serial" | sha256sum | cut -d ' ' -f 1)
    export R94_PMS_DEVICE_SERIAL="$serial"
    return 0
}
r94_profile_check() {
    if test -e "$STATE"; then
        r94_ordinary "$STATE" && test -d "$STATE" || { r94_fail state_owner_or_mode; return 1; }
        r94_ordinary "$STATE/profile" && test -f "$STATE/profile" || { r94_fail unrecognized_existing_store; return 1; }
        expected=$(printf 'R94_PMS_SOFTWARE_PRIVACY_V1\n%s\n%s' "$BACKEND_SHA" "$SERIAL_DIGEST")
        actual=$(cat "$STATE/profile")
        test "$actual" = "$expected" || { r94_fail store_identity_or_backend_changed; return 1; }
        for name in d p r; do r94_ordinary "$STATE/$name" && test -d "$STATE/$name" || { r94_fail unsafe_store_directory; return 1; }; done
        links=$(find "$STATE" -type l) || { r94_fail store_scan_failed; return 1; }
        test -z "$links" || { r94_fail store_symlink; return 1; }
        attrs=$(find "$STATE" -type f -exec stat -c '%u:%a:%h' {} \;) || { r94_fail store_stat_failed; return 1; }
        for attr in $attrs; do test "$attr" = 0:600:1 || { r94_fail unsafe_store_file; return 1; }; done
    fi
    return 0
}
