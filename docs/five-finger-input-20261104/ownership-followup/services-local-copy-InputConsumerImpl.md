# InputConsumerImpl — requested ownership methods

Artifact: `services-local-copy`; SHA256 `90948f136d8621cf86be52f7899bec5490e53a1a548f169a9fc90be890143520`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## public binderDied()V

Local disassembly 312–376.

```smali
.method public binderDied()V
    .registers 5
    .line 183
    iget-object v0, p0, Lcom/android/server/wm/InputConsumerImpl;->mService:Lcom/android/server/wm/WindowManagerService;
    invoke-virtual {v0}, Lcom/android/server/wm/WindowManagerService;->getWindowManagerLock()Ljava/lang/Object;
    move-result-object v0
    monitor-enter v0
    .line 185
    :try_start_7
    iget-object v1, p0, Lcom/android/server/wm/InputConsumerImpl;->mService:Lcom/android/server/wm/WindowManagerService;
    iget-object v1, v1, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    iget-object v2, p0, Lcom/android/server/wm/InputConsumerImpl;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v2, v2, Landroid/view/InputWindowHandle;->displayId:I
    invoke-virtual {v1, v2}, Lcom/android/server/wm/RootWindowContainer;->getDisplayContent(I)Lcom/android/server/wm/DisplayContent;
    move-result-object v1
    .line 186
    .local v1, "dc":Lcom/android/server/wm/DisplayContent;
    if-nez v1, :cond_17
    .line 187
    monitor-exit v0
    return-void
    .line 189
    :cond_17
    invoke-virtual {v1}, Lcom/android/server/wm/DisplayContent;->getInputMonitor()Lcom/android/server/wm/InputMonitor;
    move-result-object v2
    iget-object v3, p0, Lcom/android/server/wm/InputConsumerImpl;->mToken:Landroid/os/IBinder;
    invoke-virtual {v2, v3}, Lcom/android/server/wm/InputMonitor;->destroyInputConsumer(Landroid/os/IBinder;)Z
    .line 190
    invoke-virtual {p0}, Lcom/android/server/wm/InputConsumerImpl;->unlinkFromDeathRecipient()V
    .line 191
    .end local v1    # "dc":Lcom/android/server/wm/DisplayContent;
    monitor-exit v0
    .line 192
    return-void
    .line 191
    :catchall_25
    move-exception v1
    monitor-exit v0
    :try_end_27
    .catchall {:try_start_7 .. :try_end_27} :catchall_25
    throw v1
.end method
```
