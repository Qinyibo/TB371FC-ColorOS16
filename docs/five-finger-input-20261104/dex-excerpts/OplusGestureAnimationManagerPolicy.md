# OplusGestureAnimationManagerPolicy — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## private synthetic lambda$finishAnimation$0()V

Disassembly lines 1707–1762.

```smali
.method private synthetic lambda$finishAnimation$0()V
    .registers 6
    .line 610
    new-instance v0, Landroid/app/OplusStatusBarManager;
    invoke-direct {v0}, Landroid/app/OplusStatusBarManager;-><init>()V
    .line 611
    .local v0, "statusBarManager":Landroid/app/OplusStatusBarManager;
    nop
    .line 613
    const/high16 v1, 0x20000000
    :try_start_8
    invoke-virtual {v0, v1}, Landroid/app/OplusStatusBarManager;->toggleSplitScreen(I)V
    :try_end_b
    .catch Landroid/os/RemoteException; {:try_start_8 .. :try_end_b} :catch_c
    .line 616
    goto :goto_25
    .line 614
    :catch_c
    move-exception v1
    .line 615
    .local v1, "e":Landroid/os/RemoteException;
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, " toggleSplitScreen error e = "
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    invoke-static {v2, v3}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 618
    .end local v1    # "e":Landroid/os/RemoteException;
    :goto_25
    return-void
.end method
```

## private playReboundAnimIfNeed()Z

Disassembly lines 1782–2093.

```smali
.method private playReboundAnimIfNeed()Z
    .registers 9
    .line 466
    iget v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v1
    cmpg-float v0, v0, v1
    const/4 v1, 0x1
    const/4 v2, 0x2
    if-gez v0, :cond_41
    .line 468
    new-instance v0, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v0}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 469
    .local v0, "t":Landroid/view/SurfaceControl$Transaction;
    const/16 v3, 0xc8
    .line 470
    .local v3, "animationDuration":I
    new-array v2, v2, [F
    fill-array-data v2, :array_fe
    invoke-static {v2}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;
    move-result-object v2
    .line 471
    .local v2, "enlargeAnimtor":Landroid/animation/ValueAnimator;
    int-to-long v4, v3
    invoke-virtual {v2, v4, v5}, Landroid/animation/ValueAnimator;->setDuration(J)Landroid/animation/ValueAnimator;
    .line 472
    sget-object v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_CIRC:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v4}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 473
    new-instance v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;
    invoke-direct {v4, p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    invoke-virtual {v2, v4}, Landroid/animation/ValueAnimator;->addListener(Landroid/animation/Animator$AnimatorListener;)V
    .line 493
    new-instance v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$4;
    invoke-direct {v4, p0, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$4;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl$Transaction;)V
    invoke-virtual {v2, v4}, Landroid/animation/ValueAnimator;->addUpdateListener(Landroid/animation/ValueAnimator$AnimatorUpdateListener;)V
    .line 505
    invoke-virtual {v2}, Landroid/animation/ValueAnimator;->start()V
    .line 506
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    const-string/jumbo v5, "playReboundAnimIfNeed need enlarge"
    invoke-static {v4, v5}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 507
    return v1
    .line 508
    .end local v0    # "t":Landroid/view/SurfaceControl$Transaction;
    .end local v2    # "enlargeAnimtor":Landroid/animation/ValueAnimator;
    .end local v3    # "animationDuration":I
    :cond_41
    iget v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v3
    cmpl-float v0, v0, v3
    if-lez v0, :cond_e5
    iget v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    const v3, 0x3f40068e    # 0.7501f
    cmpg-float v0, v0, v3
    if-gtz v0, :cond_e5
    .line 510
    new-instance v0, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v0}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 511
    .restart local v0    # "t":Landroid/view/SurfaceControl$Transaction;
    const/16 v3, 0x12c
    .line 512
    .restart local v3    # "animationDuration":I
    new-array v2, v2, [F
    fill-array-data v2, :array_106
    invoke-static {v2}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;
    move-result-object v2
    .line 513
    .local v2, "shrinkAnimtor":Landroid/animation/ValueAnimator;
    int-to-long v4, v3
    invoke-virtual {v2, v4, v5}, Landroid/animation/ValueAnimator;->setDuration(J)Landroid/animation/ValueAnimator;
    .line 515
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mContext:Landroid/content/Context;
    invoke-virtual {v4}, Landroid/content/Context;->getContentResolver()Landroid/content/ContentResolver;
    move-result-object v4
    const-string/jumbo v5, "four_drag_window_drop_animode"
    const/4 v6, 0x7
    invoke-static {v4, v5, v6}, Landroid/provider/Settings$System;->getInt(Landroid/content/ContentResolver;Ljava/lang/String;I)I
    move-result v4
    .line 516
    .local v4, "fourDragWindowDropMode":I
    packed-switch v4, :pswitch_data_e8
    goto :goto_b3
    .line 542
    :pswitch_7a
    new-instance v5, Landroid/view/animation/LinearInterpolator;
    invoke-direct {v5}, Landroid/view/animation/LinearInterpolator;-><init>()V
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    goto :goto_b3
    .line 539
    :pswitch_83
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_CIRC:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 540
    goto :goto_b3
    .line 536
    :pswitch_89
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_QUINT:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 537
    goto :goto_b3
    .line 533
    :pswitch_8f
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_CUBIC:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 534
    goto :goto_b3
    .line 530
    :pswitch_95
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_SINE:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 531
    goto :goto_b3
    .line 527
    :pswitch_9b
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_BACK:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 528
    goto :goto_b3
    .line 524
    :pswitch_a1
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_EXPO:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 525
    goto :goto_b3
    .line 521
    :pswitch_a7
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_QUART:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 522
    goto :goto_b3
    .line 518
    :pswitch_ad
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_QUAD:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 519
    nop
    .line 545
    :goto_b3
    sget-object v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_CIRC:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 546
    new-instance v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$5;
    invoke-direct {v5, p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$5;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->addListener(Landroid/animation/Animator$AnimatorListener;)V
    .line 566
    new-instance v5, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$6;
    invoke-direct {v5, p0, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$6;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl$Transaction;)V
    invoke-virtual {v2, v5}, Landroid/animation/ValueAnimator;->addUpdateListener(Landroid/animation/ValueAnimator$AnimatorUpdateListener;)V
    .line 587
    invoke-virtual {v2}, Landroid/animation/ValueAnimator;->start()V
    .line 588
    iget-object v5, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v6, Ljava/lang/StringBuilder;
    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v7, "playReboundAnimIfNeed need shrink fourDragWindowDropMode= "
    invoke-virtual {v6, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v6
    invoke-virtual {v6, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v6
    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v6
    invoke-static {v5, v6}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 589
    return v1
    .line 591
    .end local v0    # "t":Landroid/view/SurfaceControl$Transaction;
    .end local v2    # "shrinkAnimtor":Landroid/animation/ValueAnimator;
    .end local v3    # "animationDuration":I
    .end local v4    # "fourDragWindowDropMode":I
    :cond_e5
    const/4 v0, 0x0
    return v0
    nop
    :pswitch_data_e8
    .packed-switch 0x0
        :pswitch_ad
        :pswitch_a7
        :pswitch_a1
        :pswitch_9b
        :pswitch_95
        :pswitch_8f
        :pswitch_89
        :pswitch_83
        :pswitch_7a
    .end packed-switch
    :array_fe
    .array-data 4
        0x0
        0x3f800000    # 1.0f
    .end array-data
    :array_106
    .array-data 4
        0x0
        0x3f800000    # 1.0f
    .end array-data
.end method
```

## private resetGestureAnimation()V

Disassembly lines 2095–2163.

```smali
.method private resetGestureAnimation()V
    .registers 5
    .line 450
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    if-eqz v0, :cond_2c
    .line 452
    const/4 v0, 0x0
    :try_start_5
    new-instance v1, Landroid/os/Bundle;
    invoke-direct {v1}, Landroid/os/Bundle;-><init>()V
    .line 453
    .local v1, "options":Landroid/os/Bundle;
    const-string v2, "GestureMode"
    const/4 v3, 0x1
    invoke-virtual {v1, v2, v3}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 454
    const-string v2, "Change"
    invoke-virtual {v1, v2, v0}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 455
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    invoke-interface {v2, v1}, Landroid/view/IOplusGestureAnimationController;->finishGestureAnimation(Landroid/os/Bundle;)V
    :try_end_1a
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_1a} :catch_1b
    .line 458
    .end local v1    # "options":Landroid/os/Bundle;
    goto :goto_1f
    .line 456
    :catch_1b
    move-exception v1
    .line 457
    .local v1, "e":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V
    .line 459
    .end local v1    # "e":Ljava/lang/Exception;
    :goto_1f
    const/4 v1, 0x0
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    .line 460
    iput-boolean v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 461
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    const-string/jumbo v1, "resetGestureAnimation****"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 463
    :cond_2c
    return-void
.end method
```

## public finishAnimation()V

Disassembly lines 3876–4384.

```smali
.method public finishAnimation()V
    .registers 14
    .line 595
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    const/16 v1, 0x4e8a
    const/4 v2, 0x0
    invoke-static {v0, v2, v1}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 596
    iput-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 597
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v3, "finishAnimation: mController = "
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v3, "  mAnimationSurface = "
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v3, "   mFinalCrop = "
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v3, "  mFinalScale = "
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalScale:F
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(F)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v3, "  mScale = "
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(F)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 599
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    const/4 v1, 0x0
    if-eqz v0, :cond_1a4
    .line 600
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    if-nez v0, :cond_62
    .line 601
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->resetGestureAnimation()V
    .line 602
    return-void
    .line 604
    :cond_62
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->playReboundAnimIfNeed()Z
    move-result v0
    if-eqz v0, :cond_69
    .line 605
    return-void
    .line 607
    :cond_69
    iget v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v3
    cmpg-float v0, v0, v3
    const-string/jumbo v3, "flexibleActived"
    const-string v4, "Change"
    const-string v5, "Scale"
    const-string v6, "Rotation"
    const-string v7, "Bound"
    const-string v8, "TaskId"
    const-string v9, "GestureMode"
    const/4 v10, 0x1
    if-gtz v0, :cond_fd
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    iget v0, v0, Landroid/graphics/Rect;->left:I
    if-gez v0, :cond_8f
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    iget v0, v0, Landroid/graphics/Rect;->top:I
    if-ltz v0, :cond_fd
    .line 609
    :cond_8f
    :try_start_8f
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mHandler:Landroid/os/Handler;
    new-instance v11, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$$ExternalSyntheticLambda0;
    invoke-direct {v11, p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$$ExternalSyntheticLambda0;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    invoke-virtual {v0, v11}, Landroid/os/Handler;->post(Ljava/lang/Runnable;)Z
    .line 619
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    iget v11, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mlastX:I
    iget v12, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mlastY:I
    invoke-virtual {v0, v11, v12}, Landroid/graphics/Rect;->offsetTo(II)V
    .line 621
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    invoke-direct {p0, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->updateRealCropRect(Landroid/graphics/Rect;)V
    .line 622
    new-instance v0, Landroid/os/Bundle;
    invoke-direct {v0}, Landroid/os/Bundle;-><init>()V
    .line 623
    .local v0, "options":Landroid/os/Bundle;
    invoke-virtual {v0, v9, v10}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 624
    iget v9, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationTaskId:I
    invoke-virtual {v0, v8, v9}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 625
    iget-object v8, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    invoke-virtual {v0, v7, v8}, Landroid/os/Bundle;->putParcelable(Ljava/lang/String;Landroid/os/Parcelable;)V
    .line 626
    iget v7, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mRotation:I
    invoke-virtual {v0, v6, v7}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 627
    const/high16 v6, 0x3f800000    # 1.0f
    .line 628
    .local v6, "finalScale":F
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v7
    invoke-virtual {v0, v5, v7}, Landroid/os/Bundle;->putFloat(Ljava/lang/String;F)V
    .line 629
    invoke-virtual {v0, v4, v10}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 630
    iget-boolean v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mIsFlexibleEnabled:Z
    invoke-virtual {v0, v3, v4}, Landroid/os/Bundle;->putBoolean(Ljava/lang/String;Z)V
    .line 631
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string v5, "###finishGestureAnimation:"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v3, v4}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 632
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    invoke-interface {v3, v0}, Landroid/view/IOplusGestureAnimationController;->finishGestureAnimation(Landroid/os/Bundle;)V
    .line 633
    iput-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    :try_end_ee
    .catch Ljava/lang/Exception; {:try_start_8f .. :try_end_ee} :catch_ef
    .line 638
    .end local v0    # "options":Landroid/os/Bundle;
    .end local v6    # "finalScale":F
    goto :goto_f7
    .line 634
    :catch_ef
    move-exception v0
    .line 635
    .local v0, "e":Ljava/lang/Exception;
    invoke-virtual {v0}, Ljava/lang/Exception;->printStackTrace()V
    .line 636
    iput-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 637
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    .line 639
    .end local v0    # "e":Ljava/lang/Exception;
    :goto_f7
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    .line 640
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    goto/16 :goto_1ab
    .line 642
    :cond_fd
    iget v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mScale:F
    const/high16 v11, 0x3f800000    # 1.0f
    sub-float v0, v11, v0
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v12
    sub-float/2addr v11, v12
    div-float/2addr v0, v11
    const/high16 v11, 0x43480000    # 200.0f
    mul-float/2addr v0, v11
    float-to-int v0, v0
    .line 643
    .local v0, "animationDuration":I
    if-gtz v0, :cond_16c
    .line 644
    iget-object v11, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    if-eqz v11, :cond_1a3
    .line 647
    :try_start_113
    iget-object v11, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    invoke-direct {p0, v11}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->updateRealCropRect(Landroid/graphics/Rect;)V
    .line 648
    new-instance v11, Landroid/os/Bundle;
    invoke-direct {v11}, Landroid/os/Bundle;-><init>()V
    .line 649
    .local v11, "options":Landroid/os/Bundle;
    invoke-virtual {v11, v9, v10}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 650
    iget v9, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationTaskId:I
    invoke-virtual {v11, v8, v9}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 651
    iget-object v8, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mFinalCrop:Landroid/graphics/Rect;
    invoke-virtual {v11, v7, v8}, Landroid/os/Bundle;->putParcelable(Ljava/lang/String;Landroid/os/Parcelable;)V
    .line 652
    iget v7, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mRotation:I
    invoke-virtual {v11, v6, v7}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 653
    invoke-direct {p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->getZoomThresholdScale()F
    move-result v6
    invoke-virtual {v11, v5, v6}, Landroid/os/Bundle;->putFloat(Ljava/lang/String;F)V
    .line 654
    invoke-virtual {v11, v4, v2}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 655
    iget-boolean v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mIsFlexibleEnabled:Z
    invoke-virtual {v11, v3, v4}, Landroid/os/Bundle;->putBoolean(Ljava/lang/String;Z)V
    .line 656
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v5, "onAnimationEnd finishGestureAnimation:"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v3, v4}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 657
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    invoke-interface {v3, v11}, Landroid/view/IOplusGestureAnimationController;->finishGestureAnimation(Landroid/os/Bundle;)V
    .line 658
    iput-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    :try_end_15e
    .catch Ljava/lang/Exception; {:try_start_113 .. :try_end_15e} :catch_15f
    .line 663
    .end local v11    # "options":Landroid/os/Bundle;
    goto :goto_167
    .line 659
    :catch_15f
    move-exception v3
    .line 660
    .local v3, "e":Ljava/lang/Exception;
    invoke-virtual {v3}, Ljava/lang/Exception;->printStackTrace()V
    .line 661
    iput-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 662
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    .line 664
    .end local v3    # "e":Ljava/lang/Exception;
    :goto_167
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mController:Landroid/view/IOplusGestureAnimationController;
    .line 665
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mAnimationSurface:Landroid/view/SurfaceControl;
    goto :goto_1a3
    .line 669
    :cond_16c
    new-instance v2, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v2}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 670
    .local v2, "t":Landroid/view/SurfaceControl$Transaction;
    const/4 v3, 0x2
    new-array v3, v3, [F
    fill-array-data v3, :array_1ae
    invoke-static {v3}, Landroid/animation/ValueAnimator;->ofFloat([F)Landroid/animation/ValueAnimator;
    move-result-object v3
    iput-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    .line 671
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    new-instance v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$7;
    invoke-direct {v4, p0, v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$7;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl$Transaction;)V
    invoke-virtual {v3, v4}, Landroid/animation/ValueAnimator;->addUpdateListener(Landroid/animation/ValueAnimator$AnimatorUpdateListener;)V
    .line 686
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    int-to-long v4, v0
    invoke-virtual {v3, v4, v5}, Landroid/animation/ValueAnimator;->setDuration(J)Landroid/animation/ValueAnimator;
    .line 687
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    sget-object v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->EASE_OUT_CIRC:Landroid/view/animation/PathInterpolator;
    invoke-virtual {v3, v4}, Landroid/animation/ValueAnimator;->setInterpolator(Landroid/animation/TimeInterpolator;)V
    .line 688
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    new-instance v4, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;
    invoke-direct {v4, p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    invoke-virtual {v3, v4}, Landroid/animation/ValueAnimator;->addListener(Landroid/animation/Animator$AnimatorListener;)V
    .line 727
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mSpringBackAnim:Landroid/animation/ValueAnimator;
    invoke-virtual {v3}, Landroid/animation/ValueAnimator;->start()V
    .line 729
    .end local v0    # "animationDuration":I
    .end local v2    # "t":Landroid/view/SurfaceControl$Transaction;
    :cond_1a3
    :goto_1a3
    goto :goto_1ab
    .line 731
    :cond_1a4
    invoke-static {}, Lcom/android/server/wm/OplusZoomWindowManagerService;->getInstance()Lcom/android/server/wm/OplusZoomWindowManagerService;
    move-result-object v0
    invoke-virtual {v0}, Lcom/android/server/wm/OplusZoomWindowManagerService;->resumeDisplayRotation()V
    .line 733
    :goto_1ab
    iput-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mTopAppInfo:Lcom/oplus/app/OplusAppInfo;
    .line 734
    return-void
    :array_1ae
    .array-data 4
        0x0
        0x3f800000    # 1.0f
    .end array-data
.end method
```

## public startAnmation()V

Disassembly lines 4831–4965.

```smali
.method public startAnmation()V
    .registers 7
    .line 207
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v2, "startAnmation: isInAnimation="
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-boolean v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 208
    iget-boolean v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    if-nez v0, :cond_6f
    .line 210
    const/4 v0, 0x0
    const/4 v1, 0x1
    :try_start_21
    iput-boolean v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 211
    new-instance v2, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;
    invoke-direct {v2, p0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;-><init>(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    .line 282
    .local v2, "runner":Landroid/view/IOplusGestureAnimationRunner;
    new-instance v3, Landroid/os/Bundle;
    invoke-direct {v3}, Landroid/os/Bundle;-><init>()V
    .line 283
    .local v3, "options":Landroid/os/Bundle;
    const-string v4, "GestureMode"
    invoke-virtual {v3, v4, v1}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 284
    const-string v4, "BufferLayer"
    invoke-virtual {v3, v4, v1}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 285
    const-string v1, "LoadRes"
    const/4 v4, 0x2
    invoke-virtual {v3, v1, v4}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 286
    iput-boolean v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isHorizontalApp:Z
    .line 287
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v5, "startGestureAnmation:"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v1, v4}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 288
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->mOplusWm:Landroid/view/OplusWindowManager;
    invoke-virtual {v1, v2, v3}, Landroid/view/OplusWindowManager;->startGestureAnmation(Landroid/view/IOplusGestureAnimationRunner;Landroid/os/Bundle;)V
    .line 289
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->TAG:Ljava/lang/String;
    const-string/jumbo v4, "startAnmation: vibrate for drag full window"
    invoke-static {v1, v4}, Landroid/util/Slog;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 290
    invoke-direct {p0, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->vibrateWidthSpecilEffect(I)V
    :try_end_68
    .catch Ljava/lang/Exception; {:try_start_21 .. :try_end_68} :catch_69
    .line 294
    .end local v2    # "runner":Landroid/view/IOplusGestureAnimationRunner;
    .end local v3    # "options":Landroid/os/Bundle;
    goto :goto_6f
    .line 291
    :catch_69
    move-exception v1
    .line 292
    .local v1, "e":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V
    .line 293
    iput-boolean v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->isInAnimation:Z
    .line 296
    .end local v1    # "e":Ljava/lang/Exception;
    :cond_6f
    :goto_6f
    return-void
.end method
```
