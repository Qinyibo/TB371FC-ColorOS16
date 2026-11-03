# RecentsAnimationControllerCompat — selected methods

Artifact `launcher-withdrawn-copy`, SHA256 `97ac1b9d0ab1f0986b8b25d41b39a0d5dd378a7518239bae4acf02173080bf55`. Selected complete bodies, empty lines removed; no opcode/label/register/handler changes. Ranges are local disassembly lines. Not a patch.

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
