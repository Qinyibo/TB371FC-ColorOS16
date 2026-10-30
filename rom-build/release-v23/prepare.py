import sys,pathlib,shutil,hashlib,json,subprocess,posixpath
sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,'work');import async_trial as t
O=pathlib.Path('work/release-v23').resolve();R=pathlib.Path('D:/TB371FC-release/R94T-v23-build');P=R/'payloads';P.mkdir(parents=True,exist_ok=True)
BASE=pathlib.Path('D:/TB371FC-release/R94T-v22b-FIRSTBOOT-CAMERA-PRIVATE_TEST')
manifest=json.loads((BASE/'manifest.json').read_text(encoding='utf-8-sig'))
def sha(f):
 with f.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def capture(device,name):
 path=P/name
 with path.open('wb') as out:subprocess.run(t.ADB+['exec-out','su -c '+__import__('shlex').quote('cat '+device)],stdout=out,check=True)
 return path
apply=capture('/system_ext/etc/r91-rom/apply.sh','apply.sh');s=apply.read_text(encoding='utf-8')
old='7ea250fb0b7b00830a48b6ad111c795dc3adfcbb0d7b8c5a261f63d309b29762';new='ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467'
assert s.count(old)==1;s=s.replace(old,new)
needle='    settings put system peak_refresh_rate 144.00002';assert s.count(needle)==1
s=s.replace(needle,needle+'\n    settings put system recommender_split_screen_enable 0')
needle='echo R91_ROM_NATIVE_BASE_IDENTITIES_OK';assert s.count(needle)==1
warm='''
# Preserve the accepted launcher speed compilation after a clean installation.
# A failed optimization must not prevent the existing ROM setup from continuing.
launcher_aot_state=/data/adb/r94-launcher-aot-v23
mkdir -p "$launcher_aot_state"
if [ ! -f "$launcher_aot_state/complete" ]; then
    aot_result=$(cmd package compile -m speed -f com.android.launcher 2>&1) || aot_result=failed
    printf '%s\n' "$aot_result"
    if printf '%s\n' "$aot_result" | grep -q '^Success'; then
        touch "$launcher_aot_state/complete"
        cmd pinner repin || echo R94_LAUNCHER_PIN_PENDING
    else
        echo R94_LAUNCHER_AOT_PENDING
    fi
fi
'''
s=s.replace(needle,needle+'\n'+warm);apply.write_text(s,encoding='utf-8',newline='\n')
delivery=capture('/system_ext/etc/r94-native/module-delivery/delivery.sh','delivery.sh');s=delivery.read_text(encoding='utf-8')
s=s.replace('r94_foreground_schedtune r94_bili_native_rules r94_privacy_password_test','r94_foreground_schedtune r94_privacy_password_test')
block='''        bili=/data/adb/modules/r94_bili_native_rules
        if test -f "$bili/module.prop" && test ! -e "$bili/disable" && test ! -e "$bili/remove"; then
            nohup sh "$bili/service.sh" 8>&- >/dev/null 2>&1 </dev/null &
        fi
''';assert s.count(block)==1;s=s.replace(block,'        # Bili/WeChat rules are native ROM configuration; no rules watcher.\n');delivery.write_text(s,encoding='utf-8',newline='\n')
for device,name in [('/system_ext/etc/r91-rom/SHA256SUMS','rom-SHA256SUMS'),('/system_ext/etc/r94-native/module-delivery/SHA256SUMS','delivery-SHA256SUMS')]:capture(device,name)
# These checksums cover code changes, without copying any account or app data.
for filename,mapping in [('rom-SHA256SUMS',{'apply.sh':sha(apply),'../r94-native/module-delivery/delivery.sh':sha(delivery)}),('delivery-SHA256SUMS',{'delivery.sh':sha(delivery)})]:
 f=P/filename;rows=[];seen=set()
 for line in f.read_text(encoding='utf-8').splitlines():
  h,name=line.split(None,1);name=name.strip()
  if name in mapping:h=mapping[name];seen.add(name)
  rows.append(h+'  '+name)
 assert seen==set(mapping),(filename,seen);f.write_text('\n'.join(rows)+'\n',encoding='utf-8',newline='\n')
inputs=[(pathlib.Path('work/systemui-caption-focus/SystemUI-caption-defer-candidate.apk'),'SystemUI.apk','56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928'),(pathlib.Path('work/bili-native-middle-width/oplus-services-bili-middle-width-compressed.jar'),'oplus-services.jar',new)]
for src,name,want in inputs:assert sha(src)==want;shutil.copyfile(src,P/name)
for name in ['sys_fantasy_window_managed','sys_full_orientation_managed']:
 src=pathlib.Path('work/native-window-patch')/(name+'-patched.xml');shutil.copyfile(src,P/(name+'.xml'))
changes={'system_a':{'/system/framework/oplus-services.jar':'oplus-services.jar','/my_product/etc/fantasy/sys_fantasy_window_managed.xml':'sys_fantasy_window_managed.xml','/my_product/etc/fantasy/sys_full_orientation_managed.xml':'sys_full_orientation_managed.xml'},'system_ext_a':{'/priv-app/SystemUI/SystemUI.apk':'SystemUI.apk','/etc/r91-rom/apply.sh':'apply.sh','/etc/r91-rom/SHA256SUMS':'rom-SHA256SUMS','/etc/r94-native/module-delivery/delivery.sh':'delivery.sh','/etc/r94-native/module-delivery/SHA256SUMS':'delivery-SHA256SUMS'}}
plan={'status':'PREPARING_VERIFIED_BASE_IMAGES','base_directory':str(BASE),'build_directory':str(R),'changes':changes,'double_wipe_authorized':True,'camera':'Current verified v7 retained; old temporary v8 not added','kernel':43,'systemui_native':True,'no_new_performance_trial':True,'payloads':{f.name:sha(f) for f in P.iterdir() if f.is_file()},'images':{}}
(O/'plan.json').write_text(json.dumps(plan,indent=2))
for name in changes:
 src=pathlib.Path('D:/TB371FC-release/v22b-firstboot-publication-build')/(name+'-candidate.img');dst=R/(name+'.img')
 want=next(x['sha256'] for x in manifest['logical_partitions'] if x['name']==name)
 if dst.exists():assert sha(dst)==want,'Existing image is no longer a clean baseline; do not re-clone automatically'
 else:
  print('COPYING_BASE',name,flush=True);h=hashlib.sha256()
  with src.open('rb') as f,dst.open('wb') as out:
   while b:=f.read(16<<20):h.update(b);out.write(b)
  assert h.hexdigest()==want
 assert sha(dst)==want
 plan['images'][name]={'path':str(dst),'base_sha256':want,'bytes':dst.stat().st_size};(O/'plan.json').write_text(json.dumps(plan,indent=2));print('BASE_IMAGE_VERIFIED',name,flush=True)
plan['status']='PAYLOADS_AND_INDEPENDENT_BASE_IMAGES_READY';(O/'plan.json').write_text(json.dumps(plan,indent=2));print('PREPARE_COMPLETE',flush=True)
