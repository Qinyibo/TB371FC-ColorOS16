"""24-hour PC-only diagnostics. No tablet input, wake, reset or property writes."""
from pathlib import Path
import argparse,concurrent.futures,ctypes,datetime,json,os,queue,re,shutil,subprocess,threading,time

DEATH=re.compile(rb'Process com\.android\.systemui \(pid \d+\) has died')
def now():return datetime.datetime.now().isoformat()
def metadata(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    try:tmp.replace(path)
    except PermissionError:pass # An open Windows status reader must not stop acquisition.

class Ring:
    def __init__(self,root,chunk=32*1024*1024,slots=8):
        self.root=root;root.mkdir();self.chunk=chunk;self.slots=slots;self.slot=0;self.file=None;self.size=0;self.total=0
    def write(self,line):
        if self.file is None or self.size+len(line)>self.chunk:
            if self.file:self.file.close()
            self.file=(self.root/('part-%02d.log'%self.slot)).open('wb');self.slot=(self.slot+1)%self.slots;self.size=0
        self.file.write(line);self.file.flush();self.size+=len(line);self.total+=len(line)
    def freeze(self,target):
        target.mkdir()
        files=sorted(self.root.glob('part-*.log'),key=lambda p:p.stat().st_mtime_ns)[-2:]
        for f in files:shutil.copyfile(f,target/f.name)
        metadata(target/'order.json',{'host':now(),'oldest_first':[f.name for f in files]})
    def close(self):
        if self.file:self.file.close()

def reasons_for(line,health,previous):
    reasons=[]
    if line and DEATH.search(line):reasons.append('systemui_process_died')
    if health:
        if 'failed=1' in health and (previous is None or 'failed=1' not in previous):reasons.append('touch_failed')
        b=re.search(r'BOOT=(\S+)',health);old=re.search(r'BOOT=(\S+)',previous or '')
        if b and old and b[1]!=old[1]:reasons.append('device_boot_changed')
    return reasons

def cleanup_command(pid):
    if not pid.isdecimal():raise ValueError('Expected numeric owned reader PID')
    return "p="+pid+r"""; c=$(tr '\000' ' ' </proc/$p/cmdline 2>/dev/null); case "$c" in *logcat*) kill -TERM $p;; esac"""

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--adb',required=True);parser.add_argument('--serial',required=True)
    parser.add_argument('--out',required=True);parser.add_argument('--hours',type=float,default=24)
    args=parser.parse_args();root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=False)
    if shutil.disk_usage(root).free<3*1024**3:raise RuntimeError('At least 3 GiB free space required')
    snapshots=root/'snapshots';snapshots.mkdir();incidents=root/'incidents';incidents.mkdir()
    start=time.monotonic();deadline=start+max(0.01,min(args.hours,24))*3600;adb=[args.adb,'-s',args.serial]
    status={'started':now(),'planned_end':datetime.datetime.fromtimestamp(time.time()+deadline-start).isoformat(),'read_only':True,'tablet_input_wake_reboot':False,'state':'starting','incidents':0}
    awake=False
    if os.name=='nt':awake=bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001))
    status['pc_sleep_inhibited_for_this_process']=awake
    def save(**values):status.update(values);status.update(updated=now(),bytes=ring.total);metadata(root/'status.json',status)
    def event(kind,**details):
        with (root/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'host':now(),'event':kind,**details},ensure_ascii=False)+'\n')
    def read(command,timeout=12):
        began=now()
        try:
            q=subprocess.run(adb+['shell',command],capture_output=True,timeout=timeout)
            return {'started':began,'finished':now(),'rc':q.returncode,'stdout':q.stdout.decode('utf-8',errors='replace'),'stderr':q.stderr.decode('utf-8',errors='replace')}
        except subprocess.TimeoutExpired as exc:return {'started':began,'finished':now(),'timeout':timeout,'stdout':(exc.stdout or b'').decode('utf-8',errors='replace')}
    def snapshot(full=False):
        commands={'input':'dumpsys input','window':'dumpsys window','power':'dumpsys power','touch_service':'dumpsys activity service com.android.launcher/com.android.quickstep.TouchInteractionService'}
        if full:commands.update(kernel="su -mm -c 'dmesg'",display='dumpsys display',exit_info='dumpsys activity exit-info com.android.systemui')
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(lambda item:(item[0],read(item[1],25)),commands.items()))
        return {'host':now(),'read_only':True,'results':dict(results),'health':last_health}
    ring=Ring(root/'log-ring');events=queue.Queue(maxsize=20000);proc=None;remote_pid=None;generation=0
    last_health=None;next_probe=0;next_snapshot=0;next_status=0;retry_at=0;seq=0;last_trigger=-999;pending=[];count=0
    probe="su -mm -c 'echo BOOT=$(cat /proc/sys/kernel/random/boot_id); cat /proc/uptime; cat /sys/module/nt36xxx/parameters/r94_wake_state; grep NVT-ts /proc/interrupts; echo SYSUI=$(pidof com.android.systemui)'"
    def start_reader():
        nonlocal proc,generation,remote_pid
        generation+=1;gen=generation;remote_pid=None
        proc=subprocess.Popen(adb+['shell','echo PC_24H_PID=$$; exec logcat -v threadtime -b main -b system -b events -b crash -T 1'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        local=proc
        def reader():
            try:
                for line in iter(local.stdout.readline,b''):events.put((gen,line))
            finally:events.put((gen,None))
        threading.Thread(target=reader,daemon=True).start()
    def close_reader():
        nonlocal proc,remote_pid
        if remote_pid and proc is not None and proc.poll() is None:
            # Verified, single PID belonging to this recorder, not Android services.
            command=cleanup_command(remote_pid)
            try:subprocess.run(adb+['shell',command],capture_output=True,timeout=4)
            except subprocess.TimeoutExpired:pass
        if proc is not None:
            try:proc.wait(timeout=2)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=2)
        proc=None;remote_pid=None
    def capture(reasons):
        nonlocal count,last_trigger
        if time.monotonic()-last_trigger<60 and 'user_report' not in reasons:
            event('trigger_during_cooldown',reasons=reasons);return
        if count>=16 and 'user_report' not in reasons:event('incident_limit_reached',reasons=reasons);return
        count+=1;last_trigger=time.monotonic();folder=incidents/('incident-%02d'%count);folder.mkdir()
        event('incident',number=count,reasons=reasons);save(state='capturing',incidents=count)
        ring.freeze(folder/'before-logs')
        before=folder/'before-snapshots';before.mkdir()
        for f in sorted(snapshots.glob('snapshot-*.json'))[-12:]:shutil.copyfile(f,before/f.name)
        metadata(folder/'trigger.json',{'host':now(),'reasons':reasons,'health':last_health})
        metadata(folder/'immediate.json',snapshot(True));pending.append((time.monotonic()+30,folder));save(state='recording',incidents=count)
    save(state='waiting_connection');event('started',planned_end=status['planned_end'])
    try:
        while time.monotonic()<deadline and not (root/'stop').exists():
            tick=time.monotonic();reasons=[]
            if proc is None and tick>=retry_at:
                try:q=subprocess.run(adb+['get-state'],capture_output=True,timeout=5)
                except subprocess.TimeoutExpired:q=None
                if q is not None and q.returncode==0 and q.stdout.strip()==b'device':
                    start_reader();event('connected');save(state='recording',connected=True);next_probe=0;next_snapshot=0
                else:retry_at=tick+3;save(state='waiting_connection',connected=False)
            try:gen,line=events.get(timeout=0.15)
            except queue.Empty:gen,line=generation,b''
            if gen!=generation:continue
            if line is None:
                close_reader();event('connection_lost');capture(['adb_connection_lost']);save(state='waiting_connection',connected=False);retry_at=tick+3;continue
            if line:
                m=re.search(rb'PC_24H_PID=(\d+)',line)
                if m:remote_pid=m[1].decode('ascii')
                ring.write(line);reasons+=reasons_for(line,None,None)
            if proc is not None and tick>=next_probe:
                result=read(probe,7);text=result.get('stdout','')
                with (root/'health.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
                if result.get('rc')==0:
                    reasons+=reasons_for(None,text,last_health);last_health=text
                next_probe=time.monotonic()+5
            marker=root/'capture-now'
            if marker.exists():
                kind='collector_self_check' if marker.read_text(encoding='utf-8').strip()=='self-check' else 'user_report'
                marker.rename(root/('marker-consumed-%d'%time.time_ns()));reasons.append(kind)
            if reasons:capture(reasons)
            if proc is not None and tick>=next_snapshot:
                seq+=1;metadata(snapshots/('snapshot-%08d.json'%seq),snapshot())
                old=sorted(snapshots.glob('snapshot-*.json'))
                for f in old[:-60]:f.unlink() # Only files created inside this session, no recursive deletion.
                next_snapshot=time.monotonic()+(30 if last_health and 'awake=0' in last_health else 10)
            for due,folder in pending[:]:
                if time.monotonic()>=due:ring.freeze(folder/'after-logs');metadata(folder/'after-state.json',snapshot(True));pending.remove((due,folder))
            if time.monotonic()>=next_status:
                save(remote_reader_pid=remote_pid,latest_health=last_health);next_status=time.monotonic()+5
    finally:
        for due,folder in pending:
            if not (folder/'after-logs').exists():ring.freeze(folder/'after-logs')
        close_reader();ring.close();event('stopped');save(state='stopped',finished=now())
        if awake:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
if __name__=='__main__':main()
