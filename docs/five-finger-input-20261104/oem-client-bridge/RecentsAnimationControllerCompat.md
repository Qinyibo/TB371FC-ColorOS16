# RecentsAnimationControllerCompat

Artifact `accepted Launcher`, SHA256 `bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class public Lcom/android/systemui/shared/system/RecentsAnimationControllerCompat;
.super Ljava/lang/Object;
```

## public setInputConsumerEnabled(Z)V

Local lines 299–322.

```smali
.method public setInputConsumerEnabled(Z)V
    .registers 3
    :try_start_0
    iget-object p0, p0, Lcom/android/systemui/shared/system/RecentsAnimationControllerCompat;->mAnimationController:Lcom/android/wm/shell/recents/IRecentsAnimationController;
    invoke-interface {p0, p1}, Lcom/android/wm/shell/recents/IRecentsAnimationController;->setInputConsumerEnabled(Z)V
    :try_end_5
    .catch Landroid/os/RemoteException; {:try_start_0 .. :try_end_5} :catch_6
    goto :goto_e
    :catch_6
    move-exception p0
    const-string p1, "RecentsAnimationControllerCompat"
    const-string v0, "Failed to set input consumer enabled state"
    invoke-static {p1, v0, p0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :goto_e
    return-void
.end method
```
