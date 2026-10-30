from pathlib import Path
import subprocess,sys,json,re,shlex,sqlite3,datetime
sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,'work');import async_trial as t
O=Path(__file__).resolve().parent;label=sys.argv[1]
r={'label':label,'host_time':datetime.datetime.now().astimezone().isoformat(),'checks':{}}
def check(name,value):
 r['checks'][name]=bool(value)
 if not value:raise AssertionError(name)
print('DEVICE_VERIFY',label,flush=True)
check('boot_and_setup_complete',t.shell('getprop sys.boot_completed; settings get secure user_setup_complete').splitlines()==['1','1'])
r['boot_id']=t.shell('cat /proc/sys/kernel/random/boot_id');r['kernel']=t.shell('uname -a');check('original_kernel43',bool(re.search(r'4\.19\.325-perf\+ #43 SMP',r['kernel'])))
check('selinux_enforcing',t.shell('getenforce')=='Enforcing')
expected={'/system_ext/priv-app/SystemUI/SystemUI.apk':'56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928','/system/framework/oplus-services.jar':'ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467','/vendor/etc/init/r91-rom.rc':'85739a5112d7c096ed72bc2bff8337de29b6ed90671eea1b05c8d8652bbef750'}
for path,h in expected.items():check(path,t.shell('sha256sum '+path).split()[0]==h)
log=t.shell('cat /data/adb/r91-rom/boot.log');(O/(label+'-native-boot.log')).write_text(log,encoding='utf-8')
check('native_init_completed_rc0',r['boot_id'] in log and 'R91_ROM_READY launcher_native=1' in log and log.rstrip().endswith('R91_ROM_EXIT rc=0') and 'R91_ROM_BASE_GUARD_FAILED' not in log)
r['settings']=t.shell('settings get system peak_refresh_rate; settings get system recommender_split_screen_enable; settings get global animator_duration_scale; settings get global transition_animation_scale; settings get global window_animation_scale').splitlines()
check('144hz_recommendations_off',r['settings'][:2]==['144.00002','0'])
check('normal_animation_scales',all(x=='null' or float(x)==1 for x in r['settings'][2:]))
art=t.shell('pm art dump com.android.launcher');check('launcher_speed','[status=speed] [reason=cmdline] [primary-abi]' in art)
modules=t.shell('for p in /data/adb/modules/*; do test -e "$p/disable" || test -e "$p/remove" || basename "$p"; done').splitlines();r['enabled_modules']=modules
check('no_old_bili_or_caption_module',not any(x in modules for x in ['r94_bili_native_rules','tb371fc_caption_input_defer']))
check('no_native_rule_watcher',not re.search(r'app_process /system/bin (R94BiliRules|WeChatParallelScale)\b',t.shell('ps -A -o ARGS')))
camera=t.shell('pm path com.zui.camera').removeprefix('package:');r['camera_sha256']=t.shell('sha256sum '+shlex.quote(camera)).split()[0]
check('camera7',r['camera_sha256']=='0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e')
r['native_pen_ready']=t.shell('getprop debug.r94.pen_v4_ready');check('native_pen_software_ready',r['native_pen_ready']=='1')
db=O/(label+'-window-config.db')
with db.open('wb') as f:subprocess.run(t.ADB+['exec-out','su -c '+shlex.quote('cat /data/user_de/0/com.oplus.exsystemservice/databases/fantasywindow.db')],stdout=f,check=True)
c=sqlite3.connect(db);c.row_factory=sqlite3.Row
rows=[dict(v) for v in c.execute("select * from t_config where package_name in ('com.tencent.mm','tv.danmaku.bili')")]
r['native_window_rules']=rows
for pkg in ['com.tencent.mm','tv.danmaku.bili']:
 row=next(v for v in rows if v['package_name']==pkg and v['use_function']=='magicwindow');body=json.loads(row['custom_config_body'])
 check(pkg+'_native_parallel',row['status']==1 and str(body['scaleWindow'])=='-1' and str(body['UX']['isDraggable'])=='true')
b=json.loads(next(v for v in rows if v['package_name']=='tv.danmaku.bili' and v['use_function']=='magicwindow')['custom_config_body'])
check('bili_live_exception',any(v.get('name')=='com.bilibili.bililive.room.ui.roomv3.LiveRoomActivityV3' and v.get('defaultFullScreen')=='true' for v in b['Activities']))
r['core_pids']=t.shell('pidof system_server com.android.systemui com.android.launcher').split();check('three_core_processes',len(r['core_pids'])==3)
r['crash_buffer']=subprocess.check_output(t.ADB+['shell','logcat','-b','crash','-d'],text=True,encoding='utf-8',errors='replace')
check('no_core_java_crash',not re.search(r'Process: (?:system_server|com.android.systemui|com.android.launcher)(?:,|\s)',r['crash_buffer']))
r['status']='NATIVE_BOOT_CHECKS_PASS_PHYSICAL_PHONE_PEN_AND_USER_SMOOTHNESS_PENDING'
(O/(label+'-result.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in r.items() if k not in ['native_window_rules','crash_buffer']},ensure_ascii=False),flush=True)
