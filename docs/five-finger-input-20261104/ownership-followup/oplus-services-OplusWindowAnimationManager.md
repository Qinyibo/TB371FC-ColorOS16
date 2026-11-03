# OplusWindowAnimationManager — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## constructor <init>()V

Local disassembly 627–765.

```smali
.method constructor <init>()V
    .registers 4
    .line 283
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    .line 202
    invoke-static {}, Lcom/google/android/collect/Sets;->newHashSet()Ljava/util/HashSet;
    move-result-object v0
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mNoAnimTasks:Ljava/util/Set;
    .line 203
    invoke-static {}, Lcom/google/android/collect/Sets;->newHashSet()Ljava/util/HashSet;
    move-result-object v0
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mDefferedAnimatingActivities:Ljava/util/Set;
    .line 204
    const-string v0, "com.oplus.upgradeguide"
    invoke-static {v0}, Ljava/util/List;->of(Ljava/lang/Object;)Ljava/util/List;
    move-result-object v0
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mSkipLargeScreenTaskSwitch:Ljava/util/List;
    .line 207
    const/4 v0, 0x0
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mUseDarkModeLoading:Z
    .line 208
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mFromUiModeChange:Z
    .line 209
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mIsWallpaperVisible:Z
    .line 210
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mExpandFPDimLayerSurface:Z
    .line 211
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mScreenFreezeTimeOut:Z
    .line 212
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mSuperPowerEnable:Z
    .line 213
    iput v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mWindowCornerRadius:I
    .line 214
    iput v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mCurrentScreenRotationDelta:I
    .line 215
    iput v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mBaseWindowCornerRadiusForPrimary:I
    .line 216
    iput v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mBaseWindowCornerRadiusForSecond:I
    .line 217
    const/4 v1, -0x1
    iput v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mLastSensorRotation:I
    .line 218
    iput v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mCurrentWindowCornerRadiusModeId:I
    .line 223
    new-instance v2, Ljava/util/ArrayList;
    invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V
    iput-object v2, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mOpeningTasks:Ljava/util/ArrayList;
    .line 225
    const-class v2, Landroid/os/ITheiaManagerExt;
    invoke-static {v2}, Lsystem/ext/loader/core/ExtLoader;->type(Ljava/lang/Class;)Lsystem/ext/loader/core/ExtLoader$ExtBuilder;
    move-result-object v2
    invoke-virtual {v2}, Lsystem/ext/loader/core/ExtLoader$ExtBuilder;->create()Ljava/lang/Object;
    move-result-object v2
    check-cast v2, Landroid/os/ITheiaManagerExt;
    iput-object v2, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mTheiaManagerExt:Landroid/os/ITheiaManagerExt;
    .line 232
    const/4 v2, 0x1
    iput-boolean v2, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mInputConsumerEnabled:Z
    .line 233
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mLastInputConsumerEnabled:Z
    .line 238
    iput v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->startingWindowUxTid:I
    .line 239
    iput v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->startingWindowUxPid:I
    .line 248
    new-instance v1, Lcom/android/server/wm/OplusWindowAnimationManager$1;
    invoke-direct {v1, p0}, Lcom/android/server/wm/OplusWindowAnimationManager$1;-><init>(Lcom/android/server/wm/OplusWindowAnimationManager;)V
    iput-object v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mScreenFreezeTimeOutRunable:Ljava/lang/Runnable;
    .line 272
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mHasMarkRoundedCornersAnimationUIFirst:Z
    .line 273
    new-instance v0, Lcom/android/server/wm/OplusWindowAnimationManager$2;
    invoke-direct {v0, p0}, Lcom/android/server/wm/OplusWindowAnimationManager$2;-><init>(Lcom/android/server/wm/OplusWindowAnimationManager;)V
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mMarkAnimationUIFirstTimeOut:Ljava/lang/Runnable;
    .line 316
    new-instance v0, Lcom/android/server/wm/OplusWindowAnimationManager$3;
    invoke-direct {v0, p0}, Lcom/android/server/wm/OplusWindowAnimationManager$3;-><init>(Lcom/android/server/wm/OplusWindowAnimationManager;)V
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mResetKeyguadExitAnimRunnable:Ljava/lang/Runnable;
    .line 1901
    new-instance v0, Lcom/android/server/wm/OplusWindowAnimationManager$7;
    invoke-direct {v0, p0}, Lcom/android/server/wm/OplusWindowAnimationManager$7;-><init>(Lcom/android/server/wm/OplusWindowAnimationManager;)V
    iput-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mSecurityPageFlagChangedRunnable:Ljava/lang/Runnable;
    .line 284
    return-void
.end method
```

## public getInputConsumerEnabled()Z

Local disassembly 7029–7036.

```smali
.method public getInputConsumerEnabled()Z
    .registers 2
    .line 2736
    iget-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mInputConsumerEnabled:Z
    return v0
.end method
```

## public setInputConsumerEnabled(Z)Z

Local disassembly 10943–11108.

```smali
.method public setInputConsumerEnabled(Z)Z
    .registers 7
    .param p1, "enabled"    # Z
    .line 2703
    iget-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mInputConsumerEnabled:Z
    iput-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mLastInputConsumerEnabled:Z
    .line 2704
    iput-boolean p1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mInputConsumerEnabled:Z
    .line 2705
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v1, "setInputConsumerEnabled from launcher enabled="
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, " last="
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    iget-boolean v1, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mLastInputConsumerEnabled:Z
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    invoke-static {v0}, Lcom/android/server/wm/OplusWindowAnimationManager;->logD(Ljava/lang/String;)V
    .line 2708
    iget-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mLastInputConsumerEnabled:Z
    const/4 v1, 0x1
    const/4 v2, 0x0
    if-eqz v0, :cond_56
    iget-boolean v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mInputConsumerEnabled:Z
    if-nez v0, :cond_56
    .line 2709
    sget-object v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->DEFAULT:Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    new-array v3, v2, [Ljava/lang/Object;
    invoke-static {v0, v3}, Landroid/common/OplusFeatureCache;->getOrCreate(Landroid/common/IOplusCommonFeature;[Ljava/lang/Object;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    .line 2710
    invoke-interface {v0}, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->getQuickStartController()Lcom/android/server/wm/IQuickStartController;
    move-result-object v0
    .line 2711
    invoke-interface {v0}, Lcom/android/server/wm/IQuickStartController;->rescheduleTimeoutIfNeeded()V
    .line 2713
    sget-object v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->DEFAULT:Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    new-array v2, v2, [Ljava/lang/Object;
    invoke-static {v0, v2}, Landroid/common/OplusFeatureCache;->getOrCreate(Landroid/common/IOplusCommonFeature;[Ljava/lang/Object;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    .line 2714
    invoke-interface {v0}, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->getContinuousTransitionController()Lcom/android/server/wm/IContinuousTransitionController;
    move-result-object v0
    .line 2715
    invoke-interface {v0, v1}, Lcom/android/server/wm/IContinuousTransitionController;->setPredictiveReadyInRecentsContinuous(Z)V
    goto :goto_67
    .line 2717
    :cond_56
    sget-object v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->DEFAULT:Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    new-array v3, v2, [Ljava/lang/Object;
    invoke-static {v0, v3}, Landroid/common/OplusFeatureCache;->getOrCreate(Landroid/common/IOplusCommonFeature;[Ljava/lang/Object;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;
    .line 2718
    invoke-interface {v0}, Lcom/android/server/wm/IAdaptiveSmoothAnimManager;->getContinuousTransitionController()Lcom/android/server/wm/IContinuousTransitionController;
    move-result-object v0
    .line 2719
    invoke-interface {v0, v2}, Lcom/android/server/wm/IContinuousTransitionController;->setPredictiveReadyInRecentsContinuous(Z)V
    .line 2722
    :goto_67
    invoke-static {}, Landroid/os/Binder;->clearCallingIdentity()J
    move-result-wide v2
    .line 2724
    .local v2, "token":J
    :try_start_6b
    iget-object v0, p0, Lcom/android/server/wm/OplusWindowAnimationManager;->mWMService:Lcom/android/server/wm/WindowManagerService;
    invoke-virtual {v0}, Lcom/android/server/wm/WindowManagerService;->getDefaultDisplayContentLocked()Lcom/android/server/wm/DisplayContent;
    move-result-object v0
    .line 2725
    .local v0, "displayContent":Lcom/android/server/wm/DisplayContent;
    if-eqz v0, :cond_7a
    .line 2726
    invoke-virtual {v0}, Lcom/android/server/wm/DisplayContent;->getInputMonitor()Lcom/android/server/wm/InputMonitor;
    move-result-object v4
    invoke-virtual {v4, v1}, Lcom/android/server/wm/InputMonitor;->updateInputWindowsLw(Z)V
    :try_end_7a
    .catchall {:try_start_6b .. :try_end_7a} :catchall_7f
    .line 2729
    .end local v0    # "displayContent":Lcom/android/server/wm/DisplayContent;
    :cond_7a
    invoke-static {v2, v3}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 2730
    nop
    .line 2731
    return v1
    .line 2729
    :catchall_7f
    move-exception v0
    invoke-static {v2, v3}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 2730
    throw v0
.end method
```
