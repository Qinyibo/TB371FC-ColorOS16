CREATE PERFETTO TABLE attempts AS
SELECT name,ts,dur,
 lead(ts,1,(SELECT end_ts FROM trace_bounds)) OVER (ORDER BY ts) end_ts,
 CASE WHEN name LIKE '%|wechat' THEN 'com.tencent.mm' WHEN name LIKE '%|qq' THEN 'com.tencent.mobileqq'
 WHEN name LIKE '%|bili' THEN 'tv.danmaku.bili' WHEN name LIKE '%|douyin' THEN 'com.ss.android.ugc.aweme' END package
FROM slice WHERE name GLOB 'open|*';
SELECT a.name,
 count(s.id) requests_before_next_tap,
 round(min(s.ts-a.ts)/1e6,2) first_request_after_tap_ms
FROM attempts a LEFT JOIN slice s ON s.name='launching: '||a.package AND s.ts>=a.ts AND s.ts<a.end_ts
GROUP BY a.name ORDER BY a.ts;
