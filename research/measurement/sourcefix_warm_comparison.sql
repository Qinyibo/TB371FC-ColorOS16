CREATE PERFETTO TABLE warm_window AS
SELECT min(ts) ts,max(ts+dur) end_ts FROM slice WHERE
 name GLOB 'open|[23]|*' OR name GLOB 'return|[23]|*';
SELECT p.name package,t.name thread,
 CASE WHEN s.name LIKE 'Choreographer#doFrame %' THEN 'UI frame'
 WHEN s.name LIKE 'dispatchInputEvent MotionEvent ACTION_%' THEN 'Touch dispatch'
 ELSE s.name END operation,
 count(*) n,round(percentile(s.dur,95)/1e6,2) p95_ms,round(max(s.dur)/1e6,2) max_ms
FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid),warm_window w
WHERE s.ts>=w.ts AND s.ts<w.end_ts AND s.dur>0
 AND p.name IN ('com.android.launcher','com.android.systemui')
 AND ((s.name LIKE 'Choreographer#doFrame %' AND s.name NOT LIKE 'Choreographer#doFrame -%')
 OR (p.name='com.android.launcher' AND s.name LIKE 'dispatchInputEvent MotionEvent ACTION_%')
 OR s.name='RecentTasksList#getRecentTasks' OR (t.name='wmshell.main' AND s.name='binder transaction'))
GROUP BY p.name,t.name,operation ORDER BY package,operation,thread;
SELECT count(*) monitor_waits_over20ms,round(max(s.dur)/1e6,2) max_monitor_wait_ms
FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid),warm_window w
WHERE p.name='system_server' AND s.ts>=w.ts AND s.ts<w.end_ts AND s.dur>20000000
 AND s.name LIKE 'monitor contention with owner%';
