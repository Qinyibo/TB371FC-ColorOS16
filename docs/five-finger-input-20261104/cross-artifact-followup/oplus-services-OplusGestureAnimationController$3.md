# OplusGestureAnimationController$3 — selected methods

Artifact `oplus-services`, SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`. Selected complete bodies, empty lines removed; no opcode/label/register/handler changes. Ranges are local disassembly lines. Not a patch.

## public onAnimationCancel(Landroid/animation/Animator;)V

Local lines 44–76.

```smali
.method public onAnimationCancel(Landroid/animation/Animator;)V
    .registers 4
    .param p1, "animation"    # Landroid/animation/Animator;
    .line 1596
    invoke-static {}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$sfgetTAG()Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "performFinishAnimation onAnimationCancel.."
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 1597
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mcleanUpOnAnimationEnd(Lcom/android/server/wm/OplusGestureAnimationController;)V
    .line 1598
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mclearFlexibleTaskMark(Lcom/android/server/wm/OplusGestureAnimationController;)V
    .line 1599
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    const/4 v1, 0x1
    invoke-static {v0, v1}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fputmCanceled(Lcom/android/server/wm/OplusGestureAnimationController;Z)V
    .line 1600
    return-void
.end method
```

## public onAnimationEnd(Landroid/animation/Animator;)V

Local lines 78–110.

```smali
.method public onAnimationEnd(Landroid/animation/Animator;)V
    .registers 4
    .param p1, "animation"    # Landroid/animation/Animator;
    .line 1589
    invoke-static {}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$sfgetTAG()Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "performFinishAnimation onAnimationEnd.."
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 1590
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mremoveDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)V
    .line 1591
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mclearFlexibleTaskMark(Lcom/android/server/wm/OplusGestureAnimationController;)V
    .line 1592
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    const/4 v1, 0x1
    invoke-static {v0, v1}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fputmCanceled(Lcom/android/server/wm/OplusGestureAnimationController;Z)V
    .line 1593
    return-void
.end method
```

## public onAnimationStart(Landroid/animation/Animator;)V

Local lines 112–164.

```smali
.method public onAnimationStart(Landroid/animation/Animator;)V
    .registers 4
    .param p1, "animation"    # Landroid/animation/Animator;
    .line 1580
    invoke-static {}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$sfgetTAG()Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "performFinishAnimation onAnimationStart.."
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 1581
    const/4 v0, 0x0
    invoke-static {v0}, Lcom/android/server/wm/FlexibleWindowManagerService;->getInstance(Ljava/lang/Object;)Lcom/android/server/wm/FlexibleWindowManagerService;
    move-result-object v0
    .line 1582
    invoke-virtual {v0}, Lcom/android/server/wm/FlexibleWindowManagerService;->getFlexibleTaskController()Lcom/android/server/wm/FlexibleTaskController;
    move-result-object v0
    invoke-virtual {v0}, Lcom/android/server/wm/FlexibleTaskController;->getInOrientationChanging()Z
    move-result v0
    if-eqz v0, :cond_2c
    .line 1583
    invoke-static {}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$sfgetTAG()Ljava/lang/String;
    move-result-object v0
    const-string/jumbo v1, "performFinishAnimation orientation changing need cancel"
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 1584
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$3;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmFinishAnim(Lcom/android/server/wm/OplusGestureAnimationController;)Landroid/animation/ValueAnimator;
    move-result-object v0
    invoke-virtual {v0}, Landroid/animation/ValueAnimator;->cancel()V
    .line 1586
    :cond_2c
    return-void
.end method
```
