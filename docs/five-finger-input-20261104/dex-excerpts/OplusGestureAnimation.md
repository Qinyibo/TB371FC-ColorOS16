# OplusGestureAnimation — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## public onAnimationFinished()V

Disassembly lines 1712–2030.

```smali
.method public onAnimationFinished()V
    .registers 8
    .line 75
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    iget-object v0, v0, Lcom/android/server/wm/ActivityTaskManagerService;->mGlobalLock:Lcom/android/server/wm/WindowManagerGlobalLock;
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->boostPriorityForLockedSection()V
    monitor-enter v0
    .line 76
    :try_start_8
    sget-object v1, Lcom/android/server/wm/IOplusZoomWindowManager;->DEFAULT:Lcom/android/server/wm/IOplusZoomWindowManager;
    invoke-static {v1}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v1
    check-cast v1, Lcom/android/server/wm/IOplusZoomWindowManager;
    invoke-interface {v1}, Lcom/android/server/wm/IOplusZoomWindowManager;->hasGestureAnimationController()Z
    move-result v1
    if-nez v1, :cond_1b
    .line 77
    monitor-exit v0
    :try_end_17
    .catchall {:try_start_8 .. :try_end_17} :catchall_f5
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    return-void
    .line 80
    :cond_1b
    :try_start_1b
    iget-object v1, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    invoke-virtual {v1}, Lcom/android/server/wm/ActivityTaskManagerService;->deferWindowLayout()V
    :try_end_20
    .catchall {:try_start_1b .. :try_end_20} :catchall_f5
    .line 82
    const/4 v1, 0x0
    const/4 v2, 0x0
    :try_start_22
    sget-object v3, Lcom/android/server/wm/IOplusZoomWindowManager;->DEFAULT:Lcom/android/server/wm/IOplusZoomWindowManager;
    invoke-static {v3}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v3
    check-cast v3, Lcom/android/server/wm/IOplusZoomWindowManager;
    invoke-interface {v3}, Lcom/android/server/wm/IOplusZoomWindowManager;->cleanupGestureAnimation()V
    .line 83
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mLaunchedTargetActivity:Lcom/android/server/wm/ActivityRecord;
    if-eqz v3, :cond_4f
    .line 84
    sget-object v3, Lcom/android/server/wm/OplusGestureAnimation;->TAG:Ljava/lang/String;
    new-instance v4, Ljava/lang/StringBuilder;
    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimation;->mLaunchedTargetActivity:Lcom/android/server/wm/ActivityRecord;
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v4
    const-string v5, " mLaunchTaskBehind false"
    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-static {v3, v4}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 85
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mLaunchedTargetActivity:Lcom/android/server/wm/ActivityRecord;
    iput-boolean v2, v3, Lcom/android/server/wm/ActivityRecord;->mLaunchTaskBehind:Z
    .line 87
    :cond_4f
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mCurrentTask:Lcom/android/server/wm/Task;
    if-eqz v3, :cond_83
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mCurrentTask:Lcom/android/server/wm/Task;
    invoke-virtual {v3}, Lcom/android/server/wm/Task;->getParent()Lcom/android/server/wm/WindowContainer;
    move-result-object v3
    if-eqz v3, :cond_83
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mCurrentTask:Lcom/android/server/wm/Task;
    invoke-virtual {v3}, Lcom/android/server/wm/Task;->isOnTop()Z
    move-result v3
    if-nez v3, :cond_83
    .line 88
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mCurrentTask:Lcom/android/server/wm/Task;
    invoke-virtual {v3}, Lcom/android/server/wm/Task;->getParent()Lcom/android/server/wm/WindowContainer;
    move-result-object v3
    invoke-virtual {v3}, Lcom/android/server/wm/WindowContainer;->asTaskDisplayArea()Lcom/android/server/wm/TaskDisplayArea;
    move-result-object v3
    .line 89
    .local v3, "displayArea":Lcom/android/server/wm/TaskDisplayArea;
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimation;->mDefaultTaskDisplayArea:Lcom/android/server/wm/TaskDisplayArea;
    if-ne v4, v3, :cond_83
    .line 90
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimation;->mDefaultTaskDisplayArea:Lcom/android/server/wm/TaskDisplayArea;
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimation;->mCurrentTask:Lcom/android/server/wm/Task;
    const v6, 0x7fffffff
    invoke-virtual {v4, v6, v5, v2}, Lcom/android/server/wm/TaskDisplayArea;->positionChildAt(ILcom/android/server/wm/WindowContainer;Z)V
    .line 91
    sget-object v4, Lcom/android/server/wm/OplusGestureAnimation;->TAG:Ljava/lang/String;
    const-string/jumbo v5, "move flexible task to top"
    invoke-static {v4, v5}, Landroid/util/Slog;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 94
    .end local v3    # "displayArea":Lcom/android/server/wm/TaskDisplayArea;
    :cond_83
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    iget-object v3, v3, Lcom/android/server/wm/ActivityTaskManagerService;->mRootWindowContainer:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v3}, Lcom/android/server/wm/RootWindowContainer;->ensureActivitiesVisible()V
    .line 95
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    iget-object v3, v3, Lcom/android/server/wm/ActivityTaskManagerService;->mRootWindowContainer:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v3}, Lcom/android/server/wm/RootWindowContainer;->resumeFocusedTasksTopActivities()Z
    :try_end_91
    .catch Ljava/lang/Exception; {:try_start_22 .. :try_end_91} :catch_c1
    .catchall {:try_start_22 .. :try_end_91} :catchall_bf
    .line 100
    :try_start_91
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    invoke-virtual {v3}, Lcom/android/server/wm/ActivityTaskManagerService;->continueWindowLayout()V
    .line 101
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mWindowManager:Lcom/android/server/wm/WindowManagerService;
    iget-object v3, v3, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v3}, Lcom/android/server/wm/RootWindowContainer;->isLayoutNeeded()Z
    move-result v3
    if-eqz v3, :cond_a7
    .line 102
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimation;->mWindowManager:Lcom/android/server/wm/WindowManagerService;
    iget-object v3, v3, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v3}, Lcom/android/server/wm/RootWindowContainer;->performSurfacePlacement()V
    .line 104
    :cond_a7
    sget-object v3, Lcom/android/server/wm/IOplusSplitScreenManager;->DEFAULT:Lcom/android/server/wm/IOplusSplitScreenManager;
    invoke-static {v3}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v3
    check-cast v3, Lcom/android/server/wm/IOplusSplitScreenManager;
    invoke-interface {v3, v2}, Lcom/android/server/wm/IOplusSplitScreenManager;->matainSplitState(Z)V
    .line 105
    invoke-static {v1}, Lcom/android/server/wm/FlexibleWindowManagerService;->getInstance(Ljava/lang/Object;)Lcom/android/server/wm/FlexibleWindowManagerService;
    move-result-object v1
    invoke-virtual {v1, v2}, Lcom/android/server/wm/FlexibleWindowManagerService;->setTaskBarHide(Z)V
    .line 106
    nop
    .line 107
    monitor-exit v0
    :try_end_bb
    .catchall {:try_start_91 .. :try_end_bb} :catchall_f5
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    .line 108
    return-void
    .line 100
    :catchall_bf
    move-exception v3
    goto :goto_cb
    .line 96
    :catch_c1
    move-exception v3
    .line 97
    .local v3, "e":Ljava/lang/Exception;
    :try_start_c2
    sget-object v4, Lcom/android/server/wm/OplusGestureAnimation;->TAG:Ljava/lang/String;
    const-string v5, "Failed to clean up recents activity"
    invoke-static {v4, v5, v3}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    .line 98
    nop
    .end local p0    # "this":Lcom/android/server/wm/OplusGestureAnimation;
    throw v3
    :try_end_cb
    .catchall {:try_start_c2 .. :try_end_cb} :catchall_bf
    .line 100
    .end local v3    # "e":Ljava/lang/Exception;
    .restart local p0    # "this":Lcom/android/server/wm/OplusGestureAnimation;
    :goto_cb
    :try_start_cb
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimation;->mService:Lcom/android/server/wm/ActivityTaskManagerService;
    invoke-virtual {v4}, Lcom/android/server/wm/ActivityTaskManagerService;->continueWindowLayout()V
    .line 101
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimation;->mWindowManager:Lcom/android/server/wm/WindowManagerService;
    iget-object v4, v4, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v4}, Lcom/android/server/wm/RootWindowContainer;->isLayoutNeeded()Z
    move-result v4
    if-eqz v4, :cond_e1
    .line 102
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimation;->mWindowManager:Lcom/android/server/wm/WindowManagerService;
    iget-object v4, v4, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v4}, Lcom/android/server/wm/RootWindowContainer;->performSurfacePlacement()V
    .line 104
    :cond_e1
    sget-object v4, Lcom/android/server/wm/IOplusSplitScreenManager;->DEFAULT:Lcom/android/server/wm/IOplusSplitScreenManager;
    invoke-static {v4}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v4
    check-cast v4, Lcom/android/server/wm/IOplusSplitScreenManager;
    invoke-interface {v4, v2}, Lcom/android/server/wm/IOplusSplitScreenManager;->matainSplitState(Z)V
    .line 105
    invoke-static {v1}, Lcom/android/server/wm/FlexibleWindowManagerService;->getInstance(Ljava/lang/Object;)Lcom/android/server/wm/FlexibleWindowManagerService;
    move-result-object v1
    invoke-virtual {v1, v2}, Lcom/android/server/wm/FlexibleWindowManagerService;->setTaskBarHide(Z)V
    .line 106
    nop
    .end local p0    # "this":Lcom/android/server/wm/OplusGestureAnimation;
    throw v3
    .line 107
    .restart local p0    # "this":Lcom/android/server/wm/OplusGestureAnimation;
    :catchall_f5
    move-exception v1
    monitor-exit v0
    :try_end_f7
    .catchall {:try_start_cb .. :try_end_f7} :catchall_f5
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    throw v1
.end method
```
