# RecentsViewAnimUtil

Artifact `accepted Launcher`, SHA256 `bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d`. Selected complete method bodies; empty lines removed. Opcodes/labels/registers/handlers unchanged. Range: local disassembly lines. Not a patch.

```smali
.class public final Lcom/oplus/quickstep/utils/RecentsViewAnimUtil;
.super Ljava/lang/Object;
```

## public static final setInputConsumerEnabled(Lcom/android/systemui/shared/system/RecentsAnimationControllerCompat;ZLjava/lang/String;)V

Local lines 3752–3949.

```smali
.method public static final setInputConsumerEnabled(Lcom/android/systemui/shared/system/RecentsAnimationControllerCompat;ZLjava/lang/String;)V
    .registers 7
    .annotation runtime Lkotlin/jvm/JvmStatic;
    .end annotation
    const-string v0, "controller"
    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V
    const-string/jumbo v0, "reason"
    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V
    new-instance v0, Ljava/lang/StringBuilder;
    const-string/jumbo v1, "setInputConsumerEnabled: enabled: "
    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;
    const-string v1, ", reason: "
    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p2
    const-string v0, "RecentsViewAnimUtil"
    invoke-static {v0, p2}, Lcom/oplus/basecommon/log/LogUtils;->d(Ljava/lang/String;Ljava/lang/String;)V
    const/4 p2, 0x0
    if-eqz p1, :cond_57
    sget-object v1, Lcom/android/quickstep/OplusBaseTouchInteractionService;->Companion:Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;->getInstance()Lcom/android/quickstep/OplusBaseTouchInteractionService;
    move-result-object v2
    if-eqz v2, :cond_3b
    invoke-virtual {v2}, Lcom/android/quickstep/OplusBaseTouchInteractionService;->getMInputConsumer()Lcom/android/systemui/shared/system/InputConsumerController;
    move-result-object v2
    if-eqz v2, :cond_3b
    iget-object v2, v2, Lcom/oplus/systemui/shared/system/OplusBaseInputConsumerController;->mInputEventReceiver:Lcom/oplus/systemui/shared/system/OplusBaseInputConsumerController$InputEventReceiver;
    goto :goto_3c
    :cond_3b
    move-object v2, p2
    :goto_3c
    if-nez v2, :cond_3f
    goto :goto_42
    :cond_3f
    const/4 v3, 0x0
    iput-boolean v3, v2, Lcom/android/systemui/shared/system/UserBatchedInputEventReceiver;->isHandlingEvent:Z
    :goto_42
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;->getInstance()Lcom/android/quickstep/OplusBaseTouchInteractionService;
    move-result-object v1
    if-eqz v1, :cond_68
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService;->getMInputConsumer()Lcom/android/systemui/shared/system/InputConsumerController;
    move-result-object v1
    if-eqz v1, :cond_68
    new-instance v2, Landroidx/constraintlayout/core/motion/a;
    invoke-direct {v2}, Landroidx/constraintlayout/core/motion/a;-><init>()V
    invoke-virtual {v1, v2}, Lcom/oplus/systemui/shared/system/OplusBaseInputConsumerController;->setKeyEventListener(Lcom/android/systemui/shared/system/InputConsumerController$InputListener;)V
    goto :goto_68
    :cond_57
    sget-object v1, Lcom/android/quickstep/OplusBaseTouchInteractionService;->Companion:Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;->getInstance()Lcom/android/quickstep/OplusBaseTouchInteractionService;
    move-result-object v1
    if-eqz v1, :cond_68
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService;->getMInputConsumer()Lcom/android/systemui/shared/system/InputConsumerController;
    move-result-object v1
    if-eqz v1, :cond_68
    invoke-virtual {v1, p2}, Lcom/oplus/systemui/shared/system/OplusBaseInputConsumerController;->setKeyEventListener(Lcom/android/systemui/shared/system/InputConsumerController$InputListener;)V
    :cond_68
    :goto_68
    sget-object v1, Lcom/android/quickstep/OplusBaseTouchInteractionService;->Companion:Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService$Companion;->getInstance()Lcom/android/quickstep/OplusBaseTouchInteractionService;
    move-result-object v1
    if-eqz v1, :cond_7e
    invoke-virtual {v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService;->getMInputConsumer()Lcom/android/systemui/shared/system/InputConsumerController;
    move-result-object v1
    if-eqz v1, :cond_7e
    invoke-virtual {v1}, Lcom/oplus/systemui/shared/system/OplusBaseInputConsumerController;->isCreateInputConsumerFailed()Z
    move-result p2
    invoke-static {p2}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
    move-result-object p2
    :cond_7e
    invoke-static {}, Lcom/oplus/basecommon/log/LogUtils;->isLoggableDebug()Z
    move-result v1
    if-eqz v1, :cond_a5
    const/16 v1, 0xf
    invoke-static {v1}, Landroid/os/Debug;->getCallers(I)Ljava/lang/String;
    move-result-object v1
    new-instance v2, Ljava/lang/StringBuilder;
    const-string/jumbo v3, "setInputConsumerEnabled: call trace: "
    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    const-string v1, ", createFailed="
    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v2, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p2
    invoke-static {v0, p2}, Lcom/oplus/basecommon/log/LogUtils;->d(Ljava/lang/String;Ljava/lang/String;)V
    goto :goto_c1
    :cond_a5
    if-eqz p1, :cond_c1
    sget-object v1, Ljava/lang/Boolean;->TRUE:Ljava/lang/Boolean;
    invoke-static {p2, v1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z
    move-result v1
    if-eqz v1, :cond_c1
    new-instance v1, Ljava/lang/StringBuilder;
    const-string/jumbo v2, "setInputConsumerEnabled: inputConsumer createFailed="
    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object p2
    invoke-static {v0, p2}, Lcom/oplus/basecommon/log/LogUtils;->d(Ljava/lang/String;Ljava/lang/String;)V
    :cond_c1
    :goto_c1
    invoke-virtual {p0, p1}, Lcom/android/systemui/shared/system/RecentsAnimationControllerCompat;->setInputConsumerEnabled(Z)V
    return-void
.end method
```
