CREATE PERFETTO TABLE phases AS SELECT id,name,ts,dur FROM slice WHERE name GLOB 'open|[23]|*' OR name GLOB 'return|[23]|*';
SELECT count(*) phases,sum(dur<0) incomplete FROM phases;
SELECT p.name,a.present_type,a.jank_type,count(*) n,round(percentile(a.dur,95)/1e6,2) latency95_ms,round(max(a.dur)/1e6,2) latency_max_ms
FROM actual_frame_timeline_slice a JOIN process p USING(upid)
WHERE p.name IN('/system/bin/surfaceflinger','com.android.launcher','com.android.systemui') AND a.dur>0
AND EXISTS(SELECT 1 FROM phases q WHERE a.ts>=q.ts AND a.ts<q.ts+q.dur)
GROUP BY p.name,a.present_type,a.jank_type ORDER BY p.name,n DESC;
SELECT count(*) attempts,sum(exists(SELECT 1 FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid) WHERE p.name='com.android.launcher' AND s.name LIKE 'dispatchInputEvent MotionEvent ACTION_UP%' AND s.ts>=q.ts AND s.ts<q.ts+q.dur)) delivered_to_launcher FROM phases q WHERE q.name GLOB 'open|*';
SELECT p.name,s.name,count(*) n FROM slice s JOIN thread_track tt ON tt.id=s.track_id JOIN thread t USING(utid) JOIN process p USING(upid) WHERE s.name LIKE 'performResume:%' GROUP BY p.name,s.name;
CREATE PERFETTO TABLE cpu_delta AS SELECT name,cpu,value-lag(value) OVER(PARTITION BY c.track_id ORDER BY ts) delta FROM counter c JOIN cpu_counter_track ct ON c.track_id=ct.id WHERE name GLOB 'cpu.times.*';
SELECT round(sum(CASE WHEN name='cpu.times.idle_ns' THEN delta ELSE 0 END)*100.0/sum(delta),2) cpu_idle_percent FROM cpu_delta WHERE delta>=0;
SELECT name,value FROM stats WHERE value>0 AND (severity='data_loss' OR severity='error');
