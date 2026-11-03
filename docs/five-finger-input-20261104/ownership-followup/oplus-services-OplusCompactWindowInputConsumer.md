# OplusCompactWindowInputConsumer — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## constructor <init>(Lcom/android/server/wm/WindowManagerService;Ljava/lang/String;)V

Local disassembly 109–165.

```smali
.method constructor <init>(Lcom/android/server/wm/WindowManagerService;Ljava/lang/String;)V
    .registers 5
    .param p1, "service"    # Lcom/android/server/wm/WindowManagerService;
    .param p2, "name"    # Ljava/lang/String;
    .line 116
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    .line 59
    new-instance v0, Landroid/graphics/Rect;
    invoke-direct {v0}, Landroid/graphics/Rect;-><init>()V
    iput-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mTmpClipRect:Landroid/graphics/Rect;
    .line 73
    const/4 v0, 0x0
    iput-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mOsenseClient:Lcom/oplus/osense/OsenseResClient;
    .line 75
    new-instance v1, Ljava/lang/Object;
    invoke-direct {v1}, Ljava/lang/Object;-><init>()V
    iput-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mLock:Ljava/lang/Object;
    .line 76
    new-instance v1, Ljava/lang/Object;
    invoke-direct {v1}, Ljava/lang/Object;-><init>()V
    iput-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputLock:Ljava/lang/Object;
    .line 77
    iput-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mChoreographer:Landroid/view/Choreographer;
    .line 117
    iput-object p1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mService:Lcom/android/server/wm/WindowManagerService;
    .line 118
    iput-object p2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mName:Ljava/lang/String;
    .line 119
    iget-object v0, p1, Lcom/android/server/wm/WindowManagerService;->mTransactionFactory:Ljava/util/function/Supplier;
    invoke-interface {v0}, Ljava/util/function/Supplier;->get()Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/view/SurfaceControl$Transaction;
    iput-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mTransaction:Landroid/view/SurfaceControl$Transaction;
    .line 120
    return-void
.end method
```

## registerInputConsumer(Lcom/android/server/wm/DisplayContent;Landroid/os/IBinder;Landroid/view/SurfaceControl;Z)Z

Local disassembly 747–1109.

```smali
.method registerInputConsumer(Lcom/android/server/wm/DisplayContent;Landroid/os/IBinder;Landroid/view/SurfaceControl;Z)Z
    .registers 12
    .param p1, "displayContent"    # Lcom/android/server/wm/DisplayContent;
    .param p2, "token"    # Landroid/os/IBinder;
    .param p3, "surfaceControl"    # Landroid/view/SurfaceControl;
    .param p4, "isMin"    # Z
    .line 160
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    const/4 v1, 0x0
    if-eqz v0, :cond_d
    .line 161
    const-string v0, "OplusCompactWindowInputConsumer"
    const-string v2, "compact input already registered"
    invoke-static {v0, v2}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 162
    return v1
    .line 164
    :cond_d
    iput-object p1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    .line 165
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v0, v0, Lcom/android/server/wm/WindowManagerService;->mInputManager:Lcom/android/server/input/InputManagerService;
    const-string v2, "OplusCompactWindowInputConsumer"
    invoke-virtual {v0, v2}, Lcom/android/server/input/InputManagerService;->createInputChannel(Ljava/lang/String;)Landroid/view/InputChannel;
    move-result-object v0
    iput-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    .line 166
    invoke-static {}, Lcom/android/server/UiThread;->getHandler()Landroid/os/Handler;
    move-result-object v0
    .line 167
    .local v0, "handler":Landroid/os/Handler;
    iget-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mChoreographer:Landroid/view/Choreographer;
    if-nez v2, :cond_2a
    .line 168
    invoke-virtual {v0}, Landroid/os/Handler;->getLooper()Landroid/os/Looper;
    move-result-object v2
    invoke-direct {p0, v2, v1}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->createChoreographerWithLooper(Landroid/os/Looper;I)V
    .line 170
    :cond_2a
    iget-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mChoreographer:Landroid/view/Choreographer;
    if-eqz v2, :cond_3d
    .line 171
    new-instance v2, Lcom/android/server/wm/OplusCompactWindowInputConsumer$CompactInputEventReceiver;
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    .line 172
    invoke-virtual {v0}, Landroid/os/Handler;->getLooper()Landroid/os/Looper;
    move-result-object v4
    iget-object v5, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mChoreographer:Landroid/view/Choreographer;
    invoke-direct {v2, p0, v3, v4, v5}, Lcom/android/server/wm/OplusCompactWindowInputConsumer$CompactInputEventReceiver;-><init>(Lcom/android/server/wm/OplusCompactWindowInputConsumer;Landroid/view/InputChannel;Landroid/os/Looper;Landroid/view/Choreographer;)V
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputEventReceiver:Lcom/android/server/wm/OplusCompactWindowInputConsumer$CompactInputEventReceiver;
    .line 176
    :cond_3d
    new-instance v2, Landroid/view/InputApplicationHandle;
    new-instance v3, Landroid/os/Binder;
    invoke-direct {v3}, Landroid/os/Binder;-><init>()V
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mName:Ljava/lang/String;
    sget v5, Landroid/os/InputConstants;->DEFAULT_DISPATCHING_TIMEOUT_MILLIS:I
    int-to-long v5, v5
    invoke-direct {v2, v3, v4, v5, v6}, Landroid/view/InputApplicationHandle;-><init>(Landroid/os/IBinder;Ljava/lang/String;J)V
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mApplicationHandle:Landroid/view/InputApplicationHandle;
    .line 178
    iget-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mLock:Ljava/lang/Object;
    monitor-enter v2
    .line 179
    :try_start_51
    new-instance v3, Landroid/view/InputWindowHandle;
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mApplicationHandle:Landroid/view/InputApplicationHandle;
    iget-object v5, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    .line 180
    invoke-virtual {v5}, Lcom/android/server/wm/DisplayContent;->getDisplayId()I
    move-result v5
    invoke-direct {v3, v4, v5}, Landroid/view/InputWindowHandle;-><init>(Landroid/view/InputApplicationHandle;I)V
    iput-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    .line 181
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mName:Ljava/lang/String;
    iput-object v4, v3, Landroid/view/InputWindowHandle;->name:Ljava/lang/String;
    .line 182
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    invoke-virtual {v4}, Landroid/view/InputChannel;->getToken()Landroid/os/IBinder;
    move-result-object v4
    iput-object v4, v3, Landroid/view/InputWindowHandle;->token:Landroid/os/IBinder;
    .line 183
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iput v1, v3, Landroid/view/InputWindowHandle;->layoutParamsFlags:I
    .line 184
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    const/16 v4, 0x8fd
    iput v4, v3, Landroid/view/InputWindowHandle;->layoutParamsType:I
    .line 185
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    sget v4, Landroid/os/InputConstants;->DEFAULT_DISPATCHING_TIMEOUT_MILLIS:I
    int-to-long v4, v4
    iput-wide v4, v3, Landroid/view/InputWindowHandle;->dispatchingTimeoutMillis:J
    .line 187
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    or-int/lit8 v4, v4, 0x4
    iput v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 188
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    and-int/lit8 v4, v4, -0x21
    iput v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 189
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    and-int/lit16 v4, v4, -0x81
    iput v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 190
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    or-int/lit16 v4, v4, 0x100
    iput v4, v3, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 192
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    invoke-static {}, Landroid/os/Process;->myPid()I
    move-result v4
    iput v4, v3, Landroid/view/InputWindowHandle;->ownerPid:I
    .line 193
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    invoke-static {}, Landroid/os/Process;->myUid()I
    move-result v4
    iput v4, v3, Landroid/view/InputWindowHandle;->ownerUid:I
    .line 194
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    const/high16 v4, 0x3f800000    # 1.0f
    iput v4, v3, Landroid/view/InputWindowHandle;->scaleFactor:F
    .line 195
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v3, v3, Landroid/view/InputWindowHandle;->touchableRegion:Landroid/graphics/Region;
    invoke-virtual {v3}, Landroid/graphics/Region;->setEmpty()V
    .line 197
    new-instance v3, Landroid/graphics/Rect;
    invoke-direct {v3}, Landroid/graphics/Rect;-><init>()V
    .line 198
    .local v3, "displayBounds":Landroid/graphics/Rect;
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v4, v3}, Lcom/android/server/wm/DisplayContent;->getBounds(Landroid/graphics/Rect;)V
    .line 199
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, v4, Landroid/view/InputWindowHandle;->frame:Landroid/graphics/Rect;
    iget v5, v3, Landroid/graphics/Rect;->left:I
    iput v5, v4, Landroid/graphics/Rect;->left:I
    .line 200
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, v4, Landroid/view/InputWindowHandle;->frame:Landroid/graphics/Rect;
    iget v5, v3, Landroid/graphics/Rect;->top:I
    iput v5, v4, Landroid/graphics/Rect;->top:I
    .line 201
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, v4, Landroid/view/InputWindowHandle;->frame:Landroid/graphics/Rect;
    iget v5, v3, Landroid/graphics/Rect;->right:I
    iput v5, v4, Landroid/graphics/Rect;->right:I
    .line 202
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget-object v4, v4, Landroid/view/InputWindowHandle;->frame:Landroid/graphics/Rect;
    iget v5, v3, Landroid/graphics/Rect;->bottom:I
    iput v5, v4, Landroid/graphics/Rect;->bottom:I
    .line 203
    .end local v3    # "displayBounds":Landroid/graphics/Rect;
    monitor-exit v2
    :try_end_e9
    .catchall {:try_start_51 .. :try_end_e9} :catchall_120
    .line 205
    iget-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v2}, Lcom/android/server/wm/DisplayContent;->getDisplayId()I
    move-result v2
    invoke-direct {p0, v2, p3, p4}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->showInputSurface(ILandroid/view/SurfaceControl;Z)V
    .line 206
    const-string v2, "OplusCompactWindowInputConsumer"
    new-instance v3, Ljava/lang/StringBuilder;
    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V
    const-string/jumbo v4, "register surfaceControl: "
    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v3
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v3
    invoke-static {v2, v3}, Landroid/util/Slog;->v(Ljava/lang/String;Ljava/lang/String;)I
    .line 208
    :try_start_10b
    iput-object p2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientCallback:Landroid/os/IBinder;
    .line 209
    iget-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientCallback:Landroid/os/IBinder;
    invoke-interface {v2, p0, v1}, Landroid/os/IBinder;->linkToDeath(Landroid/os/IBinder$DeathRecipient;I)V
    :try_end_112
    .catch Landroid/os/RemoteException; {:try_start_10b .. :try_end_112} :catch_115
    .line 216
    nop
    .line 217
    const/4 v1, 0x1
    return v1
    .line 210
    :catch_115
    move-exception v2
    .line 212
    .local v2, "e":Landroid/os/RemoteException;
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputStateObserver:Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputStateObserver;
    if-eqz v3, :cond_11f
    .line 213
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputStateObserver:Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputStateObserver;
    invoke-interface {v3}, Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputStateObserver;->binderDied()V
    .line 215
    :cond_11f
    return v1
    .line 203
    .end local v2    # "e":Landroid/os/RemoteException;
    :catchall_120
    move-exception v1
    :try_start_121
    monitor-exit v2
    :try_end_122
    .catchall {:try_start_121 .. :try_end_122} :catchall_120
    throw v1
.end method
```

## unregisterInputConsumer()V

Local disassembly 1152–1341.

```smali
.method unregisterInputConsumer()V
    .registers 6
    .line 221
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    if-nez v0, :cond_c
    .line 222
    const-string v0, "OplusCompactWindowInputConsumer"
    const-string v1, "compact input not registered"
    invoke-static {v0, v1}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 223
    return-void
    .line 225
    :cond_c
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputLock:Ljava/lang/Object;
    monitor-enter v0
    .line 226
    :try_start_f
    iget-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mListener:Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;
    const/4 v2, 0x0
    if-eqz v1, :cond_1b
    .line 227
    iget-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mListener:Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;
    invoke-interface {v1}, Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;->removeLeash()V
    .line 228
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mListener:Lcom/android/server/wm/OplusCompactWindowInputConsumer$InputListener;
    .line 230
    :cond_1b
    monitor-exit v0
    :try_end_1c
    .catchall {:try_start_f .. :try_end_1c} :catchall_80
    .line 231
    const-string v0, "OplusCompactWindowInputConsumer"
    const-string/jumbo v1, "unregisterInputConsumer... "
    invoke-static {v0, v1}, Landroid/util/Slog;->v(Ljava/lang/String;Ljava/lang/String;)I
    .line 232
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    invoke-virtual {v0}, Lcom/android/server/wm/DisplayContent;->getDisplayId()I
    move-result v0
    invoke-direct {p0, v0}, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->hideInputSurface(I)V
    .line 233
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v0, v0, Lcom/android/server/wm/WindowManagerService;->mInputManager:Lcom/android/server/input/InputManagerService;
    iget-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    invoke-virtual {v1}, Landroid/view/InputChannel;->getToken()Landroid/os/IBinder;
    move-result-object v1
    invoke-virtual {v0, v1}, Lcom/android/server/input/InputManagerService;->removeInputChannel(Landroid/os/IBinder;)V
    .line 234
    invoke-static {}, Lcom/android/server/UiThread;->getHandler()Landroid/os/Handler;
    move-result-object v0
    new-instance v1, Lcom/android/server/wm/OplusCompactWindowInputConsumer$DisposeInputRunnable;
    iget-object v3, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputEventReceiver:Lcom/android/server/wm/OplusCompactWindowInputConsumer$CompactInputEventReceiver;
    iget-object v4, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    invoke-direct {v1, p0, v3, v4}, Lcom/android/server/wm/OplusCompactWindowInputConsumer$DisposeInputRunnable;-><init>(Lcom/android/server/wm/OplusCompactWindowInputConsumer;Landroid/view/BatchedInputEventReceiver;Landroid/view/InputChannel;)V
    invoke-virtual {v0, v1}, Landroid/os/Handler;->postAtFrontOfQueue(Ljava/lang/Runnable;)Z
    .line 235
    iget-object v1, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mLock:Ljava/lang/Object;
    monitor-enter v1
    .line 236
    :try_start_4d
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mWindowHandle:Landroid/view/InputWindowHandle;
    .line 237
    monitor-exit v1
    :try_end_50
    .catchall {:try_start_4d .. :try_end_50} :catchall_7d
    .line 238
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mInputEventReceiver:Lcom/android/server/wm/OplusCompactWindowInputConsumer$CompactInputEventReceiver;
    .line 239
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mApplicationHandle:Landroid/view/InputApplicationHandle;
    .line 240
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientChannel:Landroid/view/InputChannel;
    .line 241
    iput-object v2, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mDisplayContent:Lcom/android/server/wm/DisplayContent;
    .line 243
    :try_start_58
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientCallback:Landroid/os/IBinder;
    if-eqz v0, :cond_62
    .line 244
    iget-object v0, p0, Lcom/android/server/wm/OplusCompactWindowInputConsumer;->mClientCallback:Landroid/os/IBinder;
    const/4 v1, 0x0
    invoke-interface {v0, p0, v1}, Landroid/os/IBinder;->unlinkToDeath(Landroid/os/IBinder$DeathRecipient;I)Z
    :try_end_62
    .catch Ljava/lang/Exception; {:try_start_58 .. :try_end_62} :catch_63
    .line 248
    :cond_62
    goto :goto_7c
    .line 246
    :catch_63
    move-exception v0
    .line 247
    .local v0, "e":Ljava/lang/Exception;
    const-string v1, "OplusCompactWindowInputConsumer"
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    const-string v3, "error unlinking to death: "
    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-static {v1, v2}, Landroid/util/Slog;->e(Ljava/lang/String;Ljava/lang/String;)I
    .line 249
    .end local v0    # "e":Ljava/lang/Exception;
    :goto_7c
    return-void
    .line 237
    :catchall_7d
    move-exception v0
    :try_start_7e
    monitor-exit v1
    :try_end_7f
    .catchall {:try_start_7e .. :try_end_7f} :catchall_7d
    throw v0
    .line 230
    :catchall_80
    move-exception v1
    :try_start_81
    monitor-exit v0
    :try_end_82
    .catchall {:try_start_81 .. :try_end_82} :catchall_80
    throw v1
.end method
```
