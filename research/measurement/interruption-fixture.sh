#!/system/bin/sh
# One owned recorder, explicit phase markers, complete 12-launch coverage.
# Existing verified landscape home: Bili (2334,505), Douyin (2679,505).
set -eu
TAG=${1:?run tag required}
MODE=${2:-normal}
case "$TAG" in *[!A-Za-z0-9_-]*) exit 2;; esac
case "$MODE" in normal|rapid|rapid4|daily4|rapidheavy4) ;; *) exit 2;; esac
ROUNDS=${3:-3}
case "$ROUNDS" in 1|2|3) ;; *) exit 2;; esac
OUT=/data/misc/perfetto-traces/codex_${TAG}.pftrace
MARKER=/sys/kernel/tracing/trace_marker
[ -w "$MARKER" ] || MARKER=/sys/kernel/debug/tracing/trace_marker
[ -w "$MARKER" ] || { echo 'trace marker unavailable'; exit 1; }
mark() { echo "B|$$|$1" > "$MARKER"; }
end() { echo "E|$$" > "$MARKER"; }
cleanup() {
  dumpsys SurfaceFlinger --timestats -disable >/dev/null
  if [ -n "${REC_PID:-}" ]; then kill -INT "$REC_PID" 2>/dev/null || true; wait "$REC_PID" 2>/dev/null || true; fi
  if [ -f "/data/local/tmp/codex_${TAG}_kgsl_restore" ]; then
    while read -r path value; do echo "$value" > "$path"; done < "/data/local/tmp/codex_${TAG}_kgsl_restore"
    rm -f "/data/local/tmp/codex_${TAG}_kgsl_restore"
  fi
}
trap cleanup EXIT INT TERM

input keyevent KEYCODE_WAKEUP
wm dismiss-keyguard
sleep 2
perfetto --txt -c "${CODEX_TRACE_CONFIG:-/data/local/tmp/codex_launch.cfg}" -o "$OUT" >/data/local/tmp/codex_${TAG}_recorder.log 2>&1 &
REC_PID=$!
sleep 1
kill -0 "$REC_PID"
if [ "${CODEX_ENABLE_KGSL:-0}" = 1 ]; then
  : > "/data/local/tmp/codex_${TAG}_kgsl_restore"
  for event in adreno_cmdbatch_queued adreno_cmdbatch_submitted adreno_cmdbatch_retired adreno_drawctxt_wait_start adreno_drawctxt_wait_done; do
    path="/sys/kernel/tracing/events/kgsl/$event/enable"
    echo "$path $(cat "$path")" >> "/data/local/tmp/codex_${TAG}_kgsl_restore"
    echo 1 > "$path"
  done
fi
dumpsys SurfaceFlinger --timestats -clear
dumpsys SurfaceFlinger --timestats -enable
mark "fixture|$MODE|$TAG"
for round in $(seq 1 "$ROUNDS"); do
  if [ "$MODE" = normal ] || [ "$MODE" = daily4 ] || [ "$MODE" = rapidheavy4 ]; then
    am force-stop tv.danmaku.bili
    am force-stop com.ss.android.ugc.aweme
    if [ "$MODE" = daily4 ] || [ "$MODE" = rapidheavy4 ]; then am force-stop com.tencent.mm; am force-stop com.tencent.mobileqq; fi
    sleep 1
  fi
  ITEMS='bili_cold douyin_cold bili_warm douyin_warm'
  if [ "$MODE" = rapid4 ] || [ "$MODE" = daily4 ] || [ "$MODE" = rapidheavy4 ]; then ITEMS='wechat qq bili douyin'; fi
  for item in $ITEMS; do
    y=505
    case "$item" in wechat) x=1644; y=505;; qq) x=1989; y=505;; bili*) x=2334;; douyin*) x=2679;; esac
    mark "open|$round|$item"
    input tap "$x" "$y"
    if [ "$MODE" = normal ] || [ "$MODE" = daily4 ]; then sleep 3.5; else sleep 0.22; fi
    end
    if [ "$MODE" = daily4 ]; then
      echo "daily_activity $round $item"
      dumpsys activity activities | sed -n '/topResumedActivity=/p'
    fi
    mark "return|$round|$item"
    input swipe 1472 1835 1472 900 120
    if [ "$MODE" = normal ] || [ "$MODE" = daily4 ]; then sleep 2; else sleep 0.44; fi
    end
  done
done
end
sleep 1
dumpsys SurfaceFlinger --timestats -dump > /data/local/tmp/v23-timestats.txt
kill -0 "$REC_PID" || { echo 'recorder ended before fixture'; exit 1; }
cleanup
REC_PID=
trap - EXIT INT TERM
echo "fixture completed: tag=$TAG mode=$MODE expected_attempts=$((4*ROUNDS))"
ls -l "$OUT"
