"""Own-process supervisor, bounded to24h; tablet state is never changed."""
from pathlib import Path
import argparse,ctypes,datetime,json,os,subprocess,sys,time
from monitor_24h import metadata

def main():
    p=argparse.ArgumentParser();p.add_argument('--adb',required=True);p.add_argument('--serial',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    root=Path(args.out).resolve();root.mkdir(parents=True,exist_ok=False);(root/'runs').mkdir()
    (root/'capture-now.cmd').write_text('@echo off\n> "%~dp0capture-now" echo user-report\n',encoding='ascii')
    (root/'stop.cmd').write_text('@echo off\n> "%~dp0stop" echo user-stop\n',encoding='ascii')
    deadline=time.monotonic()+24*3600;end=datetime.datetime.now()+datetime.timedelta(hours=24)
    awake=bool(ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)) if os.name=='nt' else False
    status={'planned_end':end.isoformat(),'started':datetime.datetime.now().isoformat(),'state':'starting','pc_sleep_inhibited':awake,'read_only':True,'tablet_input_wake_reboot':False}
    def save(**values):status.update(values);status['updated']=datetime.datetime.now().isoformat();metadata(root/'status.json',status)
    n=0;proc=None;next_status=0
    try:
        while time.monotonic()<deadline and not (root/'stop').exists():
            n+=1;run=root/'runs'/('run-%04d'%n);remaining=max((deadline-time.monotonic())/3600,0.001)
            proc=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('monitor_24h.py')),'--adb',args.adb,'--serial',args.serial,'--out',str(run),'--hours',str(remaining)],stdout=subprocess.DEVNULL,stderr=(root/('run-%04d.stderr'%n)).open('wb'))
            (root/'latest-run.txt').write_text(str(run),encoding='utf-8');save(state='running',active_run=str(run),child_pid=proc.pid,run_number=n)
            while proc.poll() is None and time.monotonic()<deadline and not (root/'stop').exists():
                marker=root/'capture-now'
                if marker.exists() and run.exists():
                    text=marker.read_text(encoding='utf-8');(run/'capture-now').write_text(text,encoding='utf-8');marker.rename(root/('forwarded-marker-%d'%time.time_ns()))
                if time.monotonic()>=next_status:
                    child=None
                    try:child=json.loads((run/'status.json').read_text(encoding='utf-8'))
                    except (FileNotFoundError,json.JSONDecodeError):pass
                    save(child=child);next_status=time.monotonic()+5
                time.sleep(0.5)
            if proc.poll() is None:
                (run/'stop').write_text('supervisor deadline or user stop',encoding='utf-8');proc.wait(timeout=90)
            save(last_child_exit=proc.returncode)
            if time.monotonic()<deadline and not (root/'stop').exists():time.sleep(3)
    finally:
        if proc is not None and proc.poll() is None:
            active=Path(status['active_run']);active.mkdir(parents=True,exist_ok=True);(active/'stop').write_text('supervisor closing',encoding='utf-8');proc.wait(timeout=90)
        save(state='stopped',finished=datetime.datetime.now().isoformat())
        if awake:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
if __name__=='__main__':main()
