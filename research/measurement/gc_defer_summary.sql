CREATE PERFETTO TABLE phases AS SELECT name,ts,dur FROM slice WHERE name GLOB 'open|[23]|*' OR name GLOB 'return|[23]|*';
SELECT count(*) sf_frames,sum(a.present_type='On-time Present') sf_on_time,sum(a.jank_type LIKE '%GPU Deadline%') sf_gpu_deadline,sum(a.present_type='Dropped Frame') sf_dropped,round(percentile(a.dur,95)/1e6,2) sf_latency95_ms,round(max(a.dur)/1e6,2) sf_latency_max_ms
FROM actual_frame_timeline_slice a JOIN process p USING(upid) WHERE p.name='/system/bin/surfaceflinger' AND a.dur>0 AND EXISTS(SELECT 1 FROM phases q WHERE a.ts>=q.ts AND a.ts<q.ts+q.dur);
SELECT p.name,round(sum(min(sc.ts+sc.dur,q.ts+q.dur)-max(sc.ts,q.ts))/1e6,1) heap_daemon_cpu_ms
FROM sched sc JOIN thread t USING(utid) JOIN process p USING(upid) JOIN phases q ON sc.ts<q.ts+q.dur AND sc.ts+sc.dur>q.ts
WHERE sc.dur>0 AND t.name='HeapTaskDaemon' AND p.name IN('com.tencent.mm','com.tencent.mobileqq','tv.danmaku.bili','com.ss.android.ugc.aweme') GROUP BY p.name;
SELECT p.name,count(*) transition_gc_events,round(max(s.dur)/1e6,2) longest_transition_ms
FROM slice s JOIN thread_track tt ON s.track_id=tt.id JOIN thread t USING(utid) JOIN process p USING(upid)
WHERE s.name LIKE 'CollectorTransition %GC' AND s.dur>0 AND p.name IN('com.tencent.mm','com.tencent.mobileqq','tv.danmaku.bili','com.ss.android.ugc.aweme') AND EXISTS(SELECT 1 FROM phases q WHERE s.ts<q.ts+q.dur AND s.ts+s.dur>q.ts)
GROUP BY p.name;
