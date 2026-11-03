# OplusZoomWindowManagerService — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## public checkAnimationReady()V

Local disassembly 5493–5509.

```smali
.method public checkAnimationReady()V
    .registers 2
    .line 2112
    iget-object v0, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    if-eqz v0, :cond_9
    .line 2113
    iget-object v0, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-virtual {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->checkAnimationReady()V
    .line 2115
    :cond_9
    return-void
.end method
```

## public cleanupGestureAnimation()V

Local disassembly 5602–5638.

```smali
.method public cleanupGestureAnimation()V
    .registers 3
    .line 2119
    iget-object v0, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    if-eqz v0, :cond_18
    .line 2120
    const-string v0, "OplusZoomWindowManagerService"
    const-string v1, "cleanupGestureAnimation"
    invoke-static {v0, v1}, Landroid/util/Slog;->i(Ljava/lang/String;Ljava/lang/String;)I
    .line 2121
    iget-object v0, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    .line 2122
    .local v0, "controller":Lcom/android/server/wm/OplusGestureAnimationController;
    const/4 v1, 0x0
    iput-object v1, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    .line 2123
    invoke-virtual {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->cleanupAnimation()V
    .line 2124
    iget-object v1, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mSurfaceAnimatorPositionListBeforeDragSlpitTask:Ljava/util/HashMap;
    invoke-virtual {v1}, Ljava/util/HashMap;->clear()V
    .line 2127
    .end local v0    # "controller":Lcom/android/server/wm/OplusGestureAnimationController;
    :cond_18
    return-void
.end method
```

## public hasGestureAnimationController()Z

Local disassembly 8490–8527.

```smali
.method public hasGestureAnimationController()Z
    .registers 2
    .line 2067
    iget-object v0, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mGestureAnimationController:Lcom/android/server/wm/OplusGestureAnimationController;
    if-nez v0, :cond_15
    sget-object v0, Lcom/android/server/wm/IOplusSplitScreenManager;->DEFAULT:Lcom/android/server/wm/IOplusSplitScreenManager;
    .line 2068
    invoke-static {v0}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IOplusSplitScreenManager;
    invoke-interface {v0}, Lcom/android/server/wm/IOplusSplitScreenManager;->isTaskInMaintainState()Z
    move-result v0
    if-eqz v0, :cond_13
    goto :goto_15
    :cond_13
    const/4 v0, 0x0
    goto :goto_16
    :cond_15
    :goto_15
    const/4 v0, 0x1
    .line 2067
    :goto_16
    return v0
.end method
```

## public startGestureAnmation(Landroid/view/IOplusGestureAnimationRunner;Landroid/os/Bundle;)V

Local disassembly 12975–13037.

```smali
.method public startGestureAnmation(Landroid/view/IOplusGestureAnimationRunner;Landroid/os/Bundle;)V
    .registers 6
    .param p1, "guestureAnimationRunner"    # Landroid/view/IOplusGestureAnimationRunner;
    .param p2, "bOptions"    # Landroid/os/Bundle;
    .line 2047
    const-string v0, "OplusZoomWindowManagerService"
    invoke-virtual {p0}, Lcom/android/server/wm/OplusZoomWindowManagerService;->hasGestureAnimationController()Z
    move-result v1
    if-nez v1, :cond_17
    .line 2048
    new-instance v0, Lcom/android/server/wm/OplusGestureAnimation;
    iget-object v1, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mWms:Lcom/android/server/wm/WindowManagerService;
    iget-object v1, v1, Lcom/android/server/wm/WindowManagerService;->mAtmService:Lcom/android/server/wm/ActivityTaskManagerService;
    iget-object v2, p0, Lcom/android/server/wm/OplusZoomWindowManagerService;->mWms:Lcom/android/server/wm/WindowManagerService;
    invoke-direct {v0, v1, v2}, Lcom/android/server/wm/OplusGestureAnimation;-><init>(Lcom/android/server/wm/ActivityTaskManagerService;Lcom/android/server/wm/WindowManagerService;)V
    .line 2049
    .local v0, "anim":Lcom/android/server/wm/OplusGestureAnimation;
    invoke-virtual {v0, p1, p2}, Lcom/android/server/wm/OplusGestureAnimation;->startGestureAnmation(Landroid/view/IOplusGestureAnimationRunner;Landroid/os/Bundle;)V
    .line 2050
    .end local v0    # "anim":Lcom/android/server/wm/OplusGestureAnimation;
    goto :goto_27
    .line 2052
    :cond_17
    :try_start_17
    const-string/jumbo v1, "implement a gestureAnmation now, cancle the next one"
    invoke-static {v0, v1}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 2053
    invoke-interface {p1}, Landroid/view/IOplusGestureAnimationRunner;->onAnimationCanceled()V
    :try_end_20
    .catch Landroid/os/RemoteException; {:try_start_17 .. :try_end_20} :catch_21
    .line 2056
    goto :goto_27
    .line 2054
    :catch_21
    move-exception v1
    .line 2055
    .local v1, "e":Landroid/os/RemoteException;
    const-string v2, "Failed to cancel gesture animation"
    invoke-static {v0, v2, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    .line 2058
    .end local v1    # "e":Landroid/os/RemoteException;
    :goto_27
    return-void
.end method
```
