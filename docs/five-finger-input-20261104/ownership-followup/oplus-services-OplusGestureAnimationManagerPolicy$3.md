# OplusGestureAnimationManagerPolicy$3 — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## public onAnimationCancel(Landroid/animation/Animator;)V

Local disassembly 44–79.

```smali
.method public onAnimationCancel(Landroid/animation/Animator;)V
    .registers 5
    .param p1, "animator"    # Landroid/animation/Animator;
    .line 476
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/4 v1, 0x0
    const/16 v2, 0x4e8a
    invoke-static {v0, v1, v2}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 477
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$mgetZoomThresholdScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v1
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 478
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-virtual {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->finishAnimation()V
    .line 479
    return-void
.end method
```

## public onAnimationEnd(Landroid/animation/Animator;)V

Local disassembly 81–116.

```smali
.method public onAnimationEnd(Landroid/animation/Animator;)V
    .registers 5
    .param p1, "animator"    # Landroid/animation/Animator;
    .line 483
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/4 v1, 0x0
    const/16 v2, 0x4e8a
    invoke-static {v0, v1, v2}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 484
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    iget-object v1, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$mgetZoomThresholdScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)F
    move-result v1
    invoke-static {v0, v1}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fputmScale(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;F)V
    .line 485
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-virtual {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->finishAnimation()V
    .line 486
    return-void
.end method
```

## public onAnimationStart(Landroid/animation/Animator;)V

Local disassembly 118–137.

```smali
.method public onAnimationStart(Landroid/animation/Animator;)V
    .registers 5
    .param p1, "animator"    # Landroid/animation/Animator;
    .line 490
    iget-object v0, p0, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy$3;->this$0:Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;
    invoke-static {v0}, Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;->-$$Nest$fgetmAnimationSurface(Lcom/android/server/oplus/input/exinputservice/globalgesture/OplusGestureAnimationManagerPolicy;)Landroid/view/SurfaceControl;
    move-result-object v0
    const/4 v1, 0x1
    const/16 v2, 0x4e8a
    invoke-static {v0, v1, v2}, Lcom/android/server/wm/FlexibleWindowUtils;->setFrameRateIfNeed(Landroid/view/SurfaceControl;ZI)V
    .line 491
    return-void
.end method
```
