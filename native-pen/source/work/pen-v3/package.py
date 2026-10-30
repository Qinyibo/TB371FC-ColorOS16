from pathlib import Path
import json,hashlib,shutil,zipfile,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
W=Path(__file__).resolve().parent;ROOT=W.parent;M=W/'module';M.mkdir(exist_ok=True);A=M/'assets';A.mkdir(exist_ok=True)
app=json.loads((W/'build/result.json').read_text());system=json.loads((ROOT/'pen-system/build/result.json').read_text());old=json.loads((ROOT/'pen-loader-v2/build-result.json').read_text())
for n in ['bootstrap.jar','manifest.properties','ipe.recipe.gz','ws.recipe.gz']:shutil.copyfile(W/'loader-v4'/n,A/n)
shutil.copyfile(ROOT/'pen-loader-v2/pen-mount-ro',A/'pen-mount-ro')
F=M/'framework';F.mkdir(exist_ok=True);shutil.copyfile(ROOT/'pen-system/build/services.jar',F/'services.jar')
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
source=(ROOT/'pen-startup-module/activate.sh').read_text(encoding='utf-8').replace('r94-pen-native-v2','r94-pen-native-v4')
rollback=(ROOT/'pen-startup-module/rollback.sh').read_text(encoding='utf-8')
for k in ['ipe','ws']:
 source=source.replace(old[k]['expected_sha256'],app[k]['target_sha256']);rollback=rollback.replace(old[k]['expected_sha256'],app[k]['target_sha256'])
rollback=rollback.replace('am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1','if [ "$(am get-started-user-state 0 2>&1)" != RUNNING_LOCKED ]; then\n    am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1\nfi')
write(M/'activate.sh',source);write(M/'rollback.sh',rollback)
activation=(M/'activate.sh').read_text(encoding='utf-8')
activation=activation.replace('am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService >/dev/null 2>&1','''state=$(/system/bin/am get-started-user-state 0 2>&1)
if [ "$state" = RUNNING_LOCKED ]; then
    echo WAITING_FOR_NORMAL_USER_UNLOCK
elif launch=$(/system/bin/am startservice -n com.oplus.ipemanager/com.oplus.ipemanager.btadsorb.CoreService 2>&1); then
    echo "$launch"
else
    state=$(/system/bin/am get-started-user-state 0 2>&1)
    if [ "$state" = RUNNING_LOCKED ]; then
        echo WAITING_FOR_NORMAL_USER_UNLOCK
    else
        echo "$launch"
        exit 1
    fi
fi''')
write(M/'activate.sh',activation)
shutil.copyfile(ROOT/'pen-startup-module/service.sh',M/'service.sh')
write(M/'skip_mount','')
write(M/'module.prop','''id=r94_pen_bootstrap_v2
name=TB371FC 原生笔事件桥与GATT接入（私有待硬件验收）
version=0.4
versionCode=4
author=TB371FC local repair
description=CTN730真实事件、原生按键动作、GATT读取队列和已配对笔重连。无LSPosed。物理功能尚未验收。
''')
write(M/'post-fs-data.sh','''#!/system/bin/sh
set -eu
MODDIR=${0%/*}
exec >"$MODDIR/framework-startup.log" 2>&1
test "$(getprop ro.product.board)" = spinel || exit 0
test "$(getprop ro.build.version.incremental)" = V.2e733a1-dda927-df323a || exit 0
test "$(getenforce)" = Enforcing
test "$(sha256sum /system/framework/services.jar | cut -d ' ' -f 1)" = '''+system['base_sha256']+'''
test "$(sha256sum "$MODDIR/framework/services.jar" | cut -d ' ' -f 1)" = '''+system['target_sha256']+'''
chmod 0644 "$MODDIR/framework/services.jar"
chcon u:object_r:system_file:s0 "$MODDIR/framework/services.jar"
mount --bind "$MODDIR/framework/services.jar" /system/framework/services.jar
"$MODDIR/assets/pen-framework-ro" /system/framework/services.jar
echo NATIVE_FRAMEWORK_BOUND
''')
write(M/'README.txt','''私有候选v0.4；当前TB371FC/spinel/SDK36/指定增量版本，原始内核39。
包含旧试验交付修正、新GATT回调和值快照、串行读取队列、设备空间真实状态、CoreService内有界重连。
services.jar只改PhoneWindowManager的systemReady和手写笔按键分支，其他DEX保留；新增系统笔输入观察与本机CTN730事件桥。
CTN730只读cached附着/电量/充电/MAC，不写GPIO/I2C/固件/触控诊断节点；不会把吸附等同蓝牙已连接。
CTN730确认的真实笔MAC允许无BLE HID服务的SPI笔接入；仍须实际配对、GATT连接和可读/可订阅电量服务。
重启锁屏期间等待正常解锁后，由系统原生事件启动原有CoreService。
原始签名APK先扫描，开机完成后校验并只读挂载生成代码；无LSPosed，无普通第三方应用改动。
禁用本模块并正常重启恢复原services.jar及APK；不得在系统运行中热重启system_server来回退。
工程代码和软件启动检查不能代替真实笔书写、压感、磁吸、按键或手机通信共享的验收。
''')
write(M/'manifest.json',json.dumps({'app':app,'system':system,'scope':'native_pen_candidate_only','physical_pen_tested':False,'phone_communication_fixed':False},indent=2)+'\n')
print('V3_MODULE_STAGED',app['ipe']['target_sha256'],system['target_sha256'])
