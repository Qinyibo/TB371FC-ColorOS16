#!/system/bin/sh

# Temporary, event-driven capture. Runs as shell and never changes display,
# suspend, or kernel settings. The caller gives it a new private directory.
set -eu
umask 077
directory=$1
duration=$2
log=$directory/wake.log
boot=$(cat /proc/sys/kernel/random/boot_id)
marker=$directory/last-kernel-time
printf '%s\n' 0 > "$marker"
[ ! -f "$log" ] || mv -f "$log" "$directory/wake.previous.log"
printf '%s BOOT %s %s\n' "$(date -Iseconds)" "$boot" "$(uname -v)" > "$log"

snapshot() {
    last=$(cat "$marker")
    # Capture the narrow display/touch path, including the first failure data.
    if dmesg | awk -v last="$last" -v marker="$marker" '
        /^\[/ && /R94_|R97_DIAG|R10[478]_|R10x_FORCE_REK|LCD bias|PANEL_DEAD|crc_done|fw history|nvt_ts_(suspend|pm_suspend|pm_resume)|nvt_(read_fw_history|check_fw_reset_state)|PM: suspend (entry|exit)|DSI PLL.*lock failed|hactive=/ {
            t = substr($0, 2, index($0, "]") - 2) + 0
            if (t > last) {
                print
                newest = t
                if (/PREPANEL_FW_FAILED|REK_FAILED|PANEL_DEAD/) failed = 1
            }
        }
        END {
            if (newest > last) printf "%.6f\n", newest > marker
            if (failed) exit 2
        }
    ' >> "$log"; then
        :
    else
        status=$?
        if [ "$status" -ne 2 ]; then return "$status"; fi
        sync
    fi
    # Protect the private directory from unbounded output even in a wake loop.
    if [ "$(wc -c < "$log")" -gt 2097152 ]; then
        mv -f "$log" "$directory/wake.previous.log"
        printf '%s CONTINUE %s\n' "$(date -Iseconds)" "$boot" > "$log"
    fi
}

snapshot
events() {
    if [ "$duration" = 0 ]; then
        logcat -b system -v brief -T 1 -s PowerManagerService:I '*:S'
    else
        timeout "$duration" logcat -b system -v brief -T 1 -s PowerManagerService:I '*:S'
    fi
}
events |
while IFS= read -r line; do
    case "$line" in
        *'Waking up from '*)
            reason=$(printf '%s\n' "$line" | sed -n 's/.*reason=\(WAKE_REASON_[A-Z_]*\).*/\1/p')
            case "$line" in *OplusLeatherCaseMode*) reason="${reason:-unknown} leather_case" ;; esac
            printf '%s WAKE %s\n' "$(date -Iseconds)" "${reason:-unknown}" >> "$log"
            snapshot
            sleep 2
            snapshot
            sleep 3
            snapshot
            ;;
        *'Going to sleep due to '*)
            printf '%s SLEEP\n' "$(date -Iseconds)" >> "$log"
            snapshot
            sleep 1
            snapshot
            ;;
    esac
done
printf '%s STOP\n' "$(date -Iseconds)" >> "$log"
