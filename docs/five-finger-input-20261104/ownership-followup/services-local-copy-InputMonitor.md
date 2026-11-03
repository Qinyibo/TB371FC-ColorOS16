# InputMonitor — requested ownership methods

Artifact: `services-local-copy`; SHA256 `90948f136d8621cf86be52f7899bec5490e53a1a548f169a9fc90be890143520`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## createInputConsumer(Landroid/os/IBinder;Ljava/lang/String;Landroid/view/InputChannel;ILandroid/os/UserHandle;)V

Local disassembly 1281–1534.

```smali
.method createInputConsumer(Landroid/os/IBinder;Ljava/lang/String;Landroid/view/InputChannel;ILandroid/os/UserHandle;)V
    .registers 17
    .param p1, "token"    # Landroid/os/IBinder;
    .param p2, "name"    # Ljava/lang/String;
    .param p3, "inputChannel"    # Landroid/view/InputChannel;
    .param p4, "clientPid"    # I
    .param p5, "clientUser"    # Landroid/os/UserHandle;
    .line 266
    move-object/from16 v6, p5
    invoke-virtual {p0, p2}, Lcom/android/server/wm/InputMonitor;->getInputConsumer(Ljava/lang/String;)Lcom/android/server/wm/InputConsumerImpl;
    move-result-object v9
    .line 267
    .local v9, "existingConsumer":Lcom/android/server/wm/InputConsumerImpl;
    const-string v10, ", display: "
    if-eqz v9, :cond_43
    iget-object v0, v9, Lcom/android/server/wm/InputConsumerImpl;->mClientUser:Landroid/os/UserHandle;
    invoke-virtual {v0, v6}, Landroid/os/UserHandle;->equals(Ljava/lang/Object;)Z
    move-result v0
    if-eqz v0, :cond_43
    .line 268
    iget-object v0, v9, Lcom/android/server/wm/InputConsumerImpl;->mToken:Landroid/os/IBinder;
    invoke-virtual {p0, v0}, Lcom/android/server/wm/InputMonitor;->destroyInputConsumer(Landroid/os/IBinder;)Z
    .line 269
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V
    const-string v1, "Replacing existing input consumer found with name: "
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    iget v1, p0, Lcom/android/server/wm/InputMonitor;->mDisplayId:I
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v0
    const-string v1, ", user: "
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    move-result-object v0
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v0
    const-string v1, "WindowManager"
    invoke-static {v1, v0}, Landroid/util/Slog;->w(Ljava/lang/String;Ljava/lang/String;)I
    .line 273
    :cond_43
    new-instance v0, Lcom/android/server/wm/InputConsumerImpl;
    iget-object v1, p0, Lcom/android/server/wm/InputMonitor;->mService:Lcom/android/server/wm/WindowManagerService;
    iget v7, p0, Lcom/android/server/wm/InputMonitor;->mDisplayId:I
    iget-object v8, p0, Lcom/android/server/wm/InputMonitor;->mInputTransaction:Landroid/view/SurfaceControl$Transaction;
    move-object v2, p1
    move-object v3, p2
    move-object v4, p3
    move v5, p4
    invoke-direct/range {v0 .. v8}, Lcom/android/server/wm/InputConsumerImpl;-><init>(Lcom/android/server/wm/WindowManagerService;Landroid/os/IBinder;Ljava/lang/String;Landroid/view/InputChannel;ILandroid/os/UserHandle;ILandroid/view/SurfaceControl$Transaction;)V
    .line 275
    .local v0, "consumer":Lcom/android/server/wm/InputConsumerImpl;
    invoke-virtual {p2}, Ljava/lang/Object;->hashCode()I
    move-result v1
    sparse-switch v1, :sswitch_data_c4
    :cond_59
    goto :goto_86
    :sswitch_5a
    const-string/jumbo v1, "wallpaper_input_consumer"
    invoke-virtual {p2, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_59
    const/4 v1, 0x0
    goto :goto_87
    :sswitch_65
    const-string/jumbo v1, "pip_input_consumer"
    invoke-virtual {p2, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_59
    const/4 v1, 0x1
    goto :goto_87
    :sswitch_70
    const-string/jumbo v1, "recents_child_input_consumer"
    invoke-virtual {p2, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_59
    const/4 v1, 0x3
    goto :goto_87
    :sswitch_7b
    const-string/jumbo v1, "recents_animation_input_consumer"
    invoke-virtual {p2, v1}, Ljava/lang/Object;->equals(Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_59
    const/4 v1, 0x2
    goto :goto_87
    :goto_86
    const/4 v1, -0x1
    :goto_87
    packed-switch v1, :pswitch_data_d6
    .line 290
    new-instance v1, Ljava/lang/IllegalArgumentException;
    new-instance v2, Ljava/lang/StringBuilder;
    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    const-string v4, "Illegal input consumer : "
    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v2
    iget v4, p0, Lcom/android/server/wm/InputMonitor;->mDisplayId:I
    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v2
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-direct {v1, v2}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V
    throw v1
    .line 287
    :pswitch_ad
    iget-object v1, v0, Lcom/android/server/wm/InputConsumerImpl;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v2, v1, Landroid/view/InputWindowHandle;->inputConfig:I
    and-int/lit8 v2, v2, -0x5
    iput v2, v1, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 288
    goto :goto_c0
    .line 281
    :pswitch_b6
    goto :goto_c0
    .line 277
    :pswitch_b7
    iget-object v1, v0, Lcom/android/server/wm/InputConsumerImpl;->mWindowHandle:Landroid/view/InputWindowHandle;
    iget v2, v1, Landroid/view/InputWindowHandle;->inputConfig:I
    or-int/lit8 v2, v2, 0x20
    iput v2, v1, Landroid/view/InputWindowHandle;->inputConfig:I
    .line 278
    nop
    .line 293
    :goto_c0
    invoke-direct {p0, v0}, Lcom/android/server/wm/InputMonitor;->addInputConsumer(Lcom/android/server/wm/InputConsumerImpl;)V
    .line 294
    return-void
    :sswitch_data_c4
    .sparse-switch
        -0x5af18033 -> :sswitch_7b
        0x1730ceb5 -> :sswitch_70
        0x3d13fc73 -> :sswitch_65
        0x5463dca8 -> :sswitch_5a
    .end sparse-switch
    :pswitch_data_d6
    .packed-switch 0x0
        :pswitch_b7
        :pswitch_b6
        :pswitch_ad
        :pswitch_ad
    .end packed-switch
.end method
```

## destroyInputConsumer(Landroid/os/IBinder;)Z

Local disassembly 1536–1601.

```smali
.method destroyInputConsumer(Landroid/os/IBinder;)Z
    .registers 5
    .param p1, "token"    # Landroid/os/IBinder;
    .line 216
    const/4 v0, 0x0
    .local v0, "i":I
    :goto_1
    iget-object v1, p0, Lcom/android/server/wm/InputMonitor;->mInputConsumers:Ljava/util/ArrayList;
    invoke-virtual {v1}, Ljava/util/ArrayList;->size()I
    move-result v1
    if-ge v0, v1, :cond_29
    .line 217
    iget-object v1, p0, Lcom/android/server/wm/InputMonitor;->mInputConsumers:Ljava/util/ArrayList;
    invoke-virtual {v1, v0}, Ljava/util/ArrayList;->get(I)Ljava/lang/Object;
    move-result-object v1
    check-cast v1, Lcom/android/server/wm/InputConsumerImpl;
    .line 218
    .local v1, "consumer":Lcom/android/server/wm/InputConsumerImpl;
    if-eqz v1, :cond_26
    iget-object v2, v1, Lcom/android/server/wm/InputConsumerImpl;->mToken:Landroid/os/IBinder;
    if-ne v2, p1, :cond_26
    .line 219
    iget-object v2, p0, Lcom/android/server/wm/InputMonitor;->mInputTransaction:Landroid/view/SurfaceControl$Transaction;
    invoke-virtual {v1, v2}, Lcom/android/server/wm/InputConsumerImpl;->disposeChannelsLw(Landroid/view/SurfaceControl$Transaction;)V
    .line 220
    iget-object v2, p0, Lcom/android/server/wm/InputMonitor;->mInputConsumers:Ljava/util/ArrayList;
    invoke-virtual {v2, v1}, Ljava/util/ArrayList;->remove(Ljava/lang/Object;)Z
    .line 221
    const/4 v2, 0x1
    invoke-virtual {p0, v2}, Lcom/android/server/wm/InputMonitor;->updateInputWindowsLw(Z)V
    .line 222
    return v2
    .line 216
    .end local v1    # "consumer":Lcom/android/server/wm/InputConsumerImpl;
    :cond_26
    add-int/lit8 v0, v0, 0x1
    goto :goto_1
    .line 225
    .end local v0    # "i":I
    :cond_29
    const/4 v0, 0x0
    return v0
.end method
```
