# OplusGestureAnimationManagerPolicy$2 — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## public onAnimationCanceled()V

Disassembly lines 44–78.

```smali
.method public onAnimationCanceled()V
    .registers 4
    .line 277
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetTAG(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "onAnimationCanceled"
    invoke-static {v0, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 278
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/16 v1, 0x4e8a
    const/4 v2, 0x0
    invoke-static {v0, v2, v1}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 279
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0, v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 280
    return-void
.end method
```

## public onAnimationStart(Landroid/view/IOplusGestureAnimationController;[Landroid/view/RemoteAnimationTarget;[Landroid/view/SurfaceControl;)V

Disassembly lines 80–690.

```smali
.method public onAnimationStart(Landroid/view/IOplusGestureAnimationController;[Landroid/view/RemoteAnimationTarget;[Landroid/view/SurfaceControl;)V
    .registers 16
    .param p1, "controller"    # Landroid/view/IOplusGestureAnimationController;
    .param p2, "apps"    # [Landroid/view/RemoteAnimationTarget;
    .param p3, "dims"    # [Landroid/view/SurfaceControl;
    .line 215
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetTAG(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Ljava/lang/String;
    move-result-object v0
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v2, "startGestureAnmation callback apps size:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    array-length v2, p2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, " dims size:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    array-length v2, p3
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, ", mIsFlexibleEnabled:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmIsFlexibleEnabled(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Z
    move-result v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, ", mRatio:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmRatio(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(F)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, ", mLaunchBounds:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmLaunchBounds(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/graphics/Rect;
    move-result-object v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, ", mFlexibleThresholdScale:"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmFlexibleThresholdScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(F)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 218
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0, p1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmController(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/IOplusGestureAnimationController;)V
    .line 219
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmController(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/IOplusGestureAnimationController;
    move-result-object v0
    if-eqz v0, :cond_90
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Z
    move-result v0
    if-nez v0, :cond_90
    .line 220
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetTAG(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "onAnimationStart: gesture had up, so cancel"
    invoke-static {v0, v1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 221
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$mresetGestureAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)V
    .line 222
    return-void
    .line 224
    :cond_90
    array-length v0, p2
    const/4 v1, 0x0
    const/4 v2, 0x1
    if-le v0, v2, :cond_20e
    array-length v0, p3
    if-nez v0, :cond_9a
    goto/16 :goto_20e
    .line 229
    :cond_9a
    array-length v0, p2
    if-le v0, v2, :cond_12f
    .line 230
    aget-object v0, p2, v2
    .line 231
    .local v0, "target":Landroid/view/RemoteAnimationTarget;
    if-nez v0, :cond_a7
    .line 232
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 233
    return-void
    .line 235
    :cond_a7
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmIsFlexibleEnabled(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Z
    move-result v3
    if-nez v3, :cond_ce
    .line 236
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    const v4, 0x3fe38e39
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmRatio(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 237
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmLaunchBounds(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/graphics/Rect;
    move-result-object v3
    invoke-virtual {v3}, Landroid/graphics/Rect;->setEmpty()V
    .line 238
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    const/16 v4, 0x16
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmCornerRadius(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;I)V
    .line 239
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    const/16 v4, 0x168
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmLaunchAppSmallestSide(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;I)V
    .line 244
    :cond_ce
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->leash:Landroid/view/SurfaceControl;
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl;)V
    .line 245
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget v4, v0, Landroid/view/RemoteAnimationTarget;->taskId:I
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmAnimationTaskId(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;I)V
    .line 246
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->localBounds:Landroid/graphics/Rect;
    invoke-virtual {v4}, Landroid/graphics/Rect;->width()I
    move-result v4
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmInitialWidth(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;I)V
    .line 247
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->localBounds:Landroid/graphics/Rect;
    invoke-virtual {v4}, Landroid/graphics/Rect;->height()I
    move-result v4
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmInitialHeight(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;I)V
    .line 248
    aget-object v3, p2, v2
    iget-object v3, v3, Landroid/view/RemoteAnimationTarget;->startBounds:Landroid/graphics/Rect;
    if-eqz v3, :cond_10f
    aget-object v3, p2, v2
    iget-object v3, v3, Landroid/view/RemoteAnimationTarget;->startBounds:Landroid/graphics/Rect;
    invoke-virtual {v3}, Landroid/graphics/Rect;->width()I
    move-result v3
    aget-object v4, p2, v2
    iget-object v4, v4, Landroid/view/RemoteAnimationTarget;->startBounds:Landroid/graphics/Rect;
    invoke-virtual {v4}, Landroid/graphics/Rect;->height()I
    move-result v4
    if-le v3, v4, :cond_10f
    .line 249
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3, v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisHorizontalApp(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 251
    :cond_10f
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->taskInfo:Landroid/app/ActivityManager$RunningTaskInfo;
    if-eqz v4, :cond_12b
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->taskInfo:Landroid/app/ActivityManager$RunningTaskInfo;
    iget-object v4, v4, Landroid/app/ActivityManager$RunningTaskInfo;->baseActivity:Landroid/content/ComponentName;
    if-eqz v4, :cond_12b
    iget-object v4, v0, Landroid/view/RemoteAnimationTarget;->taskInfo:Landroid/app/ActivityManager$RunningTaskInfo;
    iget-object v4, v4, Landroid/app/ActivityManager$RunningTaskInfo;->baseActivity:Landroid/content/ComponentName;
    .line 252
    invoke-virtual {v4}, Landroid/content/ComponentName;->getPackageName()Ljava/lang/String;
    move-result-object v4
    invoke-static {v4}, Lcom/android/server/wm/FlexibleWindowUtils;->isSupportFullScreenRatioInFlexibleTask(Ljava/lang/String;)Z
    move-result v4
    if-eqz v4, :cond_12b
    move v4, v2
    goto :goto_12c
    :cond_12b
    move v4, v1
    :goto_12c
    invoke-static {v3, v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmSupportFullScreenRatio(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 254
    .end local v0    # "target":Landroid/view/RemoteAnimationTarget;
    :cond_12f
    array-length v0, p3
    if-le v0, v2, :cond_13a
    .line 255
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    aget-object v1, p3, v2
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmDimSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl;)V
    goto :goto_141
    .line 257
    :cond_13a
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    aget-object v1, p3, v1
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmDimSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl;)V
    .line 260
    :goto_141
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetisHorizontalApp(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Z
    move-result v1
    if-eqz v1, :cond_159
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialHeight(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v1
    int-to-float v1, v1
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialWidth(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v3
    goto :goto_166
    :cond_159
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialWidth(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v1
    int-to-float v1, v1
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialHeight(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v3
    :goto_166
    int-to-float v3, v3
    div-float/2addr v1, v3
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmStartProportion(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 261
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmStartProportion(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v1
    const v3, 0x3f19a027    # 0.6001f
    sub-float/2addr v1, v3
    const v4, 0x38d1b717    # 1.0E-4f
    cmpl-float v1, v1, v4
    const/4 v4, 0x0
    if-lez v1, :cond_187
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmStartProportion(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v1
    sub-float/2addr v1, v3
    goto :goto_188
    :cond_187
    move v1, v4
    :goto_188
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmDifferenceProportion(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 262
    new-instance v0, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v0}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 263
    .local v0, "t":Landroid/view/SurfaceControl$Transaction;
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    const/high16 v3, 0x3f800000    # 1.0f
    invoke-static {v1, v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 264
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v1
    const/16 v3, 0x4e8a
    invoke-static {v1, v2, v3}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 265
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmContext(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/content/Context;
    move-result-object v2
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmCornerRadius(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v3
    int-to-float v3, v3
    invoke-static {v2, v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/Utils;->dip2px(Landroid/content/Context;F)I
    move-result v2
    int-to-float v2, v2
    invoke-virtual {v0, v1, v2}, Landroid/view/SurfaceControl$Transaction;->setCornerRadius(Landroid/view/SurfaceControl;F)Landroid/view/SurfaceControl$Transaction;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v2
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialWidth(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v3
    iget-object v5, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v5}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmInitialHeight(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v5
    .line 266
    invoke-virtual {v1, v2, v3, v5}, Landroid/view/SurfaceControl$Transaction;->setWindowCrop(Landroid/view/SurfaceControl;II)Landroid/view/SurfaceControl$Transaction;
    move-result-object v6
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v7
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v8
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v11
    .line 267
    const/4 v9, 0x0
    const/4 v10, 0x0
    invoke-virtual/range {v6 .. v11}, Landroid/view/SurfaceControl$Transaction;->setMatrix(Landroid/view/SurfaceControl;FFFF)Landroid/view/SurfaceControl$Transaction;
    .line 268
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmDimSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v1
    invoke-virtual {v1}, Landroid/view/SurfaceControl;->isValid()Z
    move-result v1
    if-eqz v1, :cond_20a
    .line 269
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmDimSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v1
    invoke-virtual {v0, v1, v4}, Landroid/view/SurfaceControl$Transaction;->setAlpha(Landroid/view/SurfaceControl;F)Landroid/view/SurfaceControl$Transaction;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmDimSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v2
    .line 270
    invoke-virtual {v1, v2}, Landroid/view/SurfaceControl$Transaction;->show(Landroid/view/SurfaceControl;)Landroid/view/SurfaceControl$Transaction;
    .line 272
    :cond_20a
    invoke-virtual {v0}, Landroid/view/SurfaceControl$Transaction;->apply()V
    .line 273
    return-void
    .line 225
    .end local v0    # "t":Landroid/view/SurfaceControl$Transaction;
    :cond_20e
    :goto_20e
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetTAG(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v2, "onAnimationStart: not to start zoom by gesture because remoteTarget exception"
    invoke-static {v0, v2}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 226
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$2;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 227
    return-void
.end method
```
