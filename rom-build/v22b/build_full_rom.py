"""Assemble and archive a new full private test ROM using original scripts."""
from pathlib import Path
import json,hashlib,shutil,copy,importlib.util,subprocess,datetime,zipfile
B=Path(__file__).parent.parent;O=B/'v22b-firstboot-publication-20261025';OLD=Path('D:/TB371FC-release/R94T-v22a-NATIVE-PEN-COMM-PRIVATE_TEST')
R=OLD.parent/'R94T-v22b-FIRSTBOOT-CAMERA-PRIVATE_TEST';Z=OLD.parent/'ColorOS16_TB371FC_R94T_v22b_20261025_PENDING_TEST.zip';T=Z.with_suffix('.zip.partial')
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
im=read(O/'image-result.json');assert im['state']=='V22B_NATIVE_FIRSTBOOT_CAMERA_ART_READBACK_LABELS_CLOSURES_FSCK_SHA_PASS_NOT_FLASHED'
base=read(OLD/'manifest.json');m=copy.deepcopy(base)
assert not R.exists() and not Z.exists() and not T.exists()
assert shutil.disk_usage(OLD.parent).free>40*(1<<30)
R.mkdir()
for directory in ['assets','drivers','scripts','tools','verification']:shutil.copytree(OLD/directory,R/directory)
for f in OLD.iterdir():
    if f.is_file() and f.name!='manifest.json':shutil.copyfile(f,R/f.name)
(R/'images').mkdir()
scripts={f.relative_to(OLD).as_posix():sha(f) for f in list(OLD.glob('*.cmd'))+list((OLD/'scripts').glob('*.ps1'))}
assert len(scripts)==7 and all(sha(R/f)==h for f,h in scripts.items())
for row in base['tools']+base['accessories']:assert sha(R/row['path'])==row['sha256']

spec=importlib.util.spec_from_file_location('lp','D:/TB371FC-work/continuation-20260925/tools/lp_probe.py');lp=importlib.util.module_from_spec(spec);spec.loader.exec_module(lp)
source=OLD/'images/super-R94.img';target=R/'images/super-R94.img'
with source.open('rb') as f:header=f.read(2<<20)
parts={p['name']:p for p in lp.parse_metadata(header,lp.parse_geometry(header))['partitions'] if p['size_bytes']}
oldparts={p['name']:p for p in base['logical_partitions']}
assert all(len(p['extents'])==1 and p['extents'][0]['source']==p['extents'][0]['type']==0 for p in parts.values())
original_hash=hashlib.sha256();target_hash=hashlib.sha256();partition_hashes={};cursor=0
print('ASSEMBLING_SUPER_FROM_VERIFIED_PARTITIONS',flush=True)
with source.open('rb') as f,target.open('wb') as out:
    for name,p in sorted(parts.items(),key=lambda kv:kv[1]['extents'][0]['target_data']):
        start=p['extents'][0]['target_data']*512
        while cursor<start:
            data=f.read(min(16<<20,start-cursor));assert data
            original_hash.update(data);target_hash.update(data);out.write(data);cursor+=len(data)
        old_hash=hashlib.sha256();new_hash=hashlib.sha256();left=p['size_bytes']
        replacement=Path(im['images'][name]['path']).open('rb') if name in im['images'] else None
        try:
            while left:
                olddata=f.read(min(16<<20,left));assert olddata
                original_hash.update(olddata);old_hash.update(olddata)
                data=replacement.read(len(olddata)) if replacement else olddata;assert len(data)==len(olddata)
                new_hash.update(data);target_hash.update(data);out.write(data);cursor+=len(data);left-=len(data)
            if replacement:assert not replacement.read(1)
        finally:
            if replacement:replacement.close()
        assert old_hash.hexdigest()==oldparts[name]['sha256']
        expected=im['images'][name]['sha256'] if name in im['images'] else oldparts[name]['sha256']
        assert new_hash.hexdigest()==expected
        partition_hashes[name]=expected;print('PARTITION_STREAM_PASS '+name,flush=True)
    while data:=f.read(16<<20):original_hash.update(data);target_hash.update(data);out.write(data);cursor+=len(data)
assert cursor==12884901888 and original_hash.hexdigest()==next(p['sha256'] for p in base['images'] if p['name']=='super')
assert target.stat().st_nlink==1
# Independent disk readback verifies the complete written file and each partition.
full=hashlib.sha256();cursor=0
with target.open('rb') as f:
    assert f.read(len(header))==header;f.seek(0)
    for name,p in sorted(parts.items(),key=lambda kv:kv[1]['extents'][0]['target_data']):
        start=p['extents'][0]['target_data']*512
        while cursor<start:
            data=f.read(min(16<<20,start-cursor));assert data;full.update(data);cursor+=len(data)
        h=hashlib.sha256();left=p['size_bytes']
        while left:
            data=f.read(min(16<<20,left));assert data;h.update(data);full.update(data);cursor+=len(data);left-=len(data)
        assert h.hexdigest()==partition_hashes[name]
    while data:=f.read(16<<20):full.update(data);cursor+=len(data)
assert cursor==12884901888 and full.hexdigest()==target_hash.hexdigest()
for row in m['images']:
    if row['name']=='super':row['sha256']=full.hexdigest()
    else:
        shutil.copyfile(OLD/row['path'],R/row['path']);assert sha(R/row['path'])==row['sha256']
assert next(p['sha256'] for p in m['images'] if p['name']=='boot')=='09d3c1bd67946575de8b0dad434f651e746747da2686fa227719142ad47cfbbe'
m['logical_partitions']=[{'name':n,'sha256':partition_hashes[n],'bytes':parts[n]['size_bytes']} for n in sorted(parts)]


C=B/'cold-start-camera-20261025'
m['label']='ColorOS16 TB371FC R94T-v22b 私有待测版（首启交付、ZUI系统相机与竖屏引导修正）'
m['based_on']='Sealed v22a with exact first-boot guard/cache publication fixes, same-signed native ZUI camera base and exact compressed update, scoped portrait RRO and standard ART background profile policy. Kernel43/vendor/accepted SystemUI and module payloads preserved.'
m['state']='OFFLINE_VERIFIED_DEVICE_PENDING'
m['clean_first_boot_tested']=m['device_runtime_verified']=False
m['user_requested_package_without_factory_reset_test']=False
m['validation_scope']='This exact v22b archive is offline verified. Component tests on kernel43 used temporary static native-equivalent overlays and a same-signed ZUI update; they are not a v22b clean-flash acceptance.'
m.pop('test_scope_v22a',None);m['test_scope_v22b']='verification/test-scope-v22b.json'
apk='0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e'
m['camera_media_compat']['APK']={'package':'com.zui.camera','sha256':apk,'version_code':160070001,'preinstalled':True,'manual_install_required':False,'system_base':'/system/app/ZuiCameraSeed/ZuiCameraSeed.apk','exact_full_update':'/system/etc/r94-camera-v7/ZuiCamera.apk.xz','delivery':'Existing post-setup native service, once-only verified PackageManager update. Same certificate preserves normal SYSTEM/UPDATED_SYSTEM_APP identity.','new_module_required':False}
m['camera_media_compat']['old_OpenCamera_removed']=True
m['camera_media_compat']['native_completion_fix']='MediaRecorderWrapper.onInfo only: completion OK/EOS is not an error merely because it preceded mStopping. Original onError and encoding validation remain.'
m['camera_media_compat']['kernel43_component_tests']={'camera1_front_back_JPEG':True,'camera2_front_back_JPEG':True,'camera2_front_back_720p_YUV':True,'system_default_handler_resolution':True,'implicit_video_front_back_RETURN_OK_audio_video_and_frame_decode':True,'explicit_photo_RETURN_OK':True,'clean_v22b_flash':False,'all_third_party_apps_or_real_video_calls':False}
m['native_pen_delivery']['publication_fix']={'prepare_domain':'existing u:r:magisk:s0','umask':'022','published_directories':'0755 root:root','published_APKs':'0644 root:root','labels':'Only ipe/ws payload children system_file; cache root/log retain existing shell_data_file rules.','readiness_after_metadata_verification':True,'extra_init_allow_or_label_expansion':False,'fresh_private_namespace_real_device_test':True,'new_full_image_firstboot_test':False}
m['firstboot_runtime_delivery_fix']={'old_guard_sha256':'e18e0e4df08b541b85c3e45b2be4de3af17ade1d21cdb4f8808b723d8d05a454','correct_exact_framework_sha256':'7ea250fb0b7b00830a48b6ad111c795dc3adfcbb0d7b8c5a261f63d309b29762','new_guard_and_checksum_closure_verified':True,'controlled_kernel43_boot_native_ready_exit0_and_five_default_modules_pass':True,'v22b_firstboot_pass':False}
m['portrait_wizard_fix']={'overlay_package':'com.tb371fc.r93.uifit.bootreg','qualifier':'w600dp-port','width_dp':180,'height_dp':130,'gap_dp':30,'existing_11_dimensions_preserved':True,'real_rotation0_visual_pass':True,'global_density_or_SystemUI_changes':False}
m['ART_background_policy']={'pm.dexopt.bg-dexopt':'speed-profile','pm.dexopt.install':'speed-profile','pm.dexopt.install-fast':'skip','new_polling_or_forced_whole_device_compilation':False,'cold_start_fully_resolved':False}
m['refresh_policy']['kernel43_finite_app_requests_rotations_and_sleep_wake_pass']=True
m['refresh_policy']['permanent_144_startup_lock_added']=False
m['refresh_policy']['cold_ABA_fixed144_clear_benefit']=False
m['test_ready']['camera']='Only ZUI camera is delivered. Camera1/Camera2 JPEG, 720p YUV and default photo/video contracts have component evidence on kernel43; front short 4K sample was slow. Exact ROM first boot and all calling apps remain pending.'
m['test_ready']['modules_ai']='Exact stale first-boot guard corrected; controlled native-service reboot restored all five default modules. Exact clean image first boot remains pending.'
m['test_ready']['third_party_jank']='Process-cold Perfetto trace collected. Native-library monitor waits and non-I/O mapping/fault waits remain; bounded fixed144 ABA showed no stable benefit. ART background policy corrected; no universal smoothness claim.'
m['limitations']=[
 'This exact v22b image/ZIP has not yet been clean-flashed. Native publication, first-boot package restoration and cross-device boot still require original-script physical acceptance.',
 'An actual automatic black-screen/reboot happened on v22a kernel43. Generic reboot reason and empty pstore do not establish its cause. Finite smoke tests do not prove that rare black screens are fixed.',
 'Current panel/driver exposes real 30/60/144 rates; no real1Hz exists. Physical120 still enumerates, and filtering tested policy paths is not exhaustive elimination of every120 path.',
 'Cold-start stutter remains under investigation. The standard background compilation change is not a measured immediate cure for native-library/memory-mapping waits.',
 'Camera call contracts passed bounded tests, not every third-party app/video call. One short front-camera HIGH request selected4K with low measured frame rate; lighting/longer capture and profile suitability remain to verify.',
 'Real pen writing/pressure/tilt/buttons/charging and paired-phone call/data/SMS/audio still need actual accessories/phone tests. Visible UI options and service recovery are not proof of these features.',
 'No user passwords, accounts, personal media, ADB keys or Wi-Fi credentials are included.'
]
V=R/'verification'
evidence=[(O/'image-result.json','v22b-image-result.json'),(O/'final-policy-image-result.json','v22b-final-policy-image.json'),(O/'cold-publication-scoped-labels-result.json','v22b-cold-publication.json'),(O/'existing-policy-publication-domain-check.json','v22b-existing-policy-domain.json'),(C/'completion-fix-v7/build-result.json','v22b-camera-source.json'),(C/'native-camera-delivery-test-result.json','v22b-camera-delivery-test.json'),(C/'third-party-direct-api-results.json','v22b-camera-API-tests.json'),(C/'third-party-yuv-preview-results.json','v22b-camera-YUV-tests.json')]
for src,name in evidence:shutil.copyfile(src,V/name)
camera_receipts={}
for lens in ['back','front']:
 src=C/('video-contract-v7-system-'+lens)/'third-party-explicit-video-result.json'
 camera_receipts[lens]=read(src)
(V/'v22b-camera-video-contracts.json').write_text(json.dumps({'implicit_default_system_camera':True,'tests':camera_receipts,'all_apps_accepted':False},indent=2),encoding='utf-8')
scope={'state':'V22B_COMPLETE_PRIVATE_CANDIDATE_CLEAN_FLASH_PENDING','kernel':43,'new_kernel_experiment':False,'original_seven_scripts':scripts,'v22a_clean_flash_performed_and_defects_found':True,'v22b_clean_flash_performed':False,'controlled_component_reboot_and_native_defaults_pass':True,'system_camera_identity_and_contract_components_pass':True,'scoped_portrait_actual_rotation0_visual_pass':True,'pen_cache_real_cold_generation_and_scoped_metadata_pass':True,'rare_black_screen_resolved':False,'cold_starts_universally_smooth':False,'real_1hz':False,'physical120_removed':False,'actual_pen_and_paired_phone_accepted':False}
(V/'test-scope-v22b.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2),encoding='utf-8')
# The camera is now restored by the ROM; remove the obsolete manual-install copy.
old_camera=R/'assets/camera/ZuiCamera-TB371FC-C16-candidate.apk'
assert old_camera.is_file() and sha(old_camera)=='beaa56d744387613661f198849679fd9963a66fc8efddeb38e5b76671db220bc'
old_camera.unlink()
camera_note=R/'assets/camera/安装说明.md'
camera_note.write_text('''# ZUI相机已随系统交付

首次进入桌面后会自动准备ZUI相机，不需要手动安装APK。原来的Open Camera已移除。

首次打开时，请本人决定协议和权限。拍照、录音及保存权限按实际用途开启；测试不需要定位权限。

已验证本机前后摄的基础图像流和系统拍照/录像返回。前摄短时4K录制帧率偏低仍需核对，全部第三方软件及真实视频通话没有逐一验收。
''',encoding='utf-8')
rootassets=R/'assets/root';rootassets.mkdir(exist_ok=True)
manager=Path('E:/TB371FC-ROM/workspaces/R7-R93/work/r93-magisk/Magisk-v30.7.apk')
assert manager.stat().st_size==11613864
shutil.copyfile(manager,rootassets/'Magisk-v30.7.apk')
(rootassets/'离线安装说明.md').write_text('清空刷入后若Magisk管理器提示联网，请安装同目录的完整Magisk30.7管理器。不要再次刷入其他magisk.zip。Shell/ADB授权由你本人决定。\n',encoding='utf-8')
m['offline_magisk_manager']={'path':'assets/root/Magisk-v30.7.apk','sha256':sha(rootassets/'Magisk-v30.7.apk'),'version':'30.7','auto_grant_root':False}
guide='''# TB371FC ColorOS16 R94T v22b 私有待测包

这版修正了清空后首次启动的交付问题：模块漏装、原生笔组件生成后的权限，以及竖屏导航引导卡片被裁切。内核仍是#43。

只保留ZUI移植相机。进入桌面后会自动准备相机，不再需要手装APK。修正第三方限时录像自动结束后被误判失败的问题；本机前后摄已能把测试录像返回原应用。前摄短时4K帧率偏低还需继续核对。

四扬、前台调度、AI控制、哔哩哔哩可移动双窗、隐私密码，以及已满意的经典/分离通知布局和负一屏继续保留。后台预编译改为按使用热点优化。冷启动偶发卡顿和黑屏仍未根治，真实手写笔和手机通信共享仍需联测。

当前面板没有真实1Hz。已适配30/60/144的刷新策略，120物理模式仍存在，不能写成所有路径都完全移除120。测试中没有发现短时强锁144能稳定改善冷启动，因此没有加入常驻强锁策略。

本机#43下的等效组件测试通过，不代表这份新整包已经清空实刷通过。整包先作为私有待测版，不作公开正式版。

仅适用于已解锁的TB371FC。刷入会删除应用、账号和个人文件，先备份。按包内原始入口依次执行“核验ROM”“1-连接检查”“2-刷前检查”“清空数据刷入”；七份脚本保持不变。出错时保留attempt-logs中的记录，不跳过检查，不安装供体OTA，也不要重新锁定。

如果Magisk管理器要求联网，assets/root内已附完整30.7离线安装包；是否授权Root由本人决定。相机首次协议及权限也由本人决定。
'''
(R/'刷入说明.md').write_text(guide,encoding='utf-8')
accessories={x['path']:x for x in m['accessories'] if x['path']!='assets/camera/ZuiCamera-TB371FC-C16-candidate.apk'}
files=[V/name for _,name in evidence]+[V/'v22b-camera-video-contracts.json',V/'test-scope-v22b.json',R/'刷入说明.md',camera_note,*rootassets.iterdir()]
for f in files:
 rel=f.relative_to(R).as_posix();accessories[rel]={'path':rel,'sha256':sha(f)}
m['accessories']=list(accessories.values())
(R/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(sha(R/p)==h for p,h in scripts.items())
assert all((R/row['path']).is_file() and sha(R/row['path'])==row['sha256'] for row in m['accessories'])
print('V22B_NATIVE_IMAGES_CAMERA_OFFLINE_MANAGER_ORIGINAL_SCRIPTS_READY',flush=True)
q=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(R/'scripts/Invoke-R91-Clean.ps1')],capture_output=True,timeout=600)
(O/'original-offline-entry.txt').write_bytes(q.stdout+q.stderr);assert not q.returncode,(q.stdout+q.stderr)
print('ORIGINAL_PACKAGE_OFFLINE_ENTRY_PASS',flush=True)
expected={}
image_hashes={p['path']:p['sha256'] for p in m['images']}
for f in sorted(R.rglob('*')):
    if f.is_file():
        rel=f.relative_to(R).as_posix();expected[rel]=image_hashes[rel] if rel in image_hashes else sha(f)
with zipfile.ZipFile(T,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
    for rel,want in expected.items():
        h=hashlib.sha256();info=zipfile.ZipInfo(rel);info.compress_type=zipfile.ZIP_DEFLATED;info._compresslevel=1
        info.external_attr=(0o100755 if rel.endswith(('.sh','.cmd','.ps1','.exe')) else 0o100644)<<16
        with (R/rel).open('rb') as f,z.open(info,'w',force_zip64=True) as dest:
            while data:=f.read(8<<20):h.update(data);dest.write(data)
        assert h.hexdigest()==want,rel
        if rel.startswith('images/'):print('ARCHIVE_IMAGE_STREAMED '+rel,flush=True)
with zipfile.ZipFile(T) as z:
    assert len(z.namelist())==len(set(z.namelist())) and set(z.namelist())==set(expected)
    for rel,want in expected.items():
        with z.open(rel) as f:h=hashlib.file_digest(f,'sha256').hexdigest()
        assert h==want,rel
print('ALL_ZIP_MEMBER_SHA256_AND_CRC_PASS',flush=True)
h=sha(T);T.rename(Z);Z.with_suffix('.zip.sha256').write_text(h+'  '+Z.name+'\n',encoding='utf-8')
result={'state':'V22B_COMPLETE_FIRSTBOOT_CAMERA_PRIVATE_ZIP_ORIGINAL_ENTRY_SHA_CRC_PASS_NOT_FLASHED','time':datetime.datetime.now().astimezone().isoformat(),'directory':str(R),'archive':str(Z),'sha256':h,'bytes':Z.stat().st_size,'members':len(expected),'super_sha256':full.hexdigest(),'logical_partition_hashes':partition_hashes,'original_seven_scripts_unchanged':scripts,'kernel43_boot_unchanged':True,'systemUI_and_accepted_seed_payloads_preserved':True,'full_clean_flash_and_first_boot_pass':False,'device_actions':0,'not_public_release':True}
(O/'archive-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False),flush=True)
