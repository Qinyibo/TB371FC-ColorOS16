"""Bounded PC-only log ring. No wake/input injection/property writes/restarts."""
from pathlib import Path
import argparse,concurrent.futures,datetime,json,queue,re,subprocess,threading,time

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--adb',required=True);ap.add_argument('--serial',required=True)
    ap.add_argument('--out',required=True);ap.add_argument('--minutes',type=int,default=120)
    args=ap.parse_args();root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=False)
    adb=[args.adb,'-s',args.serial];started=time.monotonic();end=started+min(max(args.minutes,1),480)*60
    status={'state':'starting','read_only':True,'wake_input_reboot':False,'started':datetime.datetime.now().isoformat()}
    def save(**kwargs):
        status.update(kwargs);status['updated']=datetime.datetime.now().isoformat()
        target=root/'status.json';tmp=root/'status.tmp';tmp.write_text(json.dumps(status,indent=2),encoding='utf-8');tmp.replace(target)
    cmds={'input':'dumpsys input','window':'dumpsys window','power-display':'dumpsys power; dumpsys display',
          'kernel':"su -mm -c 'dmesg'",'touch-state':"su -mm -c 'cat /proc/uptime; cat /sys/module/nt36xxx/parameters/r94_wake_state; cat /proc/interrupts'",
          'systemui-exit':'dumpsys activity exit-info com.android.systemui'}
    def snapshot(item):
        name,cmd=item
        try:
            q=subprocess.run(adb+['shell',cmd],capture_output=True,timeout=25)
            (root/(name+'.txt')).write_bytes(q.stdout);(root/(name+'-stderr.txt')).write_bytes(q.stderr)
            return {'name':name,'rc':q.returncode,'time':datetime.datetime.now().isoformat()}
        except Exception as exc:return {'name':name,'error':str(exc)}
    events=queue.Queue(maxsize=10000)
    def reader(proc):
        try:
            for line in iter(proc.stdout.readline,b''):events.put(line)
        finally:events.put(None)
    proc=None;remote_pid=None;ring=None;total=0;slot=0;size=0;triggered=False;trigger_end=None
    save(state='waiting_connection')
    try:
        while time.monotonic()<end and not (root/'stop').exists():
            if proc is None:
                q=subprocess.run(adb+['get-state'],capture_output=True,timeout=5)
                if q.returncode or q.stdout.strip()!=b'device':time.sleep(2);continue
                proc=subprocess.Popen(adb+['shell','echo PC_RING_READER_PID=$$; exec logcat -v threadtime -b main -b system -b events -b crash -T 1'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
                remote_pid=None;threading.Thread(target=reader,args=(proc,),daemon=True).start()
                save(state='recording',connected=True)
            try:line=events.get(timeout=0.25)
            except queue.Empty:line=b''
            if line is None:
                proc.wait(timeout=3);proc=None;remote_pid=None;save(state='waiting_connection',connected=False);continue
            if line:
                m=re.search(rb'PC_RING_READER_PID=(\d+)',line)
                if m:remote_pid=m[1].decode('ascii')
                if ring is None or size+len(line)>4*1024*1024:
                    if ring:ring.close()
                    ring=(root/('ring-%02d.log'%slot)).open('wb');slot=(slot+1)%8;size=0
                ring.write(line);ring.flush();size+=len(line);total+=len(line)
            trigger=(root/'capture-now').exists() or bool(line and re.search(rb'Process com\.android\.systemui \(pid \d+\) has died',line))
            if trigger and not triggered:
                triggered=True;trigger_end=time.monotonic()+30
                # Freeze the pre-trigger ring before collecting; stream continues for 30s.
                before=root/'before-trigger';before.mkdir()
                for f in root.glob('ring-*.log'):(before/f.name).write_bytes(f.read_bytes())
                save(state='capturing_incident',reason='user_marker' if (root/'capture-now').exists() else 'systemui_process_died',bytes=total)
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(snapshot,cmds.items()))
                (root/'snapshot-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
            if triggered and time.monotonic()>=trigger_end:break
            if int(time.monotonic()-started)%5==0:save(bytes=total,remote_reader_pid=remote_pid)
    except Exception as exc:save(error=str(exc))
    finally:
        if ring:ring.close()
        if remote_pid:
            # Kill only this tool's verified logcat reader, never Android services or adb server.
            command="p="+remote_pid+"; c=$(tr '\\000' ' ' </proc/$p/cmdline 2>/dev/null); case \"$c\" in *logcat*) kill -TERM $p;; esac"
            try:subprocess.run(adb+['shell',command],capture_output=True,timeout=5)
            except Exception:pass
        if proc is not None:
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=3)
        save(state='stopped',bytes=total,incident_captured=triggered,finished=datetime.datetime.now().isoformat())
if __name__=='__main__':main()
