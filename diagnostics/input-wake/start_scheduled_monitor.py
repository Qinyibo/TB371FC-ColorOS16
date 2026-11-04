"""Windows Task Scheduler entry: each launch preserves prior runs and the original deadline."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0

def main():
    p=argparse.ArgumentParser();p.add_argument('--adb',required=True);p.add_argument('--serial',required=True);p.add_argument('--workspace',required=True);p.add_argument('--until',required=True);a=p.parse_args()
    if datetime.datetime.now()>=datetime.datetime.fromisoformat(a.until):return
    workspace=Path(a.workspace).resolve();root=workspace/'outputs'/('monitor24h-task-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    (workspace/'outputs/latest-monitor24h.txt').write_text(str(root),encoding='utf-8')
    log=workspace/'outputs/monitor24h-task-launches.jsonl'
    with log.open('a',encoding='utf-8') as f:f.write(json.dumps({'time':datetime.datetime.now().isoformat(),'root':str(root),'until':a.until})+'\n')
    result=subprocess.run([sys.executable,str(Path(__file__).with_name('supervise_24h.py')),'--adb',a.adb,'--serial',a.serial,'--out',str(root),'--until',a.until],creationflags=NO_WINDOW)
    raise SystemExit(result.returncode)
if __name__=='__main__':main()
