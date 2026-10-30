"""A same-signed system preload base. The exact validated camera is its update."""
from pathlib import Path
import subprocess,os,hashlib,json,zipfile
O=Path(__file__).resolve().parent;D=O/'system-camera-seed';D.mkdir(exist_ok=True)
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk/build-tools/36.0.0')
env=dict(os.environ);env['R94_CAMERA_OWN_KEY_PASS']='android'
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,env=env,timeout=60)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p.stdout.decode('utf-8','replace')
(D/'PendingActivity.java').write_text('''package com.zui.camera;
public class PendingActivity extends android.app.Activity {
 public void onCreate(android.os.Bundle b){super.onCreate(b);android.widget.TextView t=new android.widget.TextView(this);t.setText("相机正在完成首次安装，请稍后再打开。");t.setTextSize(20);t.setPadding(40,80,40,40);setContentView(t);setResult(RESULT_CANCELED);}
}''',encoding='utf-8')
(D/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.zui.camera" android:versionCode="160069998" android:versionName="preload-base">
<uses-sdk android:minSdkVersion="26" android:targetSdkVersion="33"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<application android:label="相机" android:hasCode="true" android:theme="@android:style/Theme.Material.Light.NoActionBar">
<activity android:name=".PendingActivity" android:exported="true">
<intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter>
<intent-filter><action android:name="android.media.action.IMAGE_CAPTURE"/><category android:name="android.intent.category.DEFAULT"/></intent-filter>
<intent-filter><action android:name="android.media.action.VIDEO_CAPTURE"/><category android:name="android.intent.category.DEFAULT"/></intent-filter>
<intent-filter><action android:name="android.media.action.IMAGE_CAPTURE_SECURE"/><category android:name="android.intent.category.DEFAULT"/></intent-filter>
</activity></application></manifest>''',encoding='utf-8')
for n in ['classes','dex']:(D/n).mkdir(exist_ok=True)
run([J/'javac.exe','-encoding','UTF-8','-source','8','-target','8','-cp','C:/android-sdk/platforms/android-36/android.jar','-d',D/'classes',D/'PendingActivity.java'])
run([S/'d8.bat','--lib','C:/android-sdk/platforms/android-36/android.jar','--min-api','26','--output',D/'dex',*list((D/'classes').rglob('*.class'))])
run([S/'aapt2.exe','link','-o',D/'unsigned.apk','--manifest',D/'AndroidManifest.xml','-I','C:/android-sdk/platforms/android-36/android.jar'])
with zipfile.ZipFile(D/'unsigned.apk','a') as z:z.write(D/'dex/classes.dex','classes.dex')
run([S/'zipalign.exe','-f','4',D/'unsigned.apk',D/'aligned.apk'])
apk=D/'ZuiCameraSeed.apk';key=O.parent/'black-camera-20261020/official-camera-inputs/zui-candidate/camera-test.keystore'
run([S/'apksigner.bat','sign','--ks',key,'--ks-pass','env:R94_CAMERA_OWN_KEY_PASS','--out',apk,D/'aligned.apk'])
cert=run([S/'apksigner.bat','verify','--print-certs',apk]);expected='bfb0b7acb8ed0e8209ce1b875f56af8474f115c7a779055d5885a63836d84efc';assert expected in cert
full=Path('D:/TB371FC-release/R94T-v22a-NATIVE-PEN-COMM-PRIVATE_TEST/assets/camera/ZuiCamera-TB371FC-C16-candidate.apk')
assert expected in run([S/'apksigner.bat','verify','--print-certs',full])
with full.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()=='beaa56d744387613661f198849679fd9963a66fc8efddeb38e5b76671db220bc'
r={'state':'SAME_SIGNER_LOWER_VERSION_SYSTEM_CAMERA_PRELOAD_BASE_BUILT','package':'com.zui.camera','base_version_code':160069998,'full_version_code':160069999,'base_sha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'full_camera_apk_byte_unchanged':True,'signer_sha256':expected,'runtime_system_identity_tested':False}
(D/'result.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
