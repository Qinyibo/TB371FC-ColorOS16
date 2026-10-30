"""Assemble v23 with the original seven flash entry points, then verify/archive."""
from pathlib import Path
import sys,json,hashlib,shutil,importlib.util,subprocess,zipfile,copy
sys.stdout.reconfigure(encoding='utf-8')
O=Path(__file__).resolve().parent;B=Path('D:/TB371FC-release/R94T-v22b-FIRSTBOOT-CAMERA-PRIVATE_TEST')
R=B.parent/'R94T-v23-20261030-TEST';Z=B.parent/'ColorOS16_TB371FC_R94T_v23_20261030_TEST.zip'
im=json.loads((O/'image-result.json').read_text(encoding='utf-8'));assert im['status']=='IMAGES_EDITED_READBACK_CHECKSUM_CLOSURE_FSCK_PASS'
m=json.loads((B/'manifest.json').read_text(encoding='utf-8-sig'));base=copy.deepcopy(m)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert not R.exists() and not Z.exists();R.mkdir()
for name in ['assets','drivers','scripts','tools','verification']:shutil.copytree(B/name,R/name)
for f in B.iterdir():
 if f.is_file() and f.name!='manifest.json':shutil.copyfile(f,R/f.name)
(R/'images').mkdir()
scripts={f.relative_to(B).as_posix():sha(f) for f in [*B.glob('*.cmd'),*(B/'scripts').glob('*.ps1')]};assert len(scripts)==7
spec=importlib.util.spec_from_file_location('lp','D:/TB371FC-work/continuation-20260925/tools/lp_probe.py');lp=importlib.util.module_from_spec(spec);spec.loader.exec_module(lp)
src=B/'images/super-R94.img';dst=R/'images/super-R94.img'
with src.open('rb') as f:header=f.read(2<<20)
parts={p['name']:p for p in lp.parse_metadata(header,lp.parse_geometry(header))['partitions'] if p['size_bytes']}
assert all(len(p['extents'])==1 and p['extents'][0]['source']==p['extents'][0]['type']==0 for p in parts.values())
base_parts={p['name']:p for p in m['logical_partitions']};old_full=hashlib.sha256();new_full=hashlib.sha256();part_hashes={};cursor=0
print('ASSEMBLING_NEW_SUPER',flush=True)
with src.open('rb') as f,dst.open('wb') as out:
 for name,part in sorted(parts.items(),key=lambda kv:kv[1]['extents'][0]['target_data']):
  start=part['extents'][0]['target_data']*512
  while cursor<start:
   data=f.read(min(16<<20,start-cursor));assert data;old_full.update(data);new_full.update(data);out.write(data);cursor+=len(data)
  replacement=Path(im['images'][name]['path']).open('rb') if name in im['images'] else None
  old_hash=hashlib.sha256();new_hash=hashlib.sha256();left=part['size_bytes']
  try:
   while left:
    original=f.read(min(16<<20,left));assert original;data=replacement.read(len(original)) if replacement else original;assert len(data)==len(original)
    old_full.update(original);old_hash.update(original);new_full.update(data);new_hash.update(data);out.write(data);left-=len(data);cursor+=len(data)
   if replacement:assert not replacement.read(1)
  finally:
   if replacement:replacement.close()
  assert old_hash.hexdigest()==base_parts[name]['sha256'],name
  assert new_hash.hexdigest()==(im['images'][name]['sha256'] if name in im['images'] else base_parts[name]['sha256']),name
  part_hashes[name]=new_hash.hexdigest();print('ASSEMBLED',name,flush=True)
 while data:=f.read(16<<20):old_full.update(data);new_full.update(data);out.write(data);cursor+=len(data)
assert cursor==12884901888 and old_full.hexdigest()==next(x['sha256'] for x in base['images'] if x['name']=='super')
for row in m['images']:
 if row['name']=='super':row['sha256']=new_full.hexdigest()
 else:shutil.copyfile(B/row['path'],R/row['path']);assert sha(R/row['path'])==row['sha256']
m['logical_partitions']=[{'name':n,'sha256':part_hashes[n],'bytes':parts[n]['size_bytes']} for n in sorted(parts)]
m.update(label='ColorOS16 TB371FC R94T v23 测试版',based_on='Verified v22b kernel43/vendor/camera7 plus retained focus-aware caption patch, native WeChat/Bili source configuration, narrower Bili home and repaired startup checksum chain.',state='OFFLINE_VERIFIED_DEVICE_PENDING',clean_first_boot_tested=False,device_runtime_verified=False,validation_scope='New v23 images: file readback, metadata, checksum closure and filesystem checks completed. Exact archive clean-flash and smoothness acceptance pending.')
m.pop('test_scope_v22b',None);m['test_scope_v23']='verification/test-scope-v23.json'
m['firstboot_runtime_delivery_fix']['correct_exact_framework_sha256']='ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467'
m['defaults']['automatic_split_recommendations']=False
m['v23_changes']={'native_caption_patch_sha256':'56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928','native_framework_sha256':'ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467','native_parallel_config_for_wechat_bili':True,'bili_center_home_width_2944x1840':1149,'bili_rules_watcher_default_install_removed':True,'launcher_speed_compile_once':True,'startup_base_guard_and_two_checksum_lists_updated':True,'new_kernel_or_gc_scheduling_trial':False,'camera_version7_matches_current_device':True}
m['v23_changes']['native_init_magisk_domain_after_manager_initialization']=True
m['v23_changes']['native_init_rc_sha256']='85739a5112d7c096ed72bc2bff8337de29b6ed90671eea1b05c8d8652bbef750'
guide='''# TB371FC ColorOS16 R94T v23 测试版

相对 v17 的后续系统修正整合到本包，内核保留 #43、相机保留当前使用的 v7。

本次加入已保留的辅助触摸层延后创建与失焦取消、原生微信/B站平行视窗配置和缩窄的B站首页，关闭自动分屏推荐，保留144Hz、正常动画与模糊。修正框架更新后首启脚本仍校验旧版本导致提前退出的问题；双清后自动准备桌面 speed 编译。旧B站规则维护模块不再默认安装。

修正系统初始化服务残留的KernelSU运行域，改用本包现有Magisk运行域，避免Magisk环境初始化后正常重启时服务无法启动。

流畅度仍有残余掉帧；本包不是“卡顿、黑屏、全部硬件问题已根治”的承诺。相机后摄录像帧率、真实笔与手机通信共享仍有待验证项。

仅用于已解锁的联想 TB371FC。双清会删除应用、账号和个人文件。按原入口依次运行“核验ROM”“1-连接检查”“2-刷前检查”“清空数据刷入”。不得混用其他包镜像、不得重新锁定。

首次引导、相机权限及Magisk授权由本人决定。assets/root 内保留离线管理器。普通用户无需了解内部实现即可使用系统功能。
'''
(R/'刷入说明.md').write_text(guide,encoding='utf-8')
V=R/'verification'
(V/'v23-image-result.json').write_text(json.dumps(im,ensure_ascii=False,indent=2),encoding='utf-8')
(V/'test-scope-v23.json').write_text(json.dumps({'state':'V23_OFFLINE_IMAGE_VERIFIED_PHYSICAL_PENDING','original_seven_scripts':scripts,'double_wipe_authorized':True,'clean_flash_pass':False,'smoothness_user_accepted':False,'paired_phone_and_pen_hardware_verified':False},indent=2),encoding='utf-8')
accessories={r['path']:r for r in m['accessories']}
for f in [R/'刷入说明.md',V/'v23-image-result.json',V/'test-scope-v23.json']:
 rel=f.relative_to(R).as_posix();accessories[rel]={'path':rel,'sha256':sha(f)}
m['accessories']=list(accessories.values());(R/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(sha(R/n)==h for n,h in scripts.items())
print('VERIFYING_WITH_ORIGINAL_OFFLINE_ENTRY',flush=True)
q=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(R/'scripts/Invoke-R91-Clean.ps1')],capture_output=True,timeout=900)
(O/'original-offline-entry.log').write_bytes(q.stdout+q.stderr);assert q.returncode==0,(q.stdout+q.stderr)[-4000:]
print('ORIGINAL_OFFLINE_ENTRY_PASS',flush=True)
expected={};known={x['path']:x['sha256'] for x in m['images']}
for f in sorted(R.rglob('*')):
 if f.is_file():
  rel=f.relative_to(R).as_posix();expected[rel]=known[rel] if rel in known else sha(f)
temporary=Z.with_suffix('.zip.partial')
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as archive:
 for rel,want in expected.items():
  h=hashlib.sha256()
  with (R/rel).open('rb') as f,archive.open(rel,'w',force_zip64=True) as out:
   while data:=f.read(8<<20):h.update(data);out.write(data)
  assert h.hexdigest()==want
  if rel.startswith('images/'):print('ARCHIVED',rel,flush=True)
with zipfile.ZipFile(temporary) as archive:
 assert len(archive.namelist())==len(set(archive.namelist())) and set(archive.namelist())==set(expected)
 for rel,want in expected.items():
  with archive.open(rel) as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
  assert actual==want,rel
temporary.replace(Z);digest=sha(Z);Z.with_suffix('.zip.sha256').write_text(digest+'  '+Z.name+'\n',encoding='ascii')
result={'status':'OFFLINE_PACKAGE_SHA_CRC_ORIGINAL_ENTRY_PASS_READY_FOR_CLEAN_FLASH','directory':str(R),'archive':str(Z),'sha256':digest,'bytes':Z.stat().st_size,'members':len(expected),'double_wipe_authorized':True,'physical_flash_pass':False,'github_published':False}
(O/'package-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
