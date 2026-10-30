from pathlib import Path
import hashlib,shutil,runpy,re,json
base=Path('work/systemui-caption-defer');out=Path('work/systemui-caption-focus');out.mkdir(exist_ok=True)
good=base/'SystemUI-caption-defer-candidate.apk';backup=out/'accepted-daily-SystemUI.apk'
expected='32018d2d20d87e2532bef9d06c1360b44abbeba5e088da835cddc529784f65f0'
if not backup.exists():
 assert hashlib.sha256(good.read_bytes()).hexdigest()==expected
 shutil.copyfile(good,backup)
assert hashlib.sha256(backup.read_bytes()).hexdigest()==expected
if not (out/'classes2-original.dex').exists():shutil.copyfile(base/'classes2-original.dex',out/'classes2-original.dex')
runpy.run_path('work/patch_caption_defer.py')
p=base/'smali/com/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder.smali';s=p.read_text();C='Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;'
def edit(name,fn):
 global s
 pat=r'(?ms)^\.method [^\n]* '+re.escape(name)+r'[^\n]*\n.*?^\.end method'
 s,n=re.subn(pat,lambda m:fn(m.group(0)),s);assert n==1
focus='''    iget-object v0, p0, @C@->mTaskInfo:Landroid/app/ActivityManager$RunningTaskInfo;
    if-eqz v0, :done
    iget-boolean v0, v0, Landroid/app/ActivityManager$RunningTaskInfo;->isFocused:Z
    if-eqz v0, :done
'''.replace('@C@',C)
edit('createStatusBarInputLayer(Landroid/graphics/Point;II)V',lambda m:m.replace('    .locals 3\n','    .locals 3\n'+focus,1).replace('    return-void','    :done\n    return-void',1))
edit('run()V',lambda m:m.replace('    iget v2, p0,',focus+'    iget v2, p0,',1))
# Pending creation is cancelled when task focus moves away. Existing input windows keep original lifetime for dragging.
def update(m):
 m=m.replace('    iget-object v0, p0, @C@->mDeferredInputLayerPoint'.replace('@C@',C),'''    iget-object v0, p0, @C@->mTaskInfo:Landroid/app/ActivityManager$RunningTaskInfo;
    if-eqz v0, :cancel_pending
    iget-boolean v0, v0, Landroid/app/ActivityManager$RunningTaskInfo;->isFocused:Z
    if-eqz v0, :cancel_pending
    iget-object v0, p0, @C@->mDeferredInputLayerPoint'''.replace('@C@',C),1)
 m=m.replace('    :existing\n','''    goto :existing
    :cancel_pending
    const/4 v0, 0x0
    iput-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    iput-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iget-object v0, p0, @C@->mRootView:Landroid/view/View;
    invoke-virtual {v0, p0}, Landroid/view/View;->removeCallbacks(Ljava/lang/Runnable;)Z
    :existing
'''.replace('@C@',C),1)
 return m
edit('updateStatusBarInputLayer(Landroid/graphics/Point;)V',update)
p.write_text(s,encoding='utf-8',newline='\n');(out/'patched-holder.smali').write_text(s,encoding='utf-8',newline='\n')
print('FOCUS_CANDIDATE_OFFLINE; accepted daily APK saved once')
v=Path('work/verify_package_caption_defer.py').read_text().replace("Path('work/systemui-caption-defer')","Path('work/systemui-caption-focus')")
Path('work/verify_package_caption_focus.py').write_text(v,encoding='utf-8',newline='\n')
