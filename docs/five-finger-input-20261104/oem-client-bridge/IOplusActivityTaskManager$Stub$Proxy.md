# IOplusActivityTaskManager$Stub$Proxy

Artifact `current OEM framework`, SHA256 `c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class Landroid/app/IOplusActivityTaskManager$Stub$Proxy;
.super Ljava/lang/Object;
```

## public blacklist setInputConsumerEnabled(Z)V

Local lines 15280–15338.

```smali
.method public blacklist setInputConsumerEnabled(Z)V
    .registers 7
    .param p1, "enabled"    # Z
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Landroid/os/RemoteException;
        }
    .end annotation
    .line 8341
    invoke-virtual {p0}, Landroid/app/IOplusActivityTaskManager$Stub$Proxy;->asBinder()Landroid/os/IBinder;
    move-result-object v0
    invoke-static {v0}, Landroid/os/Parcel;->obtain(Landroid/os/IBinder;)Landroid/os/Parcel;
    move-result-object v0
    .line 8343
    .local v0, "_data":Landroid/os/Parcel;
    :try_start_8
    const-string v1, "android.app.IOplusActivityTaskManager"
    invoke-virtual {v0, v1}, Landroid/os/Parcel;->writeInterfaceToken(Ljava/lang/String;)V
    .line 8344
    invoke-virtual {v0, p1}, Landroid/os/Parcel;->writeBoolean(Z)V
    .line 8345
    iget-object v1, p0, Landroid/app/IOplusActivityTaskManager$Stub$Proxy;->mRemote:Landroid/os/IBinder;
    const/4 v2, 0x0
    const/4 v3, 0x1
    const/16 v4, 0xa0
    invoke-interface {v1, v4, v0, v2, v3}, Landroid/os/IBinder;->transact(ILandroid/os/Parcel;Landroid/os/Parcel;I)Z
    :try_end_19
    .catchall {:try_start_8 .. :try_end_19} :catchall_1e
    .line 8348
    invoke-virtual {v0}, Landroid/os/Parcel;->recycle()V
    .line 8349
    nop
    .line 8350
    return-void
    .line 8348
    :catchall_1e
    move-exception v1
    invoke-virtual {v0}, Landroid/os/Parcel;->recycle()V
    .line 8349
    throw v1
.end method
```
