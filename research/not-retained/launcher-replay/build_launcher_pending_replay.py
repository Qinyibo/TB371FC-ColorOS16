import pathlib, re, json, hashlib, zipfile, struct, zlib, sys
from loguru import logger
logger.remove()
sys.path.insert(0, 'work')
from apk_dex_replace import replace_dex

p = pathlib.Path('work/launcher-pending-replay')
target = p/'smali/com/android/quickstep/OplusBaseTouchInteractionService.smali'
source = pathlib.Path('work/launcher-input-source/com/android/quickstep/OplusBaseTouchInteractionService.smali').read_text()
name = 'onInjectDispatchInputEvent(Landroid/view/MotionEvent;)V'
m = re.search(r'(?ms)^\.method [^\n]*'+re.escape(name)+r'\n.*?^\.end method', source)
assert m
old = m[0]
clear = '''    iget-object v0, p0, Lcom/android/quickstep/OplusBaseTouchInteractionService;->mPendingInput:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    move v0, v7'''
assert old.count(clear) == 1
new = old.replace(clear, '    move v0, v7', 1)
gate = '''    :goto_9a
    if-eqz v0, :cond_a5

    if-eqz v1, :cond_a5

    invoke-virtual {v1}, Lcom/android/quickstep/inputconsumers/OplusOtherActivityInputConsumer;->isTouchHandling()Z

    move-result v6

    if-ne v6, v7, :cond_a5

    goto :goto_f1'''
replacement = '''    :goto_9a
    if-eqz v0, :cond_a5

    if-eqz v1, :codex_end_unhandled

    invoke-virtual {v1}, Lcom/android/quickstep/inputconsumers/OplusOtherActivityInputConsumer;->isTouchHandling()Z

    move-result v6

    if-ne v6, v7, :codex_end_unhandled

    # Preserve the existing active consumer's terminal-event path.
    iget-object v6, p0, Lcom/android/quickstep/OplusBaseTouchInteractionService;->mPendingInput:Ljava/util/List;

    invoke-interface {v6}, Ljava/util/List;->clear()V

    goto :goto_f1

    :codex_end_unhandled
    invoke-virtual {p1}, Landroid/view/MotionEvent;->getActionMasked()I

    move-result v6

    if-ne v6, v7, :codex_drop_pending

    iget-object v6, p0, Lcom/android/quickstep/OplusBaseTouchInteractionService;->mPendingInput:Ljava/util/List;

    invoke-interface {v6}, Ljava/util/List;->isEmpty()Z

    move-result v8

    if-nez v8, :codex_drop_pending

    const/4 v8, 0x0

    invoke-interface {v6, v8}, Ljava/util/List;->get(I)Ljava/lang/Object;

    move-result-object v8

    check-cast v8, Landroid/view/MotionEvent;

    invoke-virtual {v8}, Landroid/view/MotionEvent;->getActionMasked()I

    move-result v8

    if-nez v8, :codex_drop_pending

    # Replay only a complete DOWN...UP sequence, once, after resetInterceptState.
    const-string v0, "CodexPendingReplay"

    const-string v1, "replay complete queued gesture"

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    invoke-interface {v6}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :codex_replay_next
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :codex_replay_done

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/view/MotionEvent;

    invoke-direct {p0, v1}, Lcom/android/quickstep/OplusBaseTouchInteractionService;->onDispatchInputEvent(Landroid/view/MotionEvent;)V

    goto :codex_replay_next

    :codex_replay_done
    iget-object v0, p0, Lcom/android/quickstep/OplusBaseTouchInteractionService;->mPendingInput:Ljava/util/List;

    invoke-interface {v0}, Ljava/util/List;->clear()V

    return-void

    :codex_drop_pending
    # Keep CANCEL and incomplete streams discarded as before.
    iget-object v6, p0, Lcom/android/quickstep/OplusBaseTouchInteractionService;->mPendingInput:Ljava/util/List;

    invoke-interface {v6}, Ljava/util/List;->clear()V

    goto :cond_a5'''
assert new.count(gate) == 1
new = new.replace(gate, replacement)
target.write_text(source[:m.start()]+new+source[m.end():], encoding='utf-8', newline='\n')
(p/'original-method.smali').write_text(old)
(p/'candidate-method.smali').write_text(new)
print('TARGET_METHOD_PATCHED')
