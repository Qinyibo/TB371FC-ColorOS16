# OplusActivityManager

Artifact `current OEM framework`, SHA256 `c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class public Landroid/app/OplusActivityManager;
.super Ljava/lang/Object;
```

## public blacklist setInputConsumerEnabled(Z)Z

Local lines 9574–9591.

```smali
.method public blacklist setInputConsumerEnabled(Z)Z
    .registers 3
    .param p1, "enabled"    # Z
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Landroid/os/RemoteException;
        }
    .end annotation
    .line 967
    iget-object v0, p0, Landroid/app/OplusActivityManager;->mOplusAtm:Landroid/app/OplusActivityTaskManager;
    invoke-virtual {v0, p1}, Landroid/app/OplusActivityTaskManager;->setInputConsumerEnabled(Z)Z
    move-result v0
    return v0
.end method
```
