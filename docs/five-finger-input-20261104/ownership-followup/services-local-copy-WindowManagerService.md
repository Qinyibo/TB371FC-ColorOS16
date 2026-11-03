# WindowManagerService — requested ownership methods

Artifact: `services-local-copy`; SHA256 `90948f136d8621cf86be52f7899bec5490e53a1a548f169a9fc90be890143520`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## public createInputConsumer(Landroid/os/IBinder;Ljava/lang/String;ILandroid/view/InputChannel;)V

Local disassembly 20473–20643.

```smali
.method public createInputConsumer(Landroid/os/IBinder;Ljava/lang/String;ILandroid/view/InputChannel;)V
    .registers 13
    .param p1, "token"    # Landroid/os/IBinder;
    .param p2, "name"    # Ljava/lang/String;
    .param p3, "displayId"    # I
    .param p4, "inputChannel"    # Landroid/view/InputChannel;
    .line 7201
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mAtmService:Lcom/android/server/wm/ActivityTaskManagerService;
    invoke-static {}, Landroid/os/Binder;->getCallingUid()I
    move-result v1
    invoke-virtual {v0, v1}, Lcom/android/server/wm/ActivityTaskManagerService;->isCallerRecents(I)Z
    move-result v0
    if-nez v0, :cond_1f
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mContext:Landroid/content/Context;
    const-string v1, "android.permission.INPUT_CONSUMER"
    .line 7202
    invoke-virtual {v0, v1}, Landroid/content/Context;->checkCallingOrSelfPermission(Ljava/lang/String;)I
    move-result v0
    if-nez v0, :cond_17
    goto :goto_1f
    .line 7203
    :cond_17
    new-instance v0, Ljava/lang/SecurityException;
    const-string v1, "createInputConsumer requires INPUT_CONSUMER permission"
    invoke-direct {v0, v1}, Ljava/lang/SecurityException;-><init>(Ljava/lang/String;)V
    throw v0
    .line 7206
    :cond_1f
    :goto_1f
    iget-object v1, p0, Lcom/android/server/wm/WindowManagerService;->mGlobalLock:Lcom/android/server/wm/WindowManagerGlobalLock;
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->boostPriorityForLockedSection()V
    monitor-enter v1
    .line 7207
    :try_start_25
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v0, p3}, Lcom/android/server/wm/RootWindowContainer;->getDisplayContent(I)Lcom/android/server/wm/DisplayContent;
    move-result-object v0
    .line 7208
    .local v0, "display":Lcom/android/server/wm/DisplayContent;
    if-eqz v0, :cond_40
    .line 7209
    invoke-virtual {v0}, Lcom/android/server/wm/DisplayContent;->getInputMonitor()Lcom/android/server/wm/InputMonitor;
    move-result-object v2
    .line 7210
    invoke-static {}, Landroid/os/Binder;->getCallingPid()I
    move-result v6
    invoke-static {}, Landroid/os/Binder;->getCallingUserHandle()Landroid/os/UserHandle;
    move-result-object v7
    :try_end_39
    .catchall {:try_start_25 .. :try_end_39} :catchall_48
    .line 7209
    move-object v3, p1
    move-object v4, p2
    move-object v5, p4
    .end local p1    # "token":Landroid/os/IBinder;
    .end local p2    # "name":Ljava/lang/String;
    .end local p4    # "inputChannel":Landroid/view/InputChannel;
    .local v3, "token":Landroid/os/IBinder;
    .local v4, "name":Ljava/lang/String;
    .local v5, "inputChannel":Landroid/view/InputChannel;
    :try_start_3c
    invoke-virtual/range {v2 .. v7}, Lcom/android/server/wm/InputMonitor;->createInputConsumer(Landroid/os/IBinder;Ljava/lang/String;Landroid/view/InputChannel;ILandroid/os/UserHandle;)V
    goto :goto_43
    .line 7208
    .end local v3    # "token":Landroid/os/IBinder;
    .end local v4    # "name":Ljava/lang/String;
    .end local v5    # "inputChannel":Landroid/view/InputChannel;
    .restart local p1    # "token":Landroid/os/IBinder;
    .restart local p2    # "name":Ljava/lang/String;
    .restart local p4    # "inputChannel":Landroid/view/InputChannel;
    :cond_40
    move-object v3, p1
    move-object v4, p2
    move-object v5, p4
    .line 7212
    .end local v0    # "display":Lcom/android/server/wm/DisplayContent;
    .end local p1    # "token":Landroid/os/IBinder;
    .end local p2    # "name":Ljava/lang/String;
    .end local p4    # "inputChannel":Landroid/view/InputChannel;
    .restart local v3    # "token":Landroid/os/IBinder;
    .restart local v4    # "name":Ljava/lang/String;
    .restart local v5    # "inputChannel":Landroid/view/InputChannel;
    :goto_43
    monitor-exit v1
    :try_end_44
    .catchall {:try_start_3c .. :try_end_44} :catchall_52
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    .line 7213
    return-void
    .line 7212
    .end local v3    # "token":Landroid/os/IBinder;
    .end local v4    # "name":Ljava/lang/String;
    .end local v5    # "inputChannel":Landroid/view/InputChannel;
    .restart local p1    # "token":Landroid/os/IBinder;
    .restart local p2    # "name":Ljava/lang/String;
    .restart local p4    # "inputChannel":Landroid/view/InputChannel;
    :catchall_48
    move-exception v0
    move-object v3, p1
    move-object v4, p2
    move-object v5, p4
    move-object p1, v0
    .end local p1    # "token":Landroid/os/IBinder;
    .end local p2    # "name":Ljava/lang/String;
    .end local p4    # "inputChannel":Landroid/view/InputChannel;
    .restart local v3    # "token":Landroid/os/IBinder;
    .restart local v4    # "name":Ljava/lang/String;
    .restart local v5    # "inputChannel":Landroid/view/InputChannel;
    :goto_4d
    :try_start_4d
    monitor-exit v1
    :try_end_4e
    .catchall {:try_start_4d .. :try_end_4e} :catchall_52
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    throw p1
    :catchall_52
    move-exception v0
    move-object p1, v0
    goto :goto_4d
.end method
```

## public destroyInputConsumer(Landroid/os/IBinder;I)Z

Local disassembly 20901–21006.

```smali
.method public destroyInputConsumer(Landroid/os/IBinder;I)Z
    .registers 6
    .param p1, "token"    # Landroid/os/IBinder;
    .param p2, "displayId"    # I
    .line 7217
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mAtmService:Lcom/android/server/wm/ActivityTaskManagerService;
    invoke-static {}, Landroid/os/Binder;->getCallingUid()I
    move-result v1
    invoke-virtual {v0, v1}, Lcom/android/server/wm/ActivityTaskManagerService;->isCallerRecents(I)Z
    move-result v0
    if-nez v0, :cond_1f
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mContext:Landroid/content/Context;
    const-string v1, "android.permission.INPUT_CONSUMER"
    .line 7218
    invoke-virtual {v0, v1}, Landroid/content/Context;->checkCallingOrSelfPermission(Ljava/lang/String;)I
    move-result v0
    if-nez v0, :cond_17
    goto :goto_1f
    .line 7219
    :cond_17
    new-instance v0, Ljava/lang/SecurityException;
    const-string v1, "destroyInputConsumer requires INPUT_CONSUMER permission"
    invoke-direct {v0, v1}, Ljava/lang/SecurityException;-><init>(Ljava/lang/String;)V
    throw v0
    .line 7222
    :cond_1f
    :goto_1f
    iget-object v0, p0, Lcom/android/server/wm/WindowManagerService;->mGlobalLock:Lcom/android/server/wm/WindowManagerGlobalLock;
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->boostPriorityForLockedSection()V
    monitor-enter v0
    .line 7223
    :try_start_25
    iget-object v1, p0, Lcom/android/server/wm/WindowManagerService;->mRoot:Lcom/android/server/wm/RootWindowContainer;
    invoke-virtual {v1, p2}, Lcom/android/server/wm/RootWindowContainer;->getDisplayContent(I)Lcom/android/server/wm/DisplayContent;
    move-result-object v1
    .line 7224
    .local v1, "display":Lcom/android/server/wm/DisplayContent;
    if-eqz v1, :cond_3a
    .line 7225
    invoke-virtual {v1}, Lcom/android/server/wm/DisplayContent;->getInputMonitor()Lcom/android/server/wm/InputMonitor;
    move-result-object v2
    invoke-virtual {v2, p1}, Lcom/android/server/wm/InputMonitor;->destroyInputConsumer(Landroid/os/IBinder;)Z
    move-result v2
    monitor-exit v0
    :try_end_36
    .catchall {:try_start_25 .. :try_end_36} :catchall_40
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    return v2
    .line 7227
    :cond_3a
    :try_start_3a
    monitor-exit v0
    :try_end_3b
    .catchall {:try_start_3a .. :try_end_3b} :catchall_40
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    const/4 v0, 0x0
    return v0
    .line 7228
    .end local v1    # "display":Lcom/android/server/wm/DisplayContent;
    :catchall_40
    move-exception v1
    :try_start_41
    monitor-exit v0
    :try_end_42
    .catchall {:try_start_41 .. :try_end_42} :catchall_40
    invoke-static {}, Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V
    throw v1
.end method
```
