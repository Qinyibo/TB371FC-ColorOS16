# OplusGestureAnimationController — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## constructor <init>(Lcom/android/server/wm/WindowManagerService;Landroid/view/IOplusGestureAnimationRunner;Lcom/android/server/wm/IOplusGestureAnimationCallbacks;I)V

Local disassembly 585–902.

```smali
.method constructor <init>(Lcom/android/server/wm/WindowManagerService;Landroid/view/IOplusGestureAnimationRunner;Lcom/android/server/wm/IOplusGestureAnimationCallbacks;I)V
    .registers 22
    .param p1, "service"    # Lcom/android/server/wm/WindowManagerService;
    .param p2, "remoteAnimationRunner"    # Landroid/view/IOplusGestureAnimationRunner;
    .param p3, "callbacks"    # Lcom/android/server/wm/IOplusGestureAnimationCallbacks;
    .param p4, "displayId"    # I
    .line 304
    move-object/from16 v0, p0
    move-object/from16 v1, p1
    move/from16 v2, p4
    invoke-direct {v0}, Ljava/lang/Object;-><init>()V
    .line 125
    new-instance v3, Ljava/util/ArrayList;
    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingAnimations:Ljava/util/ArrayList;
    .line 126
    new-instance v3, Landroid/util/IntArray;
    const/4 v4, 0x0
    invoke-direct {v3, v4}, Landroid/util/IntArray;-><init>(I)V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingNewTaskTargets:Landroid/util/IntArray;
    .line 127
    new-instance v3, Ljava/util/ArrayList;
    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragAnimationDimSurface:Ljava/util/ArrayList;
    .line 134
    new-instance v3, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda0;
    invoke-direct {v3, v0}, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda0;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;)V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mFailsafeRunnable:Ljava/lang/Runnable;
    .line 149
    const/4 v3, 0x1
    iput-boolean v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingStart:Z
    .line 158
    new-instance v5, Landroid/graphics/Rect;
    invoke-direct {v5}, Landroid/graphics/Rect;-><init>()V
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTmpRect:Landroid/graphics/Rect;
    .line 179
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mGestureFullScreenDragStart:Z
    .line 180
    const/4 v5, -0x1
    iput v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mLoadResForDimLayer:I
    .line 181
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mNeedFullToZoomAnimation:Z
    .line 182
    const/high16 v5, 0x42840000    # 66.0f
    iput v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomCornerRadius:F
    .line 183
    iput v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitCornerRadius:F
    .line 184
    const/high16 v5, 0x3f000000    # 0.5f
    iput v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTotalDimAlpha:F
    .line 185
    new-instance v5, Landroid/graphics/Point;
    invoke-direct {v5}, Landroid/graphics/Point;-><init>()V
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragDimFinalPosition:Landroid/graphics/Point;
    .line 187
    new-instance v5, Landroid/graphics/Rect;
    invoke-direct {v5}, Landroid/graphics/Rect;-><init>()V
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragDimFinalRegion:Landroid/graphics/Rect;
    .line 189
    const/4 v5, 0x0
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomAnimationLeash:Landroid/view/SurfaceControl;
    .line 190
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetAnimationLeash:Landroid/view/SurfaceControl;
    .line 196
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomStack:Lcom/android/server/wm/Task;
    .line 197
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetSplitModel:Z
    .line 198
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragSplitStack:Lcom/android/server/wm/Task;
    .line 199
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragSplitModel:Z
    .line 200
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomModel:Z
    .line 201
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTmpTopWallpaper:Lcom/android/server/wm/WindowState;
    .line 202
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mChangeToZoomTask:Lcom/android/server/wm/Task;
    .line 203
    iput-boolean v4, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomToSplit:Z
    .line 204
    const v6, 0x3dcccccd    # 0.1f
    iput v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mBlurRadiusWallPaperRatio:F
    .line 205
    const/4 v6, 0x3
    iput v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragZoomInSplitModeTaskNum:I
    .line 206
    new-instance v7, Landroid/view/animation/OplusBezierInterpolator;
    const-wide/high16 v14, 0x3ff0000000000000L    # 1.0
    const/16 v16, 0x1
    const-wide v8, 0x3fd3333333333333L    # 0.3
    const-wide/16 v10, 0x0
    const-wide v12, 0x3fb999999999999aL    # 0.1
    invoke-direct/range {v7 .. v16}, Landroid/view/animation/OplusBezierInterpolator;-><init>(DDDDZ)V
    iput-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mOplusBezierInterpolator:Landroid/view/animation/OplusBezierInterpolator;
    .line 207
    invoke-static {}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->getInstance()Lcom/oplus/splitscreen/OplusSplitScreenManager;
    move-result-object v6
    invoke-virtual {v6}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->isTabletDevice()Z
    move-result v6
    iput-boolean v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mTabletFeature:Z
    .line 208
    invoke-static {}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->getInstance()Lcom/oplus/splitscreen/OplusSplitScreenManager;
    move-result-object v6
    invoke-virtual {v6}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->isFoldDevice()Z
    move-result v6
    if-eqz v6, :cond_a3
    .line 209
    invoke-static {}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->getInstance()Lcom/oplus/splitscreen/OplusSplitScreenManager;
    move-result-object v6
    invoke-virtual {v6}, Lcom/oplus/splitscreen/OplusSplitScreenManager;->isDragonflyDevice()Z
    move-result v6
    if-nez v6, :cond_a3
    move v6, v3
    goto :goto_a4
    :cond_a3
    move v6, v4
    :goto_a4
    iput-boolean v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mFoldFeature:Z
    .line 210
    iput-boolean v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDragSplitAnimationFinish:Z
    .line 211
    new-instance v3, Ljava/util/ArrayList;
    invoke-direct {v3}, Ljava/util/ArrayList;-><init>()V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mSplitChildSurface:Ljava/util/ArrayList;
    .line 215
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mStartFullScreenAnimation:Ljava/lang/Runnable;
    .line 217
    new-instance v3, Lcom/android/server/wm/OplusGestureAnimationController$1;
    invoke-direct {v3, v0}, Lcom/android/server/wm/OplusGestureAnimationController$1;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;)V
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mController:Landroid/view/IOplusGestureAnimationController;
    .line 305
    iput-object v1, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    .line 306
    move-object/from16 v3, p2
    iput-object v3, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mRunner:Landroid/view/IOplusGestureAnimationRunner;
    .line 307
    move-object/from16 v5, p3
    iput-object v5, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mCallbacks:Lcom/android/server/wm/IOplusGestureAnimationCallbacks;
    .line 308
    iput v2, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayId:I
    .line 309
    iget-object v6, v1, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v6, v2}, Lcom/android/server/wm/RootWindowContainer;->getDisplayContent(I)Lcom/android/server/wm/DisplayContent;
    move-result-object v6
    iput-object v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    .line 310
    iget-object v6, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v6, v6, Lcom/android/server/wm/WindowManagerService;->mDisplayManager:Landroid/hardware/display/DisplayManager;
    invoke-virtual {v6, v4}, Landroid/hardware/display/DisplayManager;->getDisplay(I)Landroid/view/Display;
    move-result-object v4
    .line 311
    .local v4, "display":Landroid/view/Display;
    new-instance v6, Landroid/util/DisplayMetrics;
    invoke-direct {v6}, Landroid/util/DisplayMetrics;-><init>()V
    .line 312
    .local v6, "displayMetrics":Landroid/util/DisplayMetrics;
    invoke-virtual {v4, v6}, Landroid/view/Display;->getRealMetrics(Landroid/util/DisplayMetrics;)V
    .line 313
    iget v7, v6, Landroid/util/DisplayMetrics;->heightPixels:I
    iput v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mScreenHeight:I
    .line 314
    iget v7, v6, Landroid/util/DisplayMetrics;->widthPixels:I
    iput v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mScreenWidth:I
    .line 315
    invoke-static {}, Lcom/android/server/wm/OplusZoomWindowManagerService;->getInstance()Lcom/android/server/wm/OplusZoomWindowManagerService;
    move-result-object v7
    iput-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mZoomService:Lcom/android/server/wm/OplusZoomWindowManagerService;
    .line 316
    new-instance v7, Landroid/os/HandlerThread;
    const-string v8, "gesture animation Handler"
    invoke-direct {v7, v8}, Landroid/os/HandlerThread;-><init>(Ljava/lang/String;)V
    iput-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationThread:Landroid/os/HandlerThread;
    .line 317
    iget-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationThread:Landroid/os/HandlerThread;
    invoke-virtual {v7}, Landroid/os/HandlerThread;->start()V
    .line 318
    new-instance v7, Landroid/os/Handler;
    iget-object v8, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationThread:Landroid/os/HandlerThread;
    invoke-virtual {v8}, Landroid/os/HandlerThread;->getLooper()Landroid/os/Looper;
    move-result-object v8
    invoke-direct {v7, v8}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V
    iput-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mAnimationHandler:Landroid/os/Handler;
    .line 319
    iget-object v7, v0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v7}, Lcom/android/server/wm/DisplayContent;->getDisplayRotation()Lcom/android/server/wm/DisplayRotation;
    move-result-object v7
    invoke-virtual {v7}, Lcom/android/server/wm/DisplayRotation;->pause()V
    .line 320
    return-void
.end method
```

## private synthetic lambda$new$0()V

Local disassembly 5397–5406.

```smali
.method private synthetic lambda$new$0()V
    .registers 2
    .line 134
    const-string v0, "failSafeRunnable"
    invoke-virtual {p0, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->cancelAnimation(Ljava/lang/String;)V
    return-void
.end method
```

## public initializeDragFullScreenAnmation(Lcom/android/server/wm/Task;Lcom/android/server/wm/Task;Lcom/android/server/wm/ActivityRecord;Landroid/os/Bundle;)V

Local disassembly 7957–8225.

```smali
.method public initializeDragFullScreenAnmation(Lcom/android/server/wm/Task;Lcom/android/server/wm/Task;Lcom/android/server/wm/ActivityRecord;Landroid/os/Bundle;)V
    .registers 11
    .param p1, "topTask"    # Lcom/android/server/wm/Task;
    .param p2, "targetTask"    # Lcom/android/server/wm/Task;
    .param p3, "targetActivity"    # Lcom/android/server/wm/ActivityRecord;
    .param p4, "bOptions"    # Landroid/os/Bundle;
    .line 1028
    const/4 v0, 0x0
    .line 1029
    .local v0, "needsZBoost":Z
    const/4 v1, 0x0
    .line 1030
    .local v1, "toSplitScreen":Z
    const/4 v2, 0x0
    if-eqz p4, :cond_1f
    .line 1031
    const-string v3, "GestureMode"
    invoke-virtual {p4, v3}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v3
    .line 1032
    .local v3, "gestureMode":I
    const-string v4, "LoadRes"
    invoke-virtual {p4, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v4
    iput v4, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mLoadResForDimLayer:I
    .line 1033
    const-string v4, "ZBoost"
    invoke-virtual {p4, v4, v2}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;Z)Z
    move-result v0
    .line 1034
    const-string v4, "Toggle_Split_Screen"
    invoke-virtual {p4, v4, v2}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;Z)Z
    move-result v1
    .line 1042
    .end local v3    # "gestureMode":I
    :cond_1f
    invoke-virtual {p0, p1, v0, v1}, Lcom/android/server/wm/OplusGestureAnimationController;->addAnimation(Lcom/android/server/wm/Task;ZZ)Lcom/android/server/wm/AnimationAdapter;
    .line 1043
    iget-boolean v3, p3, Lcom/android/server/wm/ActivityRecord;->mLaunchTaskBehind:Z
    if-eqz v3, :cond_29
    .line 1044
    invoke-virtual {p0, p2, v2, v1}, Lcom/android/server/wm/OplusGestureAnimationController;->addAnimation(Lcom/android/server/wm/Task;ZZ)Lcom/android/server/wm/AnimationAdapter;
    .line 1046
    :cond_29
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingAnimations:Ljava/util/ArrayList;
    invoke-virtual {v2}, Ljava/util/ArrayList;->isEmpty()Z
    move-result v2
    if-eqz v2, :cond_38
    .line 1047
    const-string/jumbo v2, "initialize-noVisibleTasks"
    invoke-virtual {p0, v2}, Lcom/android/server/wm/OplusGestureAnimationController;->cancelAnimation(Ljava/lang/String;)V
    .line 1048
    return-void
    .line 1051
    :cond_38
    :try_start_38
    invoke-direct {p0}, Lcom/android/server/wm/OplusGestureAnimationController;->linkToDeathOfRunner()V
    :try_end_3b
    .catch Landroid/os/RemoteException; {:try_start_38 .. :try_end_3b} :catch_d5
    .line 1055
    nop
    .line 1058
    if-nez v1, :cond_63
    .line 1059
    sget-object v2, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, " current full task will drag to flexible task"
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    invoke-static {v2, v3}, Landroid/util/Slog;->d(Ljava/lang/String;Ljava/lang/String;)I
    .line 1060
    invoke-virtual {p1}, Lcom/android/server/wm/Task;->getWrapper()Lcom/android/server/wm/ITaskWrapper;
    move-result-object v2
    invoke-interface {v2}, Lcom/android/server/wm/ITaskWrapper;->getExtImpl()Lcom/android/server/wm/ITaskExt;
    move-result-object v2
    const/16 v3, 0x1000
    invoke-interface {v2, v3}, Lcom/android/server/wm/ITaskExt;->addFlexibleCustomTransitionType(I)V
    .line 1063
    :cond_63
    iput-object p3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mTargetActivityRecord:Lcom/android/server/wm/ActivityRecord;
    .line 1064
    invoke-virtual {p3}, Lcom/android/server/wm/ActivityRecord;->windowsCanBeWallpaperTarget()Z
    move-result v2
    if-eqz v2, :cond_78
    .line 1065
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    iget v3, v2, Lcom/android/server/wm/DisplayContent;->pendingLayoutChanges:I
    or-int/lit8 v3, v3, 0x4
    iput v3, v2, Lcom/android/server/wm/DisplayContent;->pendingLayoutChanges:I
    .line 1066
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v2}, Lcom/android/server/wm/DisplayContent;->setLayoutNeeded()V
    .line 1068
    :cond_78
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v2, v2, Lcom/android/server/wm/WindowManagerService;->mWindowPlacerLocked:Lcom/android/server/wm/WindowSurfacePlacer;
    invoke-virtual {v2}, Lcom/android/server/wm/WindowSurfacePlacer;->performSurfacePlacement()V
    .line 1069
    iget-boolean v2, p3, Lcom/android/server/wm/ActivityRecord;->mLaunchTaskBehind:Z
    if-eqz v2, :cond_a1
    .line 1070
    const/4 v2, 0x1
    iput-boolean v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mGestureFullScreenDragStart:Z
    .line 1072
    new-instance v2, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda2;
    invoke-direct {v2, p0}, Lcom/android/server/wm/OplusGestureAnimationController$$ExternalSyntheticLambda2;-><init>(Lcom/android/server/wm/OplusGestureAnimationController;)V
    iput-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mStartFullScreenAnimation:Ljava/lang/Runnable;
    .line 1077
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v2, v2, Lcom/android/server/wm/WindowManagerService;->mAnimationHandler:Landroid/os/Handler;
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mStartFullScreenAnimation:Ljava/lang/Runnable;
    invoke-virtual {v2, v3}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V
    .line 1078
    iget-object v2, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v2, v2, Lcom/android/server/wm/WindowManagerService;->mAnimationHandler:Landroid/os/Handler;
    iget-object v3, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mStartFullScreenAnimation:Ljava/lang/Runnable;
    const-wide/16 v4, 0x1388
    invoke-virtual {v2, v3, v4, v5}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z
    .line 1080
    :cond_a1
    sget-object v2, Lcom/android/server/wm/OplusGestureAnimationController;->TAG:Ljava/lang/String;
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v4, "initializeDragFullScreenAnmation: topTask = "
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v3
    const-string v4, "   targetTask = "
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v3
    const-string v4, "   mPendingAnimations.size= "
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimationController;->mPendingAnimations:Ljava/util/ArrayList;
    .line 1082
    invoke-virtual {v4}, Ljava/util/ArrayList;->size()I
    move-result v4
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    .line 1080
    invoke-static {v2, v3}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 1083
    return-void
    .line 1052
    :catch_d5
    move-exception v2
    .line 1053
    .local v2, "e":Landroid/os/RemoteException;
    const-string/jumbo v3, "initialize-failedToLinkToDeath"
    invoke-virtual {p0, v3}, Lcom/android/server/wm/OplusGestureAnimationController;->cancelAnimation(Ljava/lang/String;)V
    .line 1054
    return-void
.end method
```

## scheduleFailsafe()V

Local disassembly 10681–10697.

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
