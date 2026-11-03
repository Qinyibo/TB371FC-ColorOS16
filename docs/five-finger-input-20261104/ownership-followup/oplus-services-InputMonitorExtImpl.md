# InputMonitorExtImpl — requested ownership methods

Artifact: `oplus-services`; SHA256 `a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136`.
Selected complete method bodies; only empty lines removed. All opcodes, labels, handlers, registers and `.line` directives unchanged. Range is local disassembly line number. Not a patch.

## public getInputConsumerEnabled()Z

Local disassembly 724–741.

```smali
.method public getInputConsumerEnabled()Z
    .registers 2
    .line 232
    sget-object v0, Lcom/android/server/wm/IOplusWindowAnimationManager;->DEFAULT:Lcom/android/server/wm/IOplusWindowAnimationManager;
    invoke-static {v0}, Landroid/common/OplusFeatureCache;->get(Landroid/common/IOplusCommonFeature;)Landroid/common/IOplusCommonFeature;
    move-result-object v0
    check-cast v0, Lcom/android/server/wm/IOplusWindowAnimationManager;
    invoke-interface {v0}, Lcom/android/server/wm/IOplusWindowAnimationManager;->getInputConsumerEnabled()Z
    move-result v0
    return v0
.end method
```
