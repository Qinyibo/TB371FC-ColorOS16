"""Run isolated real-ART cleanup checks, without changing input/UI or restarting Android."""
from pathlib import Path
import json
import shlex
import subprocess
import sys
import zipfile

SOURCE=Path(__file__).resolve().parent
BUILD=Path(sys.argv[1]).resolve()
SERIAL=sys.argv[2]
JAVA=Path('C:/Program Files/Java/jdk-21/bin')
ADB='C:/android-sdk/platform-tools/adb.exe'
ART=BUILD/'art-test'
assert not ART.exists(),'Inspect prior ART test evidence before repeating'
ART.mkdir()
vendor=ART/'vendor.jar'
with zipfile.ZipFile(vendor,'w') as z:
    classes=BUILD/'host-test/classes'
    for path in classes.rglob('*.class'):
        name=path.relative_to(classes).as_posix()
        if name.startswith(('com/','androidx/','kotlin/')):z.write(path,name)
classes=ART/'classes';classes.mkdir()
android=Path('C:/android-sdk/platforms/android-36/android.jar')
assert android.exists()
subprocess.run([str(JAVA/'javac.exe'),'-cp',str(android)+';'+str(vendor),'-d',str(classes),
    str(SOURCE/'test-src/LifecycleArtProbe.java')],check=True)
jar=ART/'probe-source.jar'
with zipfile.ZipFile(jar,'w') as z:
    for path in classes.rglob('*.class'):z.write(path,path.relative_to(classes).as_posix())
subprocess.run(['C:/android-sdk/build-tools/36.0.0/d8.bat','--min-api','35','--lib',str(android),
    '--output',str(ART/'probe.jar'),str(jar),str(vendor)],check=True)
for kind in ['before','candidate']:
    with zipfile.ZipFile(ART/(kind+'.jar'),'w') as z:z.write(BUILD/(kind+'-focused.dex'),'classes.dex')
stage='/data/local/tmp/tb371fc-input-cleanup-art-r1'
def shell(command,timeout=20):
    return subprocess.run([ADB,'-s',SERIAL,'shell','su -c '+shlex.quote(command)],capture_output=True,timeout=timeout)
p=shell('getprop ro.serialno; cat /proc/sys/kernel/random/boot_id; pidof system_server com.android.systemui com.android.launcher')
assert p.returncode==0
before=p.stdout.decode().replace('\r','').strip()
assert before.splitlines()[0]==SERIAL
assert shell('mkdir -p '+stage+'; chown 2000:2000 '+stage+'; chmod 755 '+stage).returncode==0
for name in ['probe.jar','before.jar','candidate.jar']:
    subprocess.run([ADB,'-s',SERIAL,'push',str(ART/name),stage+'/'+name],check=True,capture_output=True,timeout=30)
rows={}
for kind in ['before','candidate']:
    p=shell('chmod 444 '+stage+'/*.jar; CLASSPATH='+stage+'/'+kind+'.jar:'+stage+'/probe.jar app_process -Xverify:all /system/bin LifecycleArtProbe',35)
    (ART/(kind+'.txt')).write_bytes(p.stdout+p.stderr)
    rows[kind]=dict(returncode=p.returncode,output=(p.stdout+p.stderr).decode(errors='replace'))
    print(kind,rows[kind]['output'],flush=True)
p=shell('getprop ro.serialno; cat /proc/sys/kernel/random/boot_id; pidof system_server com.android.systemui com.android.launcher')
after=p.stdout.decode().replace('\r','').strip();assert p.returncode==0 and after==before
assert rows['before']['returncode']==1 and 'ART_CHECKS=80 FAILURES=20' in rows['before']['output']
assert rows['candidate']['returncode']==0 and 'ART_CHECKS=80 FAILURES=0' in rows['candidate']['output']
record=dict(state='ISOLATED_REAL_ART_HANDLER_CONTRACT_PASS',results=rows,
    system_processes_and_boot_unchanged=True,no_ui_or_input_injection=True,
    launcher_candidate_installed=False,interaction_incident_root_cause_proven=False)
(BUILD/'art-result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('REAL_ART_CONTRACT_PASS',flush=True)
