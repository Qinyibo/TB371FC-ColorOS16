# Sourced after the existing identity, service-conflict and binary guards.
# Only the already audited policy is used; credentials are never accessed here.
r94_policy_types_ready() {
    r94_probe=$(mktemp -d /data/adb/r94-pms-policy-probe.XXXXXX) || return 1
    r94_types_rc=0
    for r94_kind in exec gate data; do : > "$r94_probe/$r94_kind" || r94_types_rc=1; done
    chcon u:object_r:r94_pms_exec:s0 "$r94_probe/exec" 2>/dev/null || r94_types_rc=1
    chcon u:object_r:r94_pms_gate_exec:s0 "$r94_probe/gate" 2>/dev/null || r94_types_rc=1
    chcon u:object_r:r94_pms_data:s0 "$r94_probe/data" 2>/dev/null || r94_types_rc=1
    rm -f "$r94_probe/exec" "$r94_probe/gate" "$r94_probe/data"
    rmdir "$r94_probe" || r94_types_rc=1
    return "$r94_types_rc"
}

r94_policy_clean() {
    rm -f "$r94_work/base.policy" "$r94_work/candidate.policy" "$r94_work/compile.log" "$r94_work/apply.log"
    rmdir "$r94_work"
}

r94_policy_prepare() {
    test "${MODDIR:-}" = /data/adb/modules/r94_privacy_password_test || return 20
    test "$(id -u)" = 0 && test "$(getenforce)" = Enforcing || return 20
    test ! -e "$MODDIR/disable" && test ! -e "$MODDIR/remove" || return 20
    test ! -L "$MODDIR/sepolicy.rule" || return 20
    test "$(stat -c '%u:%a:%h' "$MODDIR/sepolicy.rule")" = 0:644:1 || return 20
    test "$(sha256sum "$MODDIR/sepolicy.rule" | cut -d ' ' -f 1)" = 8dac80d4b01c06aa4f0abf469ed99d5a2c0972f724e6a6f60b316e1ede5a1a50 || return 20
    # An ordinary later boot must not rewrite a policy already containing the types.
    if r94_policy_types_ready; then
        printf '%s\n' R94_PRIVACY_POLICY_ALREADY_PRESENT
        return 0
    fi
    test "$(magisk -V)" = 30700 && test -x /debug_ramdisk/magiskpolicy || return 20
    r94_work=$(mktemp -d /data/adb/r94-pms-policy-compile.XXXXXX) || return 20
    if ! cat /sys/fs/selinux/policy > "$r94_work/base.policy"; then r94_policy_clean; return 20; fi
    r94_base_sha=$(sha256sum "$r94_work/base.policy" | cut -d ' ' -f 1)
    if ! /debug_ramdisk/magiskpolicy --load "$r94_work/base.policy" --apply "$MODDIR/sepolicy.rule" --save "$r94_work/candidate.policy" > "$r94_work/compile.log" 2>&1; then
        r94_policy_clean; return 20
    fi
    if test ! -s "$r94_work/candidate.policy" || grep -Eiq 'failed|invalid|error|not found' "$r94_work/compile.log"; then
        r94_policy_clean; return 20
    fi
    # Reject an observed concurrent policy change. The live apply below merges
    # into its own current snapshot; no saved old policy is loaded over new work.
    if test "$(sha256sum /sys/fs/selinux/policy | cut -d ' ' -f 1)" != "$r94_base_sha" ||
       test "$(getenforce)" != Enforcing || test -e "$MODDIR/disable" || test -e "$MODDIR/remove"; then
        r94_policy_clean; return 20
    fi
    if ! /debug_ramdisk/magiskpolicy --live --apply "$MODDIR/sepolicy.rule" > "$r94_work/apply.log" 2>&1; then
        r94_policy_clean; return 20
    fi
    if grep -Eiq 'failed|invalid|error|not found' "$r94_work/apply.log" ||
       test "$(getenforce)" != Enforcing || ! r94_policy_types_ready; then
        r94_policy_clean; return 20
    fi
    r94_policy_clean || return 20
    printf '%s\n' R94_PRIVACY_POLICY_FIRST_START_READY
}
