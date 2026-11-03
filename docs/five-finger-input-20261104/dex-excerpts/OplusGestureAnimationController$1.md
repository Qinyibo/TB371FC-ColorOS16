# OplusGestureAnimationController$1 — selected methods

Baseline JAR SHA256: `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Only selected complete methods follow; no instruction, label, register or exception handler was edited. Blank lines omitted for compactness. Original `.line` directives retained; ranges below refer to local disassembly line numbers, not Java source. This is evidence, not a patch.

## public finishGestureAnimation(Landroid/os/Bundle;)V

Disassembly lines 44–583.

```smali
.method public finishGestureAnimation(Landroid/os/Bundle;)V
    .registers 15
    .param p1, "bOptions"    # Landroid/os/Bundle;
    .line 221
    invoke-static {}, Landroid/os/Binder;->clearCallingIdentity()J
    move-result-wide v1
    .line 223
    .local v1, "token":J
    :try_start_4
    const-string v0, "GestureMode"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v0
    move v3, v0
    .line 224
    .local v3, "gestureMode":I
    const/4 v0, 0x1
    packed-switch v3, :pswitch_data_172
    goto/16 :goto_130
    .line 276
    :pswitch_11
    const-string v0, "TaskId"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v0
    move v5, v0
    .line 277
    .local v5, "zoomId":I
    const-string v0, "TargetId"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v6
    .line 278
    .local v6, "splitId":I
    const-string v0, "Bound"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getParcelable(Ljava/lang/String;)Landroid/os/Parcelable;
    move-result-object v0
    move-object v7, v0
    check-cast v7, Landroid/graphics/Rect;
    .line 279
    .local v7, "zoomRect":Landroid/graphics/Rect;
    const-string v0, "Rotation"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v8
    .line 280
    .local v8, "zoomRotation":I
    const-string v0, "Scale"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getFloat(Ljava/lang/String;)F
    move-result v9
    .line 281
    .local v9, "zoomScale":F
    const-string v0, "CornerRadius"
    invoke-virtual {p1, v0}, Landroid/os/Bundle;->getFloat(Ljava/lang/String;)F
    move-result v10
    .line 282
    .local v10, "cornerRadius":F
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static/range {v4 .. v10}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mfinishGestureAnimationAndTransferSplitToZoom(Lcom/android/server/wm/OplusGestureAnimationController;IILandroid/graphics/Rect;IFF)V
    :try_end_3e
    .catchall {:try_start_4 .. :try_end_3e} :catchall_16c
    .line 296
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 283
    return-void
    .line 266
    .end local v5    # "zoomId":I
    .end local v6    # "splitId":I
    .end local v7    # "zoomRect":Landroid/graphics/Rect;
    .end local v8    # "zoomRotation":I
    .end local v9    # "zoomScale":F
    .end local v10    # "cornerRadius":F
    :pswitch_42
    :try_start_42
    const-string v4, "SwitchMode"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v4
    .line 267
    .local v4, "finishMode":I
    if-nez v4, :cond_4c
    .line 268
    goto/16 :goto_130
    .line 269
    :cond_4c
    if-ne v4, v0, :cond_130
    .line 270
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fputmDragZoomToSplit(Lcom/android/server/wm/OplusGestureAnimationController;Z)V
    .line 271
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0, p1}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mfinishGestureAnimationAndTransferZoomToSplit(Lcom/android/server/wm/OplusGestureAnimationController;Landroid/os/Bundle;)V
    :try_end_58
    .catchall {:try_start_42 .. :try_end_58} :catchall_16c
    .line 296
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 272
    return-void
    .line 234
    .end local v4    # "finishMode":I
    :pswitch_5c
    :try_start_5c
    invoke-static {}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$sfgetTAG()Ljava/lang/String;
    move-result-object v4
    const-string/jumbo v5, "test for animation finish GESTURE_FULLSCREEN_DRAG"
    invoke-static {v4, v5}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 235
    const-string v4, "TaskId"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v4
    move v6, v4
    .line 236
    .local v6, "taskId":I
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v4, v6}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fputmPinGestureToZoomTask(Lcom/android/server/wm/OplusGestureAnimationController;I)V
    .line 237
    const-string v4, "Bound"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getParcelable(Ljava/lang/String;)Landroid/os/Parcelable;
    move-result-object v4
    move-object v7, v4
    check-cast v7, Landroid/graphics/Rect;
    .line 238
    .local v7, "rect":Landroid/graphics/Rect;
    const-string v4, "Rotation"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v8
    .line 239
    .local v8, "rotation":I
    const-string v4, "Scale"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getFloat(Ljava/lang/String;)F
    move-result v9
    .line 240
    .local v9, "scale":F
    const-string v4, "Change"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v4
    .line 241
    .local v4, "change":I
    const-string v5, "flexibleActived"
    invoke-virtual {p1, v5}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;)Z
    move-result v11
    .line 242
    .local v11, "isFlexibleActived":Z
    if-ne v4, v0, :cond_dc
    .line 243
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fputmNeedFullToZoomAnimation(Lcom/android/server/wm/OplusGestureAnimationController;Z)V
    .line 244
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v5
    invoke-virtual {v5}, Ljava/util/ArrayList;->size()I
    move-result v5
    if-eqz v5, :cond_d2
    if-nez v11, :cond_d2
    .line 245
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v5
    iget-object v10, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v10}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v10
    invoke-virtual {v10}, Ljava/util/ArrayList;->size()I
    move-result v10
    sub-int/2addr v10, v0
    invoke-virtual {v5, v10}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/view/SurfaceControl;
    .line 246
    .local v0, "dimSurface":Landroid/view/SurfaceControl;
    if-eqz v0, :cond_d2
    .line 247
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    iget-object v10, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v10}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmScreenWidth(Lcom/android/server/wm/OplusGestureAnimationController;)I
    move-result v10
    iget-object v12, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v12}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmScreenHeight(Lcom/android/server/wm/OplusGestureAnimationController;)I
    move-result v12
    invoke-virtual {v5, v10, v12, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->setEmptyResForDim(IILandroid/view/SurfaceControl;)V
    .line 251
    .end local v0    # "dimSurface":Landroid/view/SurfaceControl;
    :cond_d2
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    const/4 v10, 0x1
    invoke-static/range {v5 .. v11}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mfinishGestureAnimationAndStartZoom(Lcom/android/server/wm/OplusGestureAnimationController;ILandroid/graphics/Rect;IFIZ)V
    :try_end_d8
    .catchall {:try_start_5c .. :try_end_d8} :catchall_16c
    .line 296
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 253
    return-void
    .line 255
    :cond_dc
    :try_start_dc
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v5
    invoke-virtual {v5}, Ljava/util/ArrayList;->size()I
    move-result v5
    if-eqz v5, :cond_130
    .line 256
    new-instance v5, Landroid/view/SurfaceControl$Transaction;
    invoke-direct {v5}, Landroid/view/SurfaceControl$Transaction;-><init>()V
    .line 257
    .local v5, "t":Landroid/view/SurfaceControl$Transaction;
    iget-object v10, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v10}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v10
    invoke-virtual {v10}, Ljava/util/ArrayList;->size()I
    move-result v10
    sub-int/2addr v10, v0
    .local v10, "i":I
    :goto_f8
    if-ltz v10, :cond_118
    .line 258
    iget-object v12, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v12}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v12
    invoke-virtual {v12, v10}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v12
    check-cast v12, Landroid/view/SurfaceControl;
    invoke-virtual {v5, v12}, Landroid/view/SurfaceControl$Transaction;->remove(Landroid/view/SurfaceControl;)Landroid/view/SurfaceControl$Transaction;
    .line 259
    invoke-virtual {v5}, Landroid/view/SurfaceControl$Transaction;->apply()V
    .line 260
    iget-object v12, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v12}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmDragAnimationDimSurface(Lcom/android/server/wm/OplusGestureAnimationController;)Ljava/util/ArrayList;
    move-result-object v12
    invoke-virtual {v12, v10}, Ljava/util/ArrayList;->remove(I)Ljava/lang/Object;
    .line 257
    add-int/lit8 v10, v10, -0x1
    goto :goto_f8
    .line 262
    .end local v5    # "t":Landroid/view/SurfaceControl$Transaction;
    .end local v10    # "i":I
    :cond_118
    goto :goto_130
    .line 226
    .end local v4    # "change":I
    .end local v6    # "taskId":I
    .end local v7    # "rect":Landroid/graphics/Rect;
    .end local v8    # "rotation":I
    .end local v9    # "scale":F
    .end local v11    # "isFlexibleActived":Z
    :pswitch_119
    const-string v4, "SwitchMode"
    invoke-virtual {p1, v4}, Landroid/os/Bundle;->getInt(Ljava/lang/String;)I
    move-result v4
    .line 227
    .local v4, "switchMode":I
    if-ne v4, v0, :cond_12a
    .line 228
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mswitchSplitTask(Lcom/android/server/wm/OplusGestureAnimationController;)V
    :try_end_126
    .catchall {:try_start_dc .. :try_end_126} :catchall_16c
    .line 296
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 229
    return-void
    .line 231
    :cond_12a
    :try_start_12a
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5, v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mshowDockDivider(Lcom/android/server/wm/OplusGestureAnimationController;Z)V
    .line 232
    nop
    .line 287
    .end local v4    # "switchMode":I
    :cond_130
    :goto_130
    iget-object v4, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v4}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmService(Lcom/android/server/wm/OplusGestureAnimationController;)Lcom/android/server/wm/WindowManagerService;
    move-result-object v4
    invoke-virtual {v4}, Lcom/android/server/wm/WindowManagerService;->getWindowManagerLock()Ljava/lang/Object;
    move-result-object v4
    monitor-enter v4
    :try_end_13b
    .catchall {:try_start_12a .. :try_end_13b} :catchall_16c
    .line 288
    :try_start_13b
    iget-object v5, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v5}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmPendingNewTaskTargets(Lcom/android/server/wm/OplusGestureAnimationController;)Landroid/util/IntArray;
    move-result-object v5
    invoke-virtual {v5}, Landroid/util/IntArray;->size()I
    move-result v5
    sub-int/2addr v5, v0
    .local v5, "i":I
    :goto_146
    if-ltz v5, :cond_15a
    .line 289
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    iget-object v6, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v6}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmPendingNewTaskTargets(Lcom/android/server/wm/OplusGestureAnimationController;)Landroid/util/IntArray;
    move-result-object v6
    invoke-virtual {v6, v5}, Landroid/util/IntArray;->get(I)I
    move-result v6
    invoke-static {v0, v6}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$mremoveTaskInternal(Lcom/android/server/wm/OplusGestureAnimationController;I)Z
    .line 288
    add-int/lit8 v5, v5, -0x1
    goto :goto_146
    .line 291
    .end local v5    # "i":I
    :cond_15a
    monitor-exit v4
    :try_end_15b
    .catchall {:try_start_13b .. :try_end_15b} :catchall_169
    .line 294
    :try_start_15b
    iget-object v0, p0, Lcom/android/server/wm/OplusGestureAnimationController$1;->this$0:Lcom/android/server/wm/OplusGestureAnimationController;
    invoke-static {v0}, Lcom/android/server/wm/OplusGestureAnimationController;->-$$Nest$fgetmCallbacks(Lcom/android/server/wm/OplusGestureAnimationController;)Lcom/android/server/wm/IOplusGestureAnimationCallbacks;
    move-result-object v0
    invoke-interface {v0}, Lcom/android/server/wm/IOplusGestureAnimationCallbacks;->onAnimationFinished()V
    :try_end_164
    .catchall {:try_start_15b .. :try_end_164} :catchall_16c
    .line 296
    .end local v3    # "gestureMode":I
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 297
    nop
    .line 298
    return-void
    .line 291
    .restart local v3    # "gestureMode":I
    :catchall_169
    move-exception v0
    :try_start_16a
    monitor-exit v4
    :try_end_16b
    .catchall {:try_start_16a .. :try_end_16b} :catchall_169
    .end local v1    # "token":J
    .end local p0    # "this":Lcom/android/server/wm/OplusGestureAnimationController$1;
    .end local p1    # "bOptions":Landroid/os/Bundle;
    :try_start_16b
    throw v0
    :try_end_16c
    .catchall {:try_start_16b .. :try_end_16c} :catchall_16c
    .line 296
    .end local v3    # "gestureMode":I
    .restart local v1    # "token":J
    .restart local p0    # "this":Lcom/android/server/wm/OplusGestureAnimationController$1;
    .restart local p1    # "bOptions":Landroid/os/Bundle;
    :catchall_16c
    move-exception v0
    invoke-static {v1, v2}, Landroid/os/Binder;->restoreCallingIdentity(J)V
    .line 297
    throw v0
    nop
    :pswitch_data_172
    .packed-switch 0x0
        :pswitch_119
        :pswitch_5c
        :pswitch_42
        :pswitch_11
    .end packed-switch
.end method
```
