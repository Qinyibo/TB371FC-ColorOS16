# OplusGestureAnimationManagerPolicy$8 — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## public onAnimationCancel(Landroid/animation/Animator;)V

Disassembly lines 44–63.

```smali
.method public onAnimationCancel(Landroid/animation/Animator;)V
    .registers 5
    .param p1, "animation"    # Landroid/animation/Animator;
    .line 724
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/4 v1, 0x0
    const/16 v2, 0x4e8a
    invoke-static {v0, v1, v2}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 725
    return-void
.end method
```

## public onAnimationEnd(Landroid/animation/Animator;)V

Disassembly lines 65–258.

```smali
.method public onAnimationEnd(Landroid/animation/Animator;)V
    .registers 8
    .param p1, "animation"    # Landroid/animation/Animator;
    .line 696
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/16 v1, 0x4e8a
    const/4 v2, 0x0
    invoke-static {v0, v2, v1}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 697
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmController(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/IOplusGestureAnimationController;
    move-result-object v0
    if-eqz v0, :cond_ac
    .line 700
    const/4 v0, 0x0
    :try_start_15
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmFinalCrop(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/graphics/Rect;
    move-result-object v3
    invoke-static {v1, v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$mupdateRealCropRect(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/graphics/Rect;)V
    .line 701
    new-instance v1, Landroid/os/Bundle;
    invoke-direct {v1}, Landroid/os/Bundle;-><init>()V
    .line 702
    .local v1, "options":Landroid/os/Bundle;
    const-string v3, "GestureMode"
    const/4 v4, 0x1
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 703
    const-string v3, "TaskId"
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationTaskId(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v4
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 704
    const-string v3, "Bound"
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmFinalCrop(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/graphics/Rect;
    move-result-object v4
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putParcelable(Ljava/lang/String;Landroid/os/Parcelable;)V
    .line 705
    const-string v3, "Rotation"
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmRotation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)I
    move-result v4
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 706
    const-string v3, "Scale"
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$mgetZoomThresholdScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v4
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putFloat(Ljava/lang/String;F)V
    .line 707
    const-string v3, "Change"
    invoke-virtual {v1, v3, v2}, Landroid/os/Bundle;->putInt(Ljava/lang/String;I)V
    .line 708
    const-string/jumbo v3, "flexibleActived"
    iget-object v4, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v4}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmIsFlexibleEnabled(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Z
    move-result v4
    invoke-virtual {v1, v3, v4}, Landroid/os/Bundle;->putBoolean(Ljava/lang/String;Z)V
    .line 709
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetTAG(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Ljava/lang/String;
    move-result-object v3
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v5, "onAnimationEnd finishGestureAnimation:"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v3, v4}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 710
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmController(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/IOplusGestureAnimationController;
    move-result-object v3
    invoke-interface {v3, v1}, Landroid/view/IOplusGestureAnimationController;->finishGestureAnimation(Landroid/os/Bundle;)V
    .line 711
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3, v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    :try_end_93
    .catch Ljava/lang/Exception; {:try_start_15 .. :try_end_93} :catch_94
    .line 716
    .end local v1    # "options":Landroid/os/Bundle;
    goto :goto_a2
    .line 712
    :catch_94
    move-exception v1
    .line 713
    .local v1, "e":Ljava/lang/Exception;
    invoke-virtual {v1}, Ljava/lang/Exception;->printStackTrace()V
    .line 714
    iget-object v3, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v3, v2}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputisInAnimation(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Z)V
    .line 715
    iget-object v2, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v2, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl;)V
    .line 717
    .end local v1    # "e":Ljava/lang/Exception;
    :goto_a2
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmController(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/IOplusGestureAnimationController;)V
    .line 718
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$8;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1, v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;Landroid/view/SurfaceControl;)V
    .line 720
    :cond_ac
    return-void
.end method
```
