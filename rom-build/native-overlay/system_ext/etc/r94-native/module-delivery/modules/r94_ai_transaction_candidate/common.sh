#!/system/bin/sh
state_of() {
    local query state
    query=$(mktemp "$MODDIR/query.XXXXXX") || return 1
    # Avoid Android external printf's single-argument limit for large dumps.
    if ! dumpsys package "$1" > "$query" 2>&1; then
        rm -f "$query"; return 1
    fi
    if state=$(awk '
      /User 0:.* enabled=/ {
        count++
        for (i=1;i<=NF;i++) if ($i ~ /^enabled=[0-4]$/) {value=substr($i,9); fields++}
      }
      END {if (count==1 && fields==1) print value; else exit 1}
    ' "$query"); then
        rm -f "$query"
        printf '%s\n' "$state"
        return 0
    fi
    # Absence must be explicit; malformed/truncated/Binder failures are errors.
    if grep -Fq "Unable to find package: $1" "$query"; then
        rm -f "$query"; return 0
    fi
    rm -f "$query"
    return 1
}
allowed() {
    case "$1" in
      com.heytap.speechassist|com.oplus.aimemory|com.coloros.translate|com.coloros.translate.engine|com.oplus.aiunit|com.aiunit.aon|com.oplus.obrain) return 0;;
      *) return 1;;
    esac
}
run_pm() {
    local result rc=0
    result=$(pm "$@" 2>&1) || rc=$?
    printf '%s\n' "$result"
    return "$rc"
}
validate_backup() {
    [ -f "$MODDIR/state.txt" ] || return 0
    local pkg old extra seen=' '
    while read -r pkg old extra; do
        [ -n "$pkg" ] && [ -z "$extra" ] || return 1
        allowed "$pkg" || return 1
        case "$old" in 0|1) ;; *) return 1;; esac
        case "$seen" in *" $pkg "*) return 1;; esac
        seen="$seen$pkg "
    done < "$MODDIR/state.txt"
}
acquire_lock() {
    mkdir "$MODDIR/.operation-lock" 2>/dev/null || { echo OPERATION_BUSY; exit 30; }
    trap 'rm -f "$MODDIR/state.next"; rmdir "$MODDIR/.operation-lock"' EXIT
}
restore_locked() {
    local pkg old current desired rc=0
    validate_backup || { echo INVALID_BACKUP; return 25; }
    [ -f "$MODDIR/state.txt" ] || return 0
    : > "$MODDIR/state.next" || return 26
    while read -r pkg old; do
        if ! current=$(state_of "$pkg"); then
            printf '%s %s\n' "$pkg" "$old" >> "$MODDIR/state.next" || return 26
            echo "RESTORE_QUERY_FAILED:$pkg"; rc=26; continue
        fi
        if [ "$current" != 3 ]; then
            echo "USER_STATE_PRESERVED:$pkg:$current"; continue
        fi
        if [ "$old" = 0 ]; then desired=default-state; else desired=enable; fi
        if run_pm "$desired" --user 0 "$pkg"; then
            current=$(state_of "$pkg") || current=unknown
        else
            current=unknown
        fi
        if [ "$current" = "$old" ]; then
            echo "RESTORED:$pkg:$old"
        else
            printf '%s %s\n' "$pkg" "$old" >> "$MODDIR/state.next" || return 26
            echo "RESTORE_PENDING:$pkg:$old"; rc=26
        fi
    done < "$MODDIR/state.txt"
    mv "$MODDIR/state.next" "$MODDIR/state.txt" || return 26
    return "$rc"
}
