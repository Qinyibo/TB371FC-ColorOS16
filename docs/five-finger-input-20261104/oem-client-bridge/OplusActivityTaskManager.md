# OplusActivityTaskManager

Artifact `current OEM framework`, SHA256 `c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class public Landroid/app/OplusActivityTaskManager;
.super Ljava/lang/Object;
```

## public blacklist setInputConsumerEnabled(Z)Z

Local lines 4069–4089.

```smali
.method public blacklist setInputConsumerEnabled(Z)Z
    .registers 3
    .param p1, "enabled"    # Z
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Landroid/os/RemoteException;
        }
    .end annotation
    .line 509
    invoke-static {}, Landroid/app/OplusActivityTaskManager;->getService()Landroid/app/IOplusActivityTaskManager;
    move-result-object v0
    invoke-interface {v0, p1}, Landroid/app/IOplusActivityTaskManager;->setInputConsumerEnabled(Z)V
    .line 510
    const/4 v0, 0x1
    return v0
.end method
```
