from pathlib import Path
import re,shutil
p=Path('work/systemui-caption-toback');root=Path('work/systemui-caption-defer/smali')
C='Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;'
D='Lcom/android/wm/shell/windowdecor/FullscreenTaskWindowDecoration;'
E='Lcom/android/wm/shell/windowdecor/FullscreenTaskWindowDecorController;'
holder=root/'com/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder.smali'
s=Path('work/systemui-caption-focus/patched-holder.smali').read_text(encoding='utf-8')
s+='''
.method public cancelPendingInputLayerForTaskToBack()V
    .locals 1
    iget-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    if-eqz v0, :done
    const-string v0, "CaptionInputLayer#cancelForTaskToBack"
    invoke-static {v0}, Landroid/os/Trace;->beginSection(Ljava/lang/String;)V
    const/4 v0, 0x0
    iput-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    iput-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iget-object v0, p0, @C@->mRootView:Landroid/view/View;
    invoke-virtual {v0, p0}, Landroid/view/View;->removeCallbacks(Ljava/lang/Runnable;)Z
    invoke-static {}, Landroid/os/Trace;->endSection()V
    :done
    return-void
.end method
'''.replace('@C@',C)
holder.write_text(s,encoding='utf-8');(p/'holder-patched.smali').write_text(s,encoding='utf-8')
for name in ['FullscreenTaskWindowDecoration','FullscreenTaskWindowDecorController']:
 src=root/('com/android/wm/shell/windowdecor/'+name+'.smali');backup=p/(name+'-original.smali')
 if not backup.exists():shutil.copyfile(src,backup)
 s=backup.read_text(encoding='utf-8')
 if name=='FullscreenTaskWindowDecoration':
  s+='''
.method public cancelPendingInputLayerForTaskToBack()V
    .locals 1
    iget-object v0, p0, @D@->mHandleBarViewHolder:@C@
    if-eqz v0, :done
    invoke-virtual {v0}, @C@->cancelPendingInputLayerForTaskToBack()V
    :done
    return-void
.end method
'''
 else:
  s+='''
.method public onTaskToBack(Landroid/app/ActivityManager$RunningTaskInfo;)V
    .locals 2
    if-eqz p1, :done
    iget-object v0, p0, @E@->mWindowDecorByTaskId:Landroid/util/SparseArray;
    iget v1, p1, Landroid/app/ActivityManager$RunningTaskInfo;->taskId:I
    invoke-virtual {v0, v1}, Landroid/util/SparseArray;->get(I)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, @D@
    if-eqz v0, :done
    invoke-virtual {v0}, @D@->cancelPendingInputLayerForTaskToBack()V
    :done
    return-void
.end method
'''
 s=s.replace('@C@',C).replace('@D@',D).replace('@E@',E)
 src.write_text(s,encoding='utf-8');(p/(name+'-patched.smali')).write_text(s,encoding='utf-8')
observer=Path('work/caption-closing-source/com/android/wm/shell/fullscreen/FullscreenTaskTransitionObserver.smali').read_text(encoding='utf-8')
pat=r'(?ms)^\.method public onTransitionReady\([^\n]*\n.*?^\.end method'
def edit(m):
 s=m[0];needle='    const/4 v6, 0x1\n';assert s.count(needle)==1
 add='''    const/4 v6, 0x4
    if-ne v4, v6, :original_mode_dispatch
    const-string v6, "FullscreenDecor#taskToBack"
    invoke-static {v6}, Landroid/os/Trace;->beginSection(Ljava/lang/String;)V
    iget-object v4, p0, Lcom/android/wm/shell/fullscreen/FullscreenTaskTransitionObserver;->mWindowDecorViewModel:@E@
    invoke-virtual {v3}, Landroid/window/TransitionInfo$Change;->getTaskInfo()Landroid/app/ActivityManager$RunningTaskInfo;
    move-result-object v6
    invoke-virtual {v4, v6}, @E@->onTaskToBack(Landroid/app/ActivityManager$RunningTaskInfo;)V
    invoke-static {}, Landroid/os/Trace;->endSection()V
    goto :goto_12
    :original_mode_dispatch
'''.replace('@E@',E)
 return s.replace(needle,add+needle)
observer,n=re.subn(pat,edit,observer);assert n==1
(p/'smali4/com/android/wm/shell/fullscreen/FullscreenTaskTransitionObserver.smali').write_text(observer,encoding='utf-8')
(p/'observer-patched.smali').write_text(observer,encoding='utf-8')
shutil.copyfile('work/systemui-caption-focus/classes2-original.dex',p/'classes2-original.dex')
verify=Path('work/verify_package_caption_focus.py').read_text().replace("Path('work/systemui-caption-focus')","Path('work/systemui-caption-toback')")
v2=verify.replace("not k.startswith(C+'->')","not k.startswith((C+'->', '"+D+"->', '"+E+"->'))").replace("p/'SystemUI-caption-defer-candidate.apk'","p/'SystemUI-classes2-intermediate.apk'").replace("p/'validation.json'","p/'classes2-validation.json'")
Path('work/verify_caption_toback_classes2.py').write_text(v2,encoding='utf-8')
v4=verify.replace('classes2','classes4').replace(C,'Lcom/android/wm/shell/fullscreen/FullscreenTaskTransitionObserver;').replace("src=base/'SystemUI-live-20261029.apk'","src=p/'SystemUI-classes2-intermediate.apk'").replace("p/'validation.json'","p/'classes4-validation.json'")
Path('work/verify_caption_toback_classes4.py').write_text(v4,encoding='utf-8')
print('TO_BACK pending-cancellation path prepared; no existing touch window removed')
