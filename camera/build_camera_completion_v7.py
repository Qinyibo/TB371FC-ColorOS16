"""Correct standard completion-status handling. No forced encoding success."""
from pathlib import Path
import subprocess,hashlib,zipfile,shutil,os,struct,json,re
B=Path(__file__).resolve().parent;O=B/'completion-fix-v7';O.mkdir(exist_ok=True)
original=B/'video-intent-fix/original-smali';modified=O/'smali'
if not modified.exists():shutil.copytree(original,modified)
target=Path('com/zui/camera/video/recorder/MediaRecorderWrapper.smali')
text=(original/target).read_text();a=text.index('.method public onInfo(');b=text.index('.end method',a)+len('.end method');old=text[a:b]
anchor='''    iget-boolean v1, p0, Lcom/zui/camera/video/recorder/MediaRecorderWrapper;->mStopping:Z

    if-nez v1, :cond_5a'''
assert old.count(anchor)==1
new=old.replace(anchor,'''    # AOSP completion info permits OK and normal end-of-stream. A track may
    # complete before the application's stop handler on a duration limit.
    if-eqz p3, :cond_5a

    const/16 v1, -0x3f3

    if-eq p3, v1, :cond_5a''')
(modified/target).write_text(text[:a]+new+text[b:],encoding='utf-8',newline='\n')
changed=[p.relative_to(original).as_posix() for p in original.rglob('*.smali') if p.read_bytes()!=(modified/p.relative_to(original)).read_bytes()]
assert changed==[target.as_posix()]
(O/'original-onInfo.smali').write_text(old,encoding='utf-8');(O/'candidate-onInfo.smali').write_text(new,encoding='utf-8')
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk/build-tools/36.0.0');env=dict(os.environ);env['R94_CAMERA_OWN_KEY_PASS']='android'
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,env=env,timeout=180)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace')[-2000:])
 return p.stdout.decode('utf-8','replace')
run([J/'java.exe','-Xmx2g','-cp','C:/Users/Administrator/Documents/Codex/2026-07-30/x/work/*','org.jf.smali.Main','assemble','--api','33','--output',O/'classes2.dex',modified])
source=Path('D:/TB371FC-release/R94T-v22a-NATIVE-PEN-COMM-PRIVATE_TEST/assets/camera/ZuiCamera-TB371FC-C16-candidate.apk')
preserved=[]
with zipfile.ZipFile(source) as z,zipfile.ZipFile(O/'unsigned.apk','w') as out:
 for i in z.infolist():
  if re.fullmatch(r'META-INF/(?:MANIFEST\.MF|[^/]+\.(?:SF|RSA|DSA|EC))',i.filename,re.I):continue
  data=z.read(i.filename)
  if i.filename=='classes2.dex':data=(O/'classes2.dex').read_bytes()
  elif i.filename=='AndroidManifest.xml':
   v=struct.pack('<I',160069999);assert data.count(v)==1;data=data.replace(v,struct.pack('<I',160070001))
  else:preserved.append({'name':i.filename,'sha256':hashlib.sha256(data).hexdigest()})
  out.writestr(i,data)
run([S/'zipalign.exe','-f','-p','4',O/'unsigned.apk',O/'aligned.apk'])
apk=O/'ZuiCamera-TB371FC-C16-system-v7.apk';key=B.parent/'black-camera-20261020/official-camera-inputs/zui-candidate/camera-test.keystore'
run([S/'apksigner.bat','sign','--ks',key,'--ks-pass','env:R94_CAMERA_OWN_KEY_PASS','--out',apk,O/'aligned.apk'])
assert 'bfb0b7acb8ed0e8209ce1b875f56af8474f115c7a779055d5885a63836d84efc' in run([S/'apksigner.bat','verify','--print-certs',apk])
run([S/'zipalign.exe','-c','-p','4',apk])
with zipfile.ZipFile(apk) as z:
 assert not 'classes4.dex' in z.namelist()
 for r in preserved:assert hashlib.sha256(z.read(r['name'])).hexdigest()==r['sha256']
with apk.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
r={'state':'MINIMAL_COMPLETION_STATUS_V7_BUILT_NOT_TESTED','sha256':h,'bytes':apk.stat().st_size,'version_code':160070001,'changed_original_class':target.as_posix(),'changed_original_method':'onInfo(MediaRecorder,int,int)','preserved_payload_members':len(preserved),'new_helper_or_forced_success':False,'onError_and_isEncodeSuccess_unchanged':True,'normal_completion_status':[0,-1011],'unexpected_nonzero_status_preserves_error':True,'v6_hypothesis_withdrawn':'actual map was present; one successful early completion was incorrectly marked error because mStopping was false'}
(O/'build-result.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
