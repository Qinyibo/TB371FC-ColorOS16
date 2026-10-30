#!/system/bin/sh
set -eu
MODDIR=${0%/*}
STATE=/data/adb/r94-speaker-direction-v19
touch "$MODDIR/disable"
test ! -L "$STATE" || exit 20
mkdir -p "$STATE"
if test -f "$STATE/owner.txt"; then
 boot=$(head -n 1 "$STATE/owner.txt"); pid=$(tail -n 1 "$STATE/owner.txt")
 case "$pid" in ''|*[!0-9]*) exit 20;; esac
 if test "$boot" = "$(cat /proc/sys/kernel/random/boot_id)" && test -d "/proc/$pid"; then
  cmd=$(tr '\000' ' ' < "/proc/$pid/cmdline")
  env=$(tr '\000' '\n' < "/proc/$pid/environ" | grep '^CLASSPATH=')
  case "$cmd" in *R94SpeakerDirection*"$MODDIR/direction.so"*) ;; *) exit 20;; esac
  test "$env" = "CLASSPATH=$MODDIR/direction.jar" || exit 20
  touch "$STATE/stop"
  kill -TERM "$pid" 2>/dev/null || test ! -d "/proc/$pid"
  n=0; while test -d "/proc/$pid"; do
   n=$((n+1)); test "$n" -le 50 || { echo SPEAKER_STOP_PENDING; exit 21; }; sleep 0.1
  done
 fi
 # Give the supervisor its short post-exit recovery window. A stale owner
 # record never skips recovery and never causes an unrelated PID kill.
 n=0; while test -f "$STATE/owner.txt" && test "$n" -lt 20; do n=$((n+1)); sleep 0.1; done
fi
"$MODDIR/directionctl" --restore
rm -f "$STATE/owner.txt"
echo 四扬旋转已停用，驱动已确认释放本次声道和静音占用
