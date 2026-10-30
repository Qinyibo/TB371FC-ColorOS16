CREATE PERFETTO TABLE attempts AS
SELECT id,name,ts,dur FROM slice WHERE name GLOB 'open|*';
CREATE PERFETTO TABLE app_input AS
SELECT s.ts,s.dur,s.name,p.name package,t.name thread
FROM slice s JOIN thread_track tt ON tt.id=s.track_id
JOIN thread t USING(utid) JOIN process p USING(upid)
WHERE s.name LIKE 'dispatchInputEvent MotionEvent ACTION_UP%';
SELECT a.name attempt,group_concat(DISTINCT i.package) touch_up_delivered_to,
 round(max(i.dur)/1e6,2) max_dispatch_ms
FROM attempts a LEFT JOIN app_input i ON i.ts>=a.ts AND i.ts<a.ts+a.dur
GROUP BY a.id ORDER BY a.ts;
SELECT p.name package,s.name,count(*) n,round(max(s.dur)/1e6,2) max_ms
FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid)
WHERE s.name LIKE 'performResume:%' OR (p.name='com.android.launcher' AND (s.name LIKE '%onClick%' OR s.name LIKE '%startActivity%'))
GROUP BY p.name,s.name ORDER BY n DESC LIMIT 20;
