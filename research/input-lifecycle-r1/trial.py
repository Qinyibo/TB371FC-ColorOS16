"""Reversible Launcher trial after explicit idle-device authorization; no reboot."""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import subprocess
import time

parser=argparse.ArgumentParser()
parser.add_argument('build');parser.add_argument('output');parser.add_argument('serial')
parser.add_argument('--art-result',default='art-result.json')
args=parser.parse_args()
BUILD=Path(args.build).resolve();OUT=Path(args.output).resolve();SERIAL=args.serial
ADB='C:/android-sdk/platform-tools/adb.exe'
TARGET='/system_ext/priv-app/OplusLauncher/OplusLauncher.apk'
CACHE='/data/local/r94-animation-v1/launcher/OplusLauncher.apk'
BACKUP=CACHE+'.input-r1-before'
NEXT=CACHE+'.input-r1-next'
STAGE='/data/local/tmp/tb371fc-input-lifecycle-r1'
OLD='bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d'
record=json.loads((BUILD/'build-result.json').read_text(encoding='utf-8'))
NEW=record['candidate_sha256'];candidate=BUILD/'OplusLauncher-input-lifecycle-r1.apk'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==NEW
assert json.loads((BUILD/args.art_result).read_text(encoding='utf-8'))['state']=='ISOLATED_REAL_ART_HANDLER_CONTRACT_PASS'
assert not OUT.exists(),'Inspect any existing deployment before retrying'
OUT.mkdir(parents=True)
receipt=dict(state='PREPARING',old_sha256=OLD,candidate_sha256=NEW,reboot_requested=False,
    partition_written=False,persistent_installation=False,root_cause_fixed_claimed=False)

def save():
    (OUT/'deployment.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')

def shell(command,timeout=25,check=True):
    p=subprocess.run([ADB,'-s',SERIAL,'shell','su -mm -c '+shlex.quote(command)],capture_output=True,timeout=timeout)
    value=(p.stdout+p.stderr).decode(errors='replace').replace('\r','').strip()
    if check:assert p.returncode==0,value
    return value

published=False
save()
try:
    assert shell('getprop ro.serialno')==SERIAL
    assert shell('sha256sum '+TARGET).split()[0]==OLD
    assert shell('sha256sum '+CACHE).split()[0]==OLD
    assert shell('getenforce')=='Enforcing'
    assert 'failed=0' in shell('cat /sys/module/nt36xxx/parameters/r94_wake_state')
    receipt['boot']=shell('cat /proc/sys/kernel/random/boot_id')
    receipt['system_server']=shell('pidof system_server')
    receipt['systemui']=shell('pidof com.android.systemui')
    receipt['launcher_before']=shell('pidof com.android.launcher')
    shell('mkdir -p '+STAGE+'; chown 2000:2000 '+STAGE+'; chmod 755 '+STAGE)
    staged=shell('if test -f '+STAGE+'/Launcher.apk; then sha256sum '+STAGE+'/Launcher.apk; else echo absent; fi')
    if staged=='absent':
        p=subprocess.run([ADB,'-s',SERIAL,'push','-Z',str(candidate),STAGE+'/Launcher.apk'],capture_output=True,timeout=90)
        assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')
    else:assert staged.split()[0]==NEW,'Staging contains another candidate; inspect it'
    assert shell('sha256sum '+STAGE+'/Launcher.apk').split()[0]==NEW
    shell('chmod 444 '+STAGE+'/Launcher.apk; chcon u:object_r:system_file:s0 '+STAGE+'/Launcher.apk')
    assert shell('sha256sum '+TARGET).split()[0]==OLD
    backup_state=shell('if test -e '+BACKUP+'; then sha256sum '+BACKUP+'; else echo absent; fi')
    if backup_state=='absent':shell('ln '+CACHE+' '+BACKUP)
    else:assert backup_state.split()[0]==OLD
    shell('cp '+STAGE+'/Launcher.apk '+NEXT+'; chmod 644 '+NEXT+'; chcon u:object_r:system_file:s0 '+NEXT)
    assert shell('sha256sum '+NEXT).split()[0]==NEW
    shell('am force-stop com.android.launcher')
    # Existing app namespaces already share this native cache directory. An
    # atomic rename changes its file for all of them without a new mount layer.
    shell('mv -f '+NEXT+' '+CACHE)
    published=True
    assert shell('sha256sum '+TARGET).split()[0]==NEW
    receipt.update(state='CANDIDATE_NATIVE_CACHE_PUBLISHED',backup=BACKUP);save()
    print('COMPILING_LAUNCHER_ONLY_NO_REBOOT',flush=True)
    compilation=shell('cmd package compile --primary-dex -m speed -f com.android.launcher',180)
    (OUT/'compile.txt').write_text(compilation,encoding='utf-8')
    assert 'Success' in compilation,compilation
    # The bootstrap uses the same final stop: no process spawned during asset
    # publication/compilation may retain the old classes.
    shell('am force-stop com.android.launcher')
    shell('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    (OUT/'home-start.txt').write_text(shell('am start -W -a android.intent.action.MAIN -c android.intent.category.HOME',45),encoding='utf-8')
    deadline=time.monotonic()+45
    while time.monotonic()<deadline:
        pid=shell('pidof com.android.launcher',check=False)
        if pid.isdigit() and pid!=receipt['launcher_before']:
            break
        time.sleep(1)
    else:raise RuntimeError('New Launcher process not observed')
    time.sleep(2)
    assert shell('pidof com.android.launcher')==pid
    inode=shell('stat -c %i '+CACHE)
    maps=shell('grep -F OplusLauncher /proc/'+pid+'/maps')
    (OUT/'launcher-maps.txt').write_text(maps,encoding='utf-8')
    assert any(line.split()[4]==inode for line in maps.splitlines()),'Candidate APK mapping not observed'
    assert shell('cat /proc/sys/kernel/random/boot_id')==receipt['boot']
    assert shell('pidof system_server')==receipt['system_server']
    assert shell('pidof com.android.systemui')==receipt['systemui']
    health=shell('cat /sys/module/nt36xxx/parameters/r94_wake_state; dumpsys power | grep mWakefulness=')
    (OUT/'health.txt').write_text(health,encoding='utf-8')
    assert 'failed=0' in health and 'mWakefulness=Awake' in health
    receipt.update(state='CANDIDATE_ACTIVE_NATIVE_CACHE_TRIAL',launcher=pid,mapped_inode=inode,
                   ui_behavior_verified=False,boot_and_core_system_processes_unchanged=True)
except Exception as error:
    receipt['error']=repr(error);receipt['failed_at']=receipt['state']
    if published:
        assert shell('sha256sum '+TARGET).split()[0]==NEW,'Target changed externally; inspect before rollback'
        assert shell('sha256sum '+BACKUP).split()[0]==OLD
        rollback=CACHE+'.input-r1-rollback'
        shell('ln '+BACKUP+' '+rollback+'; mv -f '+rollback+' '+CACHE)
        assert shell('sha256sum '+TARGET).split()[0]==OLD
        shell('am force-stop com.android.launcher; am start -a android.intent.action.MAIN -c android.intent.category.HOME',45)
        receipt['state']='TRIAL_FAILED_PREVIOUS_LAUNCHER_RESTORED'
    else:receipt['state']='PREFLIGHT_FAILED_NO_LAUNCHER_CHANGE'
    raise
finally:
    save();print(json.dumps(receipt),flush=True)
