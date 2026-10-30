from pathlib import Path
import sys,subprocess,runpy,zipfile,json,hashlib
sys.stdout.reconfigure(encoding='utf-8')
p=Path('work/systemui-caption-settle');p.mkdir(exist_ok=True)
accepted=Path('work/systemui-caption-focus/SystemUI-caption-defer-candidate.apk')
good='56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928'
assert hashlib.sha256(accepted.read_bytes()).hexdigest()==good
holder=Path('work/systemui-caption-defer/smali/com/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder.smali')
source=Path('work/systemui-caption-focus/patched-holder.smali').read_text(encoding='utf-8')
assert source.count('const-wide/16 v1, 0x190')==1
patched=source.replace('const-wide/16 v1, 0x190','const-wide/16 v1, 0x320')
(p/'holder-patched.smali').write_text(patched,encoding='utf-8')
with zipfile.ZipFile(accepted) as z:(p/'classes2-original.dex').write_bytes(z.read('classes2.dex'))
try:
 holder.write_text(patched,encoding='utf-8')
 subprocess.run(['java','-cp',r'D:\TB371FC-work\tools\apktool.jar','work/DexTool.java','asm','work/systemui-caption-defer/smali',str(p/'classes2-candidate.dex')],check=True)
finally:holder.write_text(source,encoding='utf-8')
# Compare against the accepted DEX; only the delay instruction may change.
verify=Path('work/verify_package_caption_focus.py').read_text().replace("Path('work/systemui-caption-focus')","Path('work/systemui-caption-settle')").replace("'delay_ms':400","'delay_ms':800")
verify=verify.replace("base_apk_sha256':hashlib.sha256(raw).hexdigest()","base_apk_sha256':hashlib.sha256(raw).hexdigest()")
script=p/'verify_package.py';script.write_text(verify,encoding='utf-8')
scope=runpy.run_path(str(script))
assert scope['changed']==['Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;->createStatusBarInputLayer(Landroid/graphics/Point; I I)V'],scope['changed']
key=scope['changed'][0];old=scope['x'][key];new=scope['y'][key]
diff=[(a,b) for a,b in zip(old,new) if a!=b];assert len(old)==len(new) and len(diff)==1,diff
assert '400' in str(diff[0][0]) and '800' in str(diff[0][1]),diff
v=json.loads((p/'validation.json').read_text());v.update(accepted_fallback_sha256=good,status='OFFLINE_SINGLE_DELAY_CHANGE_VERIFIED',changed_from_accepted_focus=scope['changed'],currently_active=False)
(p/'validation.json').write_text(json.dumps(v,indent=2));print('SETTLE800_READY',v['candidate_apk_sha256'],flush=True)
