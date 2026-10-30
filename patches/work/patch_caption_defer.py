from pathlib import Path
import re,hashlib,json
root=Path('work/systemui-caption-defer');p=root/'smali/com/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder.smali';backup=root/'original-holder.smali'
if not backup.exists():backup.write_bytes(p.read_bytes())
s=backup.read_text(encoding='utf-8');C='Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;'
assert '.implements Ljava/lang/Runnable;' not in s and 'run()V' not in s
s=s.replace('.super Ljava/lang/Object;','.super Ljava/lang/Object;\n.implements Ljava/lang/Runnable;',1)
fields='''\n.field private mDeferredInputLayerPending:Z
.field private mDeferredInputLayerPoint:Landroid/graphics/Point;
.field private mDeferredInputLayerWidth:I
.field private mDeferredInputLayerHeight:I
'''
s=s.replace('# direct methods',fields+'\n# direct methods',1)
s=s.replace('.method private createStatusBarInputLayer(Landroid/graphics/Point;II)V','.method private createStatusBarInputLayerNow(Landroid/graphics/Point;II)V',1)
wrapper='''
.method private createStatusBarInputLayer(Landroid/graphics/Point;II)V
    .locals 3
    iget-object v0, p0, @C@->mRootView:Landroid/view/View;
    invoke-virtual {v0, p0}, Landroid/view/View;->removeCallbacks(Ljava/lang/Runnable;)Z
    new-instance v1, Landroid/graphics/Point;
    invoke-direct {v1, p1}, Landroid/graphics/Point;-><init>(Landroid/graphics/Point;)V
    iput-object v1, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iput p2, p0, @C@->mDeferredInputLayerWidth:I
    iput p3, p0, @C@->mDeferredInputLayerHeight:I
    const/4 v1, 0x1
    iput-boolean v1, p0, @C@->mDeferredInputLayerPending:Z
    const-wide/16 v1, 0x190
    invoke-virtual {v0, p0, v1, v2}, Landroid/view/View;->postDelayed(Ljava/lang/Runnable;J)Z
    return-void
.end method
'''.replace('@C@',C)
s=s.replace('.method private createStatusBarInputLayerNow',wrapper+'\n.method private createStatusBarInputLayerNow',1)
def replace_method(name,body):
 global s
 pat=r'(?ms)^\.method [^\n]* '+re.escape(name)+r'[^\n]*\n.*?^\.end method'
 s,n=re.subn(pat,lambda m:body.strip(),s);assert n==1,(name,n)
replace_method('hasStatusBarInputLayer()Z','''
.method private hasStatusBarInputLayer()Z
    .locals 1
    iget-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    if-nez v0, :present
    iget-object v0, p0, @C@->mStatusBarInputLayer:Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder$StatusBarInputLayer;
    if-nez v0, :present
    const/4 v0, 0x0
    return v0
    :present
    const/4 v0, 0x1
    return v0
.end method
'''.replace('@C@',C))
replace_method('updateStatusBarInputLayer(Landroid/graphics/Point;)V','''
.method private updateStatusBarInputLayer(Landroid/graphics/Point;)V
    .locals 3
    iget-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    if-eqz v0, :existing
    iget-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    if-eqz v0, :existing
    iget v1, p1, Landroid/graphics/Point;->x:I
    iget v2, p1, Landroid/graphics/Point;->y:I
    invoke-virtual {v0, v1, v2}, Landroid/graphics/Point;->set(II)V
    :existing
    iget-object v0, p0, @C@->mStatusBarInputLayer:Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder$StatusBarInputLayer;
    if-eqz v0, :done
    iget v1, p1, Landroid/graphics/Point;->x:I
    iget v2, p1, Landroid/graphics/Point;->y:I
    invoke-virtual {v0, v1, v2}, Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder$StatusBarInputLayer;->setPosition(II)V
    :done
    return-void
.end method
'''.replace('@C@',C))
pat=r'(?ms)(^\.method public disposeStatusBarInputLayer\(\)V\n\s*\.registers 2\n)'
prefix='''
    const/4 v0, 0x0
    iput-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    iput-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iget-object v0, p0, @C@->mRootView:Landroid/view/View;
    invoke-virtual {v0, p0}, Landroid/view/View;->removeCallbacks(Ljava/lang/Runnable;)Z
'''.replace('@C@',C)
s,n=re.subn(pat,lambda m:m.group(1)+prefix,s);assert n==1
s+='''
.method public run()V
    .locals 4
    iget-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    if-eqz v0, :done
    const/4 v0, 0x0
    iput-boolean v0, p0, @C@->mDeferredInputLayerPending:Z
    iget-object v1, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    iput-object v0, p0, @C@->mDeferredInputLayerPoint:Landroid/graphics/Point;
    if-eqz v1, :done
    iget v2, p0, @C@->mDeferredInputLayerWidth:I
    iget v3, p0, @C@->mDeferredInputLayerHeight:I
    invoke-direct {p0, v1, v2, v3}, @C@->createStatusBarInputLayerNow(Landroid/graphics/Point;II)V
    :done
    return-void
.end method
'''.replace('@C@',C)
p.write_text(s,encoding='utf-8',newline='\n')
(root/'patch-note.json').write_text(json.dumps({'status':'OFFLINE_ONLY_NOT_DEPLOYED','delay_ms':400,'original_holder_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'patched_holder_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'intent':'defer auxiliary statusbar caption input window; cancel pending creation when caption is hidden/disposed; keep existing token fallback; retain split menu functionality after settling','risks':['400ms delayed auxiliary touch region availability','runtime verifier and behavior not tested']},indent=2),encoding='utf-8')
print('Patched one holder class offline')
