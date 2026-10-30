from pathlib import Path
import subprocess,shlex,zipfile,hashlib,json,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace');W=Path(__file__).resolve().parent;M=W/'comm-recovery-module';M.mkdir(exist_ok=True);OUT=W.parent/'outputs'
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
write(M/'module.prop','''id=r94_commcenter_recovery
name=TB371FC 通信中心异常恢复修正
version=0.1
versionCode=1
author=TB371FC local repair
description=恢复通信中心后台的init自动重启能力；不强制会话或SIM状态，不代表真手机通信共享全部通过。
''')
write(M/'skip_mount','')
write(M/'service.sh','''#!/system/bin/sh
set -eu
MODDIR=${0%/*}
exec >"$MODDIR/recovery.log" 2>&1
test "$(getprop ro.product.board)" = spinel || exit 0
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a || exit 0
test "$(getenforce)" = Enforcing
count=0
while [ "$(getprop sys.boot_completed)" != 1 ]; do
    [ "$count" -lt 120 ] || exit 1
    [ ! -e "$MODDIR/disable" ] && [ ! -e "$MODDIR/remove" ] || exit 0
    sleep 1
    count=$((count+1))
done
setprop ctl.oneshot_off r94-commcenterd
if [ "$(getprop init.svc.r94-commcenterd)" != running ]; then
    setprop ctl.start r94-commcenterd
fi
echo INIT_OWNS_COMM_CENTER_RESTART
''')
write(M/'README.txt','''本机受控退出对照：修正前通信中心在15秒采样窗内未自动恢复，需手动启动；修正后约3秒采样即观察到新进程，Radio/IMS会话重新打开。
仅切换r94-commcenterd的oneshot标志，由Android init负责原生恢复。启动脚本运行一次后退出，没有Root常驻轮询。
虚拟RIL已经能按需自动恢复，本包不改它；不改SIM、PhoneAccount、能力协商、数据路由、音频或SELinux。
禁用模块并正常重启可恢复原init配置。本轮不能证明远端手机拨号/来电/音频/移动数据/短信已正常。
ROM固化：在现有r94-commcenterd服务定义中去掉oneshot；其余配置保持不变。
AOSP依据：https://android.googlesource.com/platform/system/core/+/refs/heads/main/init/README.md
''')
target=OUT/'TB371FC-通信中心异常恢复修正-v0.1.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED)as z:
 for p in M.rglob('*'):
  if p.is_file():
   info=zipfile.ZipInfo(p.relative_to(M).as_posix(),(2026,10,21,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100755 if p.suffix=='.sh'else 0o100644)<<16;z.writestr(info,p.read_bytes())
print(str(target),hashlib.sha256(target.read_bytes()).hexdigest())
