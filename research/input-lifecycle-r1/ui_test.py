"""Finite real UI test; temporarily keep the USB-powered screen awake, then restore."""
from pathlib import Path
import json
import shlex
import subprocess
import sys
import time
import zipfile

SOURCE=Path(__file__).resolve().parent
BUILD=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();SERIAL=sys.argv[3]
assert not OUT.exists(),'Preserve existing UI evidence'
OUT.mkdir(parents=True)
JAVA=Path('C:/Program Files/Java/jdk-21/bin');SDK=Path('C:/android-sdk/platforms/android-36')
ADB='C:/android-sdk/platform-tools/adb.exe'
classes=OUT/'classes';classes.mkdir()
libs=[SDK/'android.jar',SDK/'uiautomator.jar',SDK/'optional/android.test.base.jar']
subprocess.run([str(JAVA/'javac.exe'),'-encoding','UTF-8','-cp',';'.join(map(str,libs)),
    '-d',str(classes),str(SOURCE/'test-src/InputUiTest.java')],check=True)
jar=OUT/'test-source.jar'
with zipfile.ZipFile(jar,'w') as z:
    for p in classes.rglob('*.class'):z.write(p,p.relative_to(classes).as_posix())
d8=['C:/android-sdk/build-tools/36.0.0/d8.bat','--min-api','35','--output',str(OUT/'ui-test.jar')]
for lib in libs:d8+=['--lib',str(lib)]
subprocess.run(d8+[str(jar)],check=True)
def shell(command,timeout=25):
    return subprocess.run([ADB,'-s',SERIAL,'shell','su -mm -c '+shlex.quote(command)],capture_output=True,timeout=timeout)
def sh(command,timeout=25):
    p=shell(command,timeout);assert p.returncode==0,(p.stdout+p.stderr).decode(errors='replace')
    return p.stdout.decode(errors='replace').replace('\r','').strip()
record=dict(state='PREPARING',no_reboot=True,partition_written=False,physical_touch_tested=False)
def save():(OUT/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
assert sh('sha256sum /system_ext/priv-app/OplusLauncher/OplusLauncher.apk').split()[0]==json.loads((BUILD/'build-result.json').read_text(encoding='utf-8'))['candidate_sha256']
identity='cat /proc/sys/kernel/random/boot_id; pidof system_server com.android.systemui com.android.launcher'
record['before_identity']=sh(identity)
original_stay=sh('settings get global stay_on_while_plugged_in')
record['original_stay_on_while_plugged_in']=original_stay;save()
stage='/data/local/tmp/tb371fc-input-ui-r1'
sh('mkdir -p '+stage+'; chown 2000:2000 '+stage+'; chmod 755 '+stage)
p=subprocess.run([ADB,'-s',SERIAL,'push',str(OUT/'ui-test.jar'),stage+'/ui-test.jar'],capture_output=True,timeout=25)
assert p.returncode==0,p.stderr
sh('chmod 444 '+stage+'/ui-test.jar')
log=(OUT/'gesture-log.txt').open('wb');logger=None
try:
    sh('svc power stayon usb; input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard')
    time.sleep(1)
    logger=subprocess.Popen([ADB,'-s',SERIAL,'logcat','-v','threadtime','-T','1','-s',
        'TouchInteractionService:V','OplusBaseTouchInteractionService:V','OplusInputInterceptHelper:V',
        'OtherActivityInputConsumer:V','OplusOtherActivityInputConsumer:V',
        'OplusGestureAnimationManagerPolicy:V','OplusGestureAnimationController:V',
        'FlexibleWindowManagerService:V','InputDispatcher:W','AndroidRuntime:E',
        'TB371FCInputContract:I','*:S'],stdout=log,stderr=subprocess.STDOUT)
    record['state']='FINITE_UI_SUITE_RUNNING';save();print('FINITE_UI_SUITE_RUNNING_NO_REBOOT',flush=True)
    p=shell('uiautomator runtest /system/framework/android.test.runner.jar '+stage+'/ui-test.jar -c org.tb371fc.inputcontract.InputUiTest',140)
    output=(p.stdout+p.stderr).decode(errors='replace').replace('\r','')
    (OUT/'suite.txt').write_text(output,encoding='utf-8');print(output,flush=True)
    expected_cases = (
        'ordinary_tap_delivered', 'normal_home_pass',
        'interrupted_gesture_then_home_pass', 'hold_to_overview_pass',
        'four_pointer_sequence_delivered', 'home_after_multi_pointer_pass',
        'final_ordinary_home_pass',
    )
    missing_cases = [case for case in expected_cases if 'CASE '+case not in output]
    runner_aborted = any(marker in output for marker in (
        'Test run aborted', 'INSTRUMENTATION_STATUS: shortMsg=',
        'FAILURES!!!', 'INSTRUMENTATION_FAILED',
    ))
    record.update(returncode=p.returncode, missing_cases=missing_cases,
        runner_aborted=runner_aborted,
        suite_pass=p.returncode==0 and 'OK (1 test)' in output
        and not missing_cases and not runner_aborted)
    for name,command in [('input','dumpsys input'),('window','dumpsys window'),
        ('touch-service','dumpsys activity service com.android.launcher/com.android.quickstep.TouchInteractionService'),
        ('health','cat /sys/module/nt36xxx/parameters/r94_wake_state; cat /sys/class/backlight/panel0-backlight/bl_power; dumpsys power | grep mWakefulness='),
        ('kernel','dmesg')]:
        (OUT/(name+'.txt')).write_text(sh(command,35),encoding='utf-8')
    record['after_identity']=sh(identity)
    record['boot_and_core_system_processes_unchanged']=record['after_identity']==record['before_identity']
    p=subprocess.run([ADB,'-s',SERIAL,'pull',stage,str(OUT/'screens')],capture_output=True,timeout=30)
    record['screens_pulled']=p.returncode==0
    record['state']='FINITE_UI_SUITE_PASS' if record['suite_pass'] and record['boot_and_core_system_processes_unchanged'] else 'FINITE_UI_SUITE_FAILED_REQUIRES_REVIEW'
except Exception as error:
    record.update(state='UI_TEST_ERROR',error=repr(error));raise
finally:
    if logger is not None:
        logger.terminate()
        try:logger.wait(timeout=5)
        except subprocess.TimeoutExpired:logger.kill();logger.wait()
    log.close()
    restore='settings delete global stay_on_while_plugged_in' if original_stay=='null' else 'settings put global stay_on_while_plugged_in '+shlex.quote(original_stay)
    sh(restore)
    record['screen_stay_setting_restored']=sh('settings get global stay_on_while_plugged_in')==original_stay
    save();print(json.dumps(record),flush=True)
