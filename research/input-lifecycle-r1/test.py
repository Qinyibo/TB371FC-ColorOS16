"""Run extracted DEX cleanup methods on an isolated host JVM; never use ADB."""
from pathlib import Path
import json
import subprocess
import sys

SOURCE = Path(__file__).resolve().parent
BUILD = Path(sys.argv[1]).resolve()
TRANSLATOR = Path(sys.argv[2]).resolve()
JAVA = Path('C:/Program Files/Java/jdk-21/bin')
TEST = BUILD/'host-test'
assert not TEST.exists(), 'Inspect prior test evidence before repeating'
TEST.mkdir()
STUBS = {
    'android/os/Handler.java': '''package android.os;
public class Handler { public String state; public int removed;
 public Handler(String s){state=s;} public boolean hasCallbacks(Runnable r){return state.equals("queued");}
 public void removeCallbacks(Runnable r){removed++;state="cancelled";} }
''',
    'android/view/MotionEvent.java': '''package android.view;
public class MotionEvent { public int recycles;
 public void recycle(){if(++recycles>1)throw new AssertionError("double recycle");} }
''',
    'android/view/VelocityTracker.java': '''package android.view;
public class VelocityTracker { public boolean recycled; public void recycle(){recycled=true;} }
''',
    'kotlin/jvm/internal/DefaultConstructorMarker.java': 'package kotlin.jvm.internal; public class DefaultConstructorMarker {}',
    'com/android/common/util/AppFeatureUtils.java': 'package com.android.common.util; public class AppFeatureUtils { public static boolean isTablet(){return true;} }',
    'com/android/common/util/ScreenUtils.java': 'package com.android.common.util; public class ScreenUtils { public static boolean isFoldScreenExpanded(){return false;} }',
    'com/android/common/util/LauncherAnimConfig.java': 'package com.android.common.util; public class LauncherAnimConfig { public static boolean isLevelBOrBPlus(){return false;} }',
    'com/oplus/basecommon/log/LogUtils.java': '''package com.oplus.basecommon.log;
public class LogUtils { public static boolean isLoggableInfo(){return false;} public static void i(String a,String b){} }
''',
    'androidx/compose/animation/k.java': '''package androidx.compose.animation;
public class k {public static StringBuilder b(String a,String b,long n){return new StringBuilder(a).append(n).append(b);} }
''',
    'com/oplus/quickstep/gesture/helper/OplusInputInterceptHelper$State.java': '''package com.oplus.quickstep.gesture.helper;
public enum OplusInputInterceptHelper$State {SWIPE_DETECTING,SWIPE_FAIL,SWIPE_SUCCESS,SWIPE_SUCCESS_BUT_NEED_INJECT}
''',
    'com/oplus/quickstep/gesture/helper/OplusInputInterceptHelper$IGestureStateChangeListener.java': '''package com.oplus.quickstep.gesture.helper;
public interface OplusInputInterceptHelper$IGestureStateChangeListener {}
''',
    'com/oplus/quickstep/gesture/helper/OplusInputInterceptHelper$INSTANCE.java': '''package com.oplus.quickstep.gesture.helper;
public class OplusInputInterceptHelper$INSTANCE { public OplusInputInterceptHelper$INSTANCE(kotlin.jvm.internal.DefaultConstructorMarker m){} }
''',
}
files=[]
for name, content in STUBS.items():
    path=TEST/'src'/name; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8',newline='\n'); files.append(str(path))
classes=TEST/'classes';classes.mkdir()
subprocess.run([str(JAVA/'javac.exe'),'-d',str(classes),*files,
                str(SOURCE/'test-src/LifecycleContractTest.java')],check=True)
rows={}
for kind in ['before','candidate']:
    jar=TEST/(kind+'.jar')
    p=subprocess.run([sys.executable,'-O','-m','enjarify.main',str(BUILD/(kind+'-focused.dex')),
                      '-o',str(jar)],cwd=TRANSLATOR,capture_output=True,timeout=60)
    (TEST/(kind+'-translation.txt')).write_bytes(p.stdout+p.stderr)
    assert p.returncode==0 and jar.exists(),(p.stdout+p.stderr).decode(errors='replace')
    p=subprocess.run([str(JAVA/'java.exe'),'-cp',str(classes)+';'+str(jar),
                      'LifecycleContractTest'],capture_output=True,timeout=30)
    (TEST/(kind+'.txt')).write_bytes(p.stdout+p.stderr)
    rows[kind]=dict(returncode=p.returncode,output=(p.stdout+p.stderr).decode(errors='replace'))
    print(kind,rows[kind]['output'],flush=True)
assert rows['before']['returncode']==1 and 'CHECKS=120 FAILURES=30' in rows['before']['output']
assert rows['candidate']['returncode']==0 and 'CHECKS=120 FAILURES=0' in rows['candidate']['output']
result=dict(state='HOST_EXTRACTED_DEX_CONTRACT_PASS',results=rows,
    production_methods_translated_not_hand_reimplemented=True,os_environment_stubbed=True,
    translator_commit=subprocess.check_output(['git','-C',str(TRANSLATOR),'rev-parse','HEAD']).decode().strip(),
    android_art_runtime_tested=False,device_tested=False,reported_incident_root_cause_proven=False)
(BUILD/'contract-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('HOST_CONTRACT_PASS',flush=True)
