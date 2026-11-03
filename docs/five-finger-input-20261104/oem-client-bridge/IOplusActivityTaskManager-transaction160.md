# IOplusActivityTaskManager Stub — transaction160

This is a bounded onTransact branch excerpt, not the complete giant onTransact method. Baseline OEM framework SHA256 `c7cd0e506d1dd1b0de7c713b68e9508b2ce358ce76efb559138ad9c9fe1b4c99`.

The actual packed-switch base plus the index of `:pswitch_a35` evaluates to160 (0xa0); tool check passed. Constant and full selected branch follow. No branch instruction changed.

```smali
.field static final blacklist TRANSACTION_setInputConsumerEnabled:I = 0xa0
    :pswitch_a35
    invoke-virtual {p2}, Landroid/os/Parcel;->readBoolean()Z
    move-result v1
    .line 4063
    .local v1, "_arg0":Z
    invoke-virtual {p2}, Landroid/os/Parcel;->enforceNoDataAvail()V
    .line 4064
    invoke-virtual {p0, v1}, Landroid/app/IOplusActivityTaskManager$Stub;->setInputConsumerEnabled(Z)V
    .line 4065
    goto/16 :goto_1719
```

The shared `:goto_1719` epilogue and other transactions are outside this excerpt.
