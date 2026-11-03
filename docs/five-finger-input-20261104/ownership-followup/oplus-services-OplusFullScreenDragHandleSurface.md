# OplusFullScreenDragHandleSurface — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## private unregisterInputConsumer()V

Local disassembly 972–993.

```smali
.method private unregisterInputConsumer()V
    .registers 2
    .line 171
    iget-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    if-eqz v0, :cond_c
    .line 172
    iget-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    invoke-virtual {v0}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->unregisterInputConsumer()V
    .line 173
    const/4 v0, 0x0
    iput-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    .line 175
    :cond_c
    return-void
.end method
```

## public createInputConsumer(Landroid/graphics/Rect;Lcom/android/server/wm/WindowManagerService;Lcom/android/server/wm/DisplayContent;Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;)V

Local disassembly 1064–1129.

```smali
.method public createInputConsumer(Landroid/graphics/Rect;Lcom/android/server/wm/WindowManagerService;Lcom/android/server/wm/DisplayContent;Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;)V
    .registers 9
    .param p1, "rect"    # Landroid/graphics/Rect;
    .param p2, "service"    # Lcom/android/server/wm/WindowManagerService;
    .param p3, "displayContent"    # Lcom/android/server/wm/DisplayContent;
    .param p4, "listener"    # Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;
    .line 152
    if-eqz p2, :cond_2c
    if-nez p3, :cond_5
    goto :goto_2c
    .line 155
    :cond_5
    iget-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    if-nez v0, :cond_24
    .line 156
    new-instance v0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    const-string v1, "OplusFullScreenDragHandleSurface"
    invoke-direct {v0, p2, v1}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;-><init>(Lcom/android/server/wm/WindowManagerService;Ljava/lang/String;)V
    iput-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    .line 157
    new-instance v0, Landroid/os/Binder;
    invoke-direct {v0}, Landroid/os/Binder;-><init>()V
    .line 158
    .local v0, "token":Landroid/os/IBinder;
    iget-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    iget-object v2, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurfaceControl:Landroid/view/SurfaceControl;
    const/4 v3, 0x1
    invoke-virtual {v1, p3, v0, v2, v3}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->registerInputConsumer(Lcom/android/server/wm/DisplayContent;Landroid/os/IBinder;Landroid/view/SurfaceControl;Z)Z
    .line 159
    iget-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    invoke-virtual {v1, p4}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->setInputListener(Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;)V
    .line 161
    .end local v0    # "token":Landroid/os/IBinder;
    :cond_24
    iget-object v0, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mInputConsumer:Lcom/android/server/wm/OplusCompactWindowInputConsumer;
    const/16 v1, 0x20
    invoke-virtual {v0, p1, v1}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->updateInputWindowInfo(Landroid/graphics/Rect;I)V
    .line 162
    return-void
    .line 153
    :cond_2c
    :goto_2c
    return-void
.end method
```

## public destroy()V

Local disassembly 1131–1233.

```smali
.method public destroy()V
    .registers 4
    .line 265
    const-class v0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;
    monitor-enter v0
    .line 266
    :try_start_3
    iget-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurfaceControl:Landroid/view/SurfaceControl;
    if-eqz v1, :cond_49
    iget-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mTransaction:Landroid/view/SurfaceControl$Transaction;
    if-eqz v1, :cond_49
    .line 267
    sget-boolean v1, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->sDEBUG:Z
    if-eqz v1, :cond_37
    .line 268
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "destroy() surface: "
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurfaceControl:Landroid/view/SurfaceControl;
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, "; callers: "
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    const/16 v2, 0xa
    invoke-static {v2}, Landroid/os/Debug;->getCallers(I)Ljava/lang/String;
    move-result-object v2
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-direct {p0, v1}, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->logD(Ljava/lang/String;)V
    .line 270
    :cond_37
    iget-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mTransaction:Landroid/view/SurfaceControl$Transaction;
    iget-object v2, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurfaceControl:Landroid/view/SurfaceControl;
    invoke-virtual {v1, v2}, Landroid/view/SurfaceControl$Transaction;->remove(Landroid/view/SurfaceControl;)Landroid/view/SurfaceControl$Transaction;
    .line 271
    const/4 v1, 0x0
    iput-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurface:Landroid/view/Surface;
    .line 272
    iput-object v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mSurfaceControl:Landroid/view/SurfaceControl;
    .line 273
    const/4 v1, 0x0
    iput-boolean v1, p0, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->mShowing:Z
    .line 274
    invoke-direct {p0}, Lcom/android/server/wm/OplusFullScreenDragHandleSurface;->unregisterInputConsumer()V
    .line 276
    :cond_49
    monitor-exit v0
    .line 277
    return-void
    .line 276
    :catchall_4b
    move-exception v1
    monitor-exit v0
    :try_end_4d
    .catchall {:try_start_3 .. :try_end_4d} :catchall_4b
    throw v1
.end method
```
