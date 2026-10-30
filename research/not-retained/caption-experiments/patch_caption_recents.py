from pathlib import Path
import shutil,re
out=Path('work/systemui-caption-recents');out.mkdir(exist_ok=True)
src=Path('work/systemui-caption-focus')
holder=Path('work/systemui-caption-defer/smali/com/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder.smali')
s=(src/'patched-holder.smali').read_text(encoding='utf-8')
C='Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;'
prefix='''
    iget-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    if-eqz v0, :recents_original
    const-string v0, "CaptionInputLayer#cancelForRecents"
    invoke-static {v0}, Landroid/os/Trace;->beginSection(Ljava/lang/String;)V
    const/4 v0, 0x0
    iput-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    iput-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iget-object v0, p0, @C@->mRootView:Landroid/view/View;
    invoke-virtual {v0, p0}, Landroid/view/View;->removeCallbacks(Ljava/lang/Runnable;)Z
    invoke-static {}, Landroid/os/Trace;->endSection()V
    :recents_original
'''.replace('@C@',C)
pat=r'(?ms)(^\.method public onRecentAnimationStart\(\)V\n\s*\.registers 2\n)'
s,n=re.subn(pat,lambda m:m[1]+prefix,s);assert n==1
holder.write_text(s,encoding='utf-8',newline='\n');(out/'patched-holder.smali').write_text(s,encoding='utf-8',newline='\n')
shutil.copyfile(src/'classes2-original.dex',out/'classes2-original.dex')
verify=Path('work/verify_package_caption_focus.py').read_text().replace("Path('work/systemui-caption-focus')","Path('work/systemui-caption-recents')")
Path('work/verify_package_caption_recents.py').write_text(verify,encoding='utf-8',newline='\n')
print('Recents cancellation added to the existing holder only')
