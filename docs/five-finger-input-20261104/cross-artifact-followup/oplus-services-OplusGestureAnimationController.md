# OplusGestureAnimationController — selected methods

Artifact `oplus-services`, SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`. Selected complete bodies, empty lines removed; no opcode/label/register/handler changes. Ranges are local disassembly lines. Not a patch.

## performFinishAnimation()V

Local lines 9386–9406.

```smali
.method performFinishAnimation()V
    .registers 3
    .line 1546
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationHandler:Landroid/os/Handler;
    if-eqz v0, :cond_e
    .line 1547
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationHandler:Landroid/os/Handler;
    new-instance v1, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda7;
    invoke-direct {v1, p0}, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda7;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;)V
    invoke-virtual {v0, v1}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z
    .line 1549
    :cond_e
    return-void
.end method
```

## performFinishAnimationInWms()V

Local lines 9408–9553.

```smali
.method performFinishAnimationInWms()V
    .registers 5
    .line 1551
    sget-object v0, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v2, "performFinishAnimationInWms mDragAnimationDimSurface.size:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragAnimationDimSurface:Ljava/util/ArrayList;
    invoke-virtual {v2}, Ljava/util/ArrayList;->size()I
    move-result v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, " cancel:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCanceled:Z
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 1552
    iget-boolean v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCanceled:Z
    if-eqz v0, :cond_36
    .line 1553
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->removeDimSurface()V
    .line 1554
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->clearFlexibleTaskMark()V
    .line 1555
    return-void
    .line 1557
    :cond_36
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragAnimationDimSurface:Ljava/util/ArrayList;
    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I
    move-result v0
    if-lez v0, :cond_80
    .line 1558
    new-instance v0, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v0}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 1559
    .local v0, "animTransaction":Landroid/view/SurfaceControl$Transaction;
    const/4 v1, 0x2
    new-array v1, v1, [F
    fill-array-data v1, :array_82
    invoke-static {v1}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;
    move-result-object v1
    iput-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    .line 1560
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    new-instance v2, Lcom/android/server/wm/OplusGestureAnimationController$2;
    invoke-direct {v2, p0, v0}, Lcom/android/server/wm/OplusGestureAnimationController$2;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;Landroid/view/SurfaceControl$Transaction;)V
    invoke-virtual {v1, v2}, Landroid/animation/ValueAnimator;->addUpdateListener(Landroid/animation/ValueAnimator$AnimatorUpdateListener;)V
    .line 1574
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    const-wide/16 v2, 0xfa
    invoke-virtual {v1, v2, v3}, Landroid/animation/ValueAnimator;->setStartDelay(J)V
    .line 1575
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    const-wide/16 v2, 0x15e
    invoke-virtual {v1, v2, v3}, Landroid/animation/ValueAnimator;->setDuration(J)Landroid/animation/ValueAnimator;
    .line 1576
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    new-instance v2, Landroid/view/animation/AccelerateDecelerateInterpolator;
    invoke-direct {v2}, Landroid/view/animation/AccelerateDecelerateInterpolator;-><init>()V
    invoke-virtual {v1, v2}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 1577
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    new-instance v2, Lcom/android/server/wm/OplusGestureAnimationController$3;
    invoke-direct {v2, p0}, Lcom/android/server/wm/OplusGestureAnimationController$3;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;)V
    invoke-virtual {v1, v2}, Landroid/animation/ValueAnimator;->addListener(Landroid/animation/Animator$AnimatorListener;)V
    .line 1602
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    invoke-virtual {v1}, Landroid/animation/ValueAnimator;->start()V
    .line 1604
    .end local v0    # "animTransaction":Landroid/view/SurfaceControl$Transaction;
    :cond_80
    return-void
    nop
    :array_82
    .array-data 4
        0x3f800000    # 1.0f
        0x0
    .end array-data
.end method
```
