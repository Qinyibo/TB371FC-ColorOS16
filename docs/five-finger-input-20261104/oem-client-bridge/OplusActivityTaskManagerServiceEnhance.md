# OplusActivityTaskManagerServiceEnhance

Artifact `current oplus-services`, SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class public Lcom/android/server/wm/OplusActivityTaskManagerServiceEnhance;
.super Landroid/app/IOplusActivityTaskManager$Stub;
```

## public setInputConsumerEnabled(Z)V

Local lines 8298–8315.

```smali
.method public setInputConsumerEnabled(Z)V
    .registers 3
    .param p1, "enable"    # Z
    .line 778
    sget-object v0, Lcom/android/server/wm/IOplusWindowAnimationManager;->DEFAULT:Lcom/android/server/wm/IOplusWindowAnimationManager;
    invoke-static {v0}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IOplusWindowAnimationManager;
    invoke-interface {v0, p1}, Lcom/android/server/wm/IOplusWindowAnimationManager;->setInputConsumerEnabled(Z)Z
    .line 779
    return-void
.end method
```
