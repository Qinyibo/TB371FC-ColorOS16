# OplusGestureAnimationController — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## private cleanUpOnAnimationEnd()V

Disassembly lines 1920–2077.

```smali
.method private cleanUpOnAnimationEnd()V
    .registers 7
    .line 657
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingAnimations:Ljava/util/ArrayList;
    invoke-virtual {v0}, Ljava/util/ArrayList;->size()I
    move-result v0
    const/4 v1, 0x1
    sub-int/2addr v0, v1
    .local v0, "i":I
    :goto_8
    if-ltz v0, :cond_31
    .line 658
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingAnimations:Ljava/util/ArrayList;
    invoke-virtual {v2, v0}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Lcom/android/server/wm/OplusGestureAnimationController$TaskAnimationAdapter;
    .line 660
    .local v2, "taskAdapter":Lcom/android/server/wm/OplusGestureAnimationController$TaskAnimationAdapter;
    sget-object v3, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v5, "removeAnimation:"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v3, v4}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 661
    invoke-virtual {p0, v2}, Lcom/android/server/wm/OplusGestureAnimationController;->removeAnimation(Lcom/android/server/wm/OplusGestureAnimationController$TaskAnimationAdapter;)V
    .line 657
    .end local v2    # "taskAdapter":Lcom/android/server/wm/OplusGestureAnimationController$TaskAnimationAdapter;
    add-int/lit8 v0, v0, -0x1
    goto :goto_8
    .line 663
    .end local v0    # "i":I
    :cond_31
    const/4 v0, 0x0
    iput-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomStack:Lcom/android/server/wm/Task;
    .line 664
    const/4 v2, 0x0
    iput-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetSplitModel:Z
    .line 665
    iput-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragSplitStack:Lcom/android/server/wm/Task;
    .line 666
    iput-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragSplitModel:Z
    .line 667
    iput-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mChangeToZoomTask:Lcom/android/server/wm/Task;
    .line 668
    iput-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomToSplit:Z
    .line 669
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitChildSurface:Ljava/util/ArrayList;
    invoke-virtual {v2}, Ljava/util/ArrayList;->clear()V
    .line 671
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v2, v2, Lcom/android/server/wm/WindowManagerService;->mH:Lcom/android/server/wm/WindowManagerService$H;
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFailsafeRunnable:Ljava/lang/Runnable;
    invoke-virtual {v2, v3}, Lcom/android/server/wm/WindowManagerService$H;->removeCallbacks(Ljava/lang/Runnable;)V
    .line 674
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->unlinkToDeathOfRunner()V
    .line 675
    iput-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mRunner:Landroid/view/IOplusGestureAnimationRunner;
    .line 676
    iget-boolean v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mNeedFullToZoomAnimation:Z
    if-nez v0, :cond_58
    .line 677
    iput-boolean v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCanceled:Z
    .line 679
    :cond_58
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v0, v0, Lcom/android/server/wm/WindowManagerService;->mGlobalLock:Lcom/android/server/wm/WindowManagerGlobalLock;
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->boostPriorityForLockedSection()V
    monitor-enter v0
    .line 680
    :try_start_60
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v1}, Lcom/android/server/wm/DisplayContent;->getDisplayRotation()Lcom/android/server/wm/DisplayRotation;
    move-result-object v1
    invoke-virtual {v1}, Lcom/android/server/wm/DisplayRotation;->resume()V
    .line 681
    monitor-exit v0
    :try_end_6a
    .catchall {:try_start_60 .. :try_end_6a} :catchall_71
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    .line 682
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->clearAnimThread()V
    .line 683
    return-void
    .line 681
    :catchall_71
    move-exception v1
    :try_start_72
    monitor-exit v0
    :try_end_73
    .catchall {:try_start_72 .. :try_end_73} :catchall_71
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    throw v1
.end method
```

## private synthetic lambda$new$0()V

Disassembly lines 5397–5406.

```smali
.method private synthetic lambda$new$0()V
    .registers 2
    .line 134
    const-string v0, "failSafeRunnable"
    invoke-virtual {p0, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->cancelAnimation(Ljava/lang/String;)V
    return-void
.end method
```

## cancelAnimation(Ljava/lang/String;)V

Disassembly lines 6956–7079.

```smali
.method cancelAnimation(Ljava/lang/String;)V
    .registers 6
    .param p1, "reason"    # Ljava/lang/String;
    .line 576
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    invoke-virtual {v0}, Lcom/android/server/wm/WindowManagerService;->getWindowManagerLock()Ljava/lang/Object;
    move-result-object v0
    monitor-enter v0
    .line 577
    :try_start_7
    iget-boolean v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCanceled:Z
    if-eqz v1, :cond_d
    .line 579
    monitor-exit v0
    return-void
    .line 581
    :cond_d
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v1, v1, Lcom/android/server/wm/WindowManagerService;->mH:Lcom/android/server/wm/WindowManagerService$H;
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFailsafeRunnable:Ljava/lang/Runnable;
    invoke-virtual {v1, v2}, Lcom/android/server/wm/WindowManagerService$H;->removeCallbacks(Ljava/lang/Runnable;)V
    .line 582
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v1, v1, Lcom/android/server/wm/WindowManagerService;->mAnimationHandler:Landroid/os/Handler;
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mStartFullScreenAnimation:Ljava/lang/Runnable;
    invoke-virtual {v1, v2}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    .line 583
    const/4 v1, 0x1
    iput-boolean v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCanceled:Z
    :try_end_22
    .catchall {:try_start_7 .. :try_end_22} :catchall_52
    .line 588
    :try_start_22
    sget-object v1, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "cancelAnimation:  reason = "
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static {v1, v2}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 589
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mRunner:Landroid/view/IOplusGestureAnimationRunner;
    invoke-interface {v1}, Landroid/view/IOplusGestureAnimationRunner;->onAnimationCanceled()V
    :try_end_3f
    .catch Landroid/os/RemoteException; {:try_start_22 .. :try_end_3f} :catch_40
    .catchall {:try_start_22 .. :try_end_3f} :catchall_52
    .line 592
    goto :goto_48
    .line 590
    :catch_40
    move-exception v1
    .line 591
    .local v1, "e":Landroid/os/RemoteException;
    :try_start_41
    sget-object v2, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    const-string v3, "Failed to cancel gesture animation"
    invoke-static {v2, v3, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    .line 593
    .end local v1    # "e":Landroid/os/RemoteException;
    :goto_48
    invoke-virtual {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->cancelAnimationInRun()V
    .line 594
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCallbacks:Lcom/android/server/wm/IOplusGestureAnimationCallbacks;
    invoke-interface {v1}, Lcom/android/server/wm/IOplusGestureAnimationCallbacks;->onAnimationFinished()V
    .line 595
    monitor-exit v0
    .line 596
    return-void
    .line 595
    :catchall_52
    move-exception v1
    monitor-exit v0
    :try_end_54
    .catchall {:try_start_41 .. :try_end_54} :catchall_52
    throw v1
.end method
```

## cancelAnimationInRun()V

Disassembly lines 7081–7185.

```smali
.method cancelAnimationInRun()V
    .registers 4
    .line 600
    :try_start_0
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    if-eqz v0, :cond_9
    .line 601
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFinishAnim:Landroid/animation/ValueAnimator;
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    .line 603
    :cond_9
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitToZoomFinishAnim:Landroid/animation/ValueAnimator;
    if-eqz v0, :cond_12
    .line 604
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitToZoomFinishAnim:Landroid/animation/ValueAnimator;
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    .line 606
    :cond_12
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomToSplitFinishAnim:Landroid/animation/ValueAnimator;
    if-eqz v0, :cond_1b
    .line 607
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomToSplitFinishAnim:Landroid/animation/ValueAnimator;
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    .line 609
    :cond_1b
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomToSplitFinishAnimReplaceMode:Landroid/animation/ValueAnimator;
    if-eqz v0, :cond_24
    .line 610
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomToSplitFinishAnimReplaceMode:Landroid/animation/ValueAnimator;
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    .line 612
    :cond_24
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragDimAnimation:Landroid/animation/ValueAnimator;
    if-eqz v0, :cond_2d
    .line 613
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragDimAnimation:Landroid/animation/ValueAnimator;
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    :try_end_2d
    .catch Landroid/util/AndroidRuntimeException; {:try_start_0 .. :try_end_2d} :catch_30
    .catchall {:try_start_0 .. :try_end_2d} :catchall_2e
    .line 618
    :cond_2d
    goto :goto_39
    :catchall_2e
    move-exception v0
    goto :goto_3e
    .line 615
    :catch_30
    move-exception v0
    .line 616
    .local v0, "e":Landroid/util/AndroidRuntimeException;
    :try_start_31
    sget-object v1, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    const-string v2, "Failed to cancel gesture animation, AndroidRuntimeException"
    invoke-static {v1, v2}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_38
    .catchall {:try_start_31 .. :try_end_38} :catchall_2e
    .line 618
    nop
    .end local v0    # "e":Landroid/util/AndroidRuntimeException;
    :goto_39
    invoke-virtual {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->finishGestureAnimationUncheck()V
    .line 619
    nop
    .line 620
    return-void
    .line 618
    :goto_3e
    invoke-virtual {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->finishGestureAnimationUncheck()V
    .line 619
    throw v0
.end method
```

## cleanupAnimation()V

Disassembly lines 7421–7516.

```smali
.method cleanupAnimation()V
    .registers 5
    .line 623
    iget-boolean v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mNeedFullToZoomAnimation:Z
    if-eqz v0, :cond_8
    .line 624
    invoke-virtual {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->performFinishAnimation()V
    goto :goto_43
    .line 626
    :cond_8
    new-instance v0, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v0}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 627
    .local v0, "t":Landroid/view/SurfaceControl$Transaction;
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragAnimationDimSurface:Ljava/util/ArrayList;
    invoke-virtual {v1}, Ljava/util/ArrayList;->size()I
    move-result v1
    add-int/lit8 v1, v1, -0x1
    .local v1, "i":I
    :goto_15
    if-ltz v1, :cond_3d
    .line 628
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragAnimationDimSurface:Ljava/util/ArrayList;
    invoke-virtual {v2, v1}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Landroid/view/SurfaceControl;
    .line 629
    .local v2, "dimSurface":Landroid/view/SurfaceControl;
    if-eqz v2, :cond_3a
    invoke-virtual {v2}, Landroid/view/SurfaceControl;->isValid()Z
    move-result v3
    if-eqz v3, :cond_3a
    .line 630
    iget-boolean v3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFoldFeature:Z
    if-eqz v3, :cond_37
    .line 631
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitChildSurface:Ljava/util/ArrayList;
    invoke-virtual {v3, v2}, Ljava/util/ArrayList;->contains(Ljava/lang/Object;)Z
    move-result v3
    if-nez v3, :cond_3a
    .line 632
    invoke-virtual {v0, v2}, Landroid/view/SurfaceControl$Transaction;->remove(Landroid/view/SurfaceControl;)Landroid/view/SurfaceControl$Transaction;
    goto :goto_3a
    .line 635
    :cond_37
    invoke-virtual {v0, v2}, Landroid/view/SurfaceControl$Transaction;->remove(Landroid/view/SurfaceControl;)Landroid/view/SurfaceControl$Transaction;
    .line 627
    .end local v2    # "dimSurface":Landroid/view/SurfaceControl;
    :cond_3a
    :goto_3a
    add-int/lit8 v1, v1, -0x1
    goto :goto_15
    .line 639
    .end local v1    # "i":I
    :cond_3d
    invoke-virtual {v0}, Landroid/view/SurfaceControl$Transaction;->apply()V
    .line 640
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->cleanUpOnAnimationEnd()V
    .line 642
    .end local v0    # "t":Landroid/view/SurfaceControl$Transaction;
    :goto_43
    return-void
.end method
```

## public finishGestureAnimationUncheck()V

Disassembly lines 7780–7845.

```smali
.method public finishGestureAnimationUncheck()V
    .registers 4
    .line 2128
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    invoke-virtual {v0}, Lcom/android/server/wm/WindowManagerService;->getWindowManagerLock()Ljava/lang/Object;
    move-result-object v0
    monitor-enter v0
    .line 2129
    :try_start_7
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingNewTaskTargets:Landroid/util/IntArray;
    invoke-virtual {v1}, Landroid/util/IntArray;->size()I
    move-result v1
    add-int/lit8 v1, v1, -0x1
    .local v1, "i":I
    :goto_f
    if-ltz v1, :cond_1d
    .line 2130
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingNewTaskTargets:Landroid/util/IntArray;
    invoke-virtual {v2, v1}, Landroid/util/IntArray;->get(I)I
    move-result v2
    invoke-direct {p0, v2}, Lcom/android/server/wm/OplusGestureAnimationController;->removeTaskInternal(I)Z
    .line 2129
    add-int/lit8 v1, v1, -0x1
    goto :goto_f
    .line 2132
    .end local v1    # "i":I
    :cond_1d
    monitor-exit v0
    :try_end_1e
    .catchall {:try_start_7 .. :try_end_1e} :catchall_24
    .line 2135
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mCallbacks:Lcom/android/server/wm/IOplusGestureAnimationCallbacks;
    invoke-interface {v0}, Lcom/android/server/wm/IOplusGestureAnimationCallbacks;->onAnimationFinished()V
    .line 2136
    return-void
    .line 2132
    :catchall_24
    move-exception v1
    :try_start_25
    monitor-exit v0
    :try_end_26
    .catchall {:try_start_25 .. :try_end_26} :catchall_24
    throw v1
.end method
```

## scheduleFailsafe()V

Disassembly lines 10681–10697.

```smali
.method scheduleFailsafe()V
    .registers 5
    .line 686
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v0, v0, Lcom/android/server/wm/WindowManagerService;->mH:Lcom/android/server/wm/WindowManagerService$H;
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mFailsafeRunnable:Ljava/lang/Runnable;
    const-wide/16 v2, 0x3e8
    invoke-virtual {v0, v1, v2, v3}, Lcom/android/server/wm/WindowManagerService$H;->postDelayed(Ljava/lang/Runnable;J)Z
    .line 687
    return-void
.end method
```

## public shouldApplyInputConsumer(Lcom/android/server/wm/ActivityRecord;)Z

Disassembly lines 10819–10892.

```smali
.method public shouldApplyInputConsumer(Lcom/android/server/wm/ActivityRecord;)Z
    .registers 5
    .param p1, "activity"    # Lcom/android/server/wm/ActivityRecord;
    .line 1994
    sget-object v0, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v2, "shouldApplyInputConsumer activity:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, " mTargetActivityRecord:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetActivityRecord:Lcom/android/server/wm/ActivityRecord;
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, " mGestureFullScreenDragStart:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mGestureFullScreenDragStart:Z
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 1995
    iget-boolean v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mGestureFullScreenDragStart:Z
    if-eqz v0, :cond_3f
    if-eqz p1, :cond_3f
    invoke-virtual {p0, p1}, Lcom/android/server/wm/OplusGestureAnimationController;->isTargetApp(Lcom/android/server/wm/ActivityRecord;)Z
    move-result v0
    if-nez v0, :cond_3f
    const/4 v0, 0x1
    goto :goto_40
    :cond_3f
    const/4 v0, 0x0
    :goto_40
    return v0
.end method
```

## public updateInputConsumerForApp(Landroid/view/InputWindowHandle;Z)Z

Disassembly lines 11249–11324.

```smali
.method public updateInputConsumerForApp(Landroid/view/InputWindowHandle;Z)Z
    .registers 7
    .param p1, "inputWindowHandle"    # Landroid/view/InputWindowHandle;
    .param p2, "hasFocus"    # Z
    .line 2004
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetActivityRecord:Lcom/android/server/wm/ActivityRecord;
    if-eqz v0, :cond_b
    .line 2005
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetActivityRecord:Lcom/android/server/wm/ActivityRecord;
    invoke-virtual {v0}, Lcom/android/server/wm/ActivityRecord;->findMainWindow()Lcom/android/server/wm/WindowState;
    move-result-object v0
    goto :goto_c
    .line 2006
    :cond_b
    const/4 v0, 0x0
    :goto_c
    nop
    .line 2007
    .local v0, "targetAppMainWindow":Lcom/android/server/wm/WindowState;
    sget-object v1, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v3, "updateInputConsumerForApp targetAppMainWindow:"
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static {v1, v2}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 2008
    if-eqz v0, :cond_36
    .line 2009
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTmpRect:Landroid/graphics/Rect;
    invoke-virtual {v0, v1}, Lcom/android/server/wm/WindowState;->getBounds(Landroid/graphics/Rect;)V
    .line 2011
    iget-object v1, p1, Landroid/view/InputWindowHandle;->touchableRegion:Landroid/graphics/Region;
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTmpRect:Landroid/graphics/Rect;
    invoke-virtual {v1, v2}, Landroid/graphics/Region;->set(Landroid/graphics/Rect;)Z
    .line 2012
    const/4 v1, 0x1
    return v1
    .line 2014
    :cond_36
    const/4 v1, 0x0
    return v1
.end method
```
