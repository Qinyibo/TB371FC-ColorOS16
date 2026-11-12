"""Assemble a local v26/r104 candidate with the unchanged offline flash tools."""
import copy
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
BUILD = pathlib.Path(sys.argv[1]).resolve()
WORKSPACE = pathlib.Path(sys.argv[2]).resolve()
BASE = pathlib.Path('D:/TB371FC-release/R94T-v25-r102-20261102-CANDIDATE-animation-default-r1-freezer-fallback-r1')
result = json.loads((BUILD / 'image-result.json').read_text(encoding='utf-8'))
animation_default_r1 = result.get('animation_default_r1', False)
freezer_fallback_r1 = result.get('freezer_fallback_r1', False)
suffix = ('-animation-default-r1' if animation_default_r1 else '') + ('-freezer-fallback-r1' if freezer_fallback_r1 else '')
OUT = BASE.parent / 'R94T-v26-r104-20261103-CANDIDATE'
assert not OUT.exists(), 'Preserve any existing candidate; inspect before rebuilding.'
assert result['state'] == 'INDEPENDENT_IMAGES_READBACK_CLOSURE_FSCK_PASS'
plan=json.loads((BUILD/'plan.json').read_text())
framework_sha='a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136'
manifest = json.loads((BASE / 'manifest.json').read_text(encoding='utf-8-sig'))
original = copy.deepcopy(manifest)
def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()
OUT.mkdir()
for name in ['assets', 'drivers', 'scripts', 'tools', 'verification']:
    shutil.copytree(BASE / name, OUT / name)
for source in BASE.iterdir():
    if source.is_file() and source.name != 'manifest.json': shutil.copyfile(source, OUT / source.name)
(OUT / 'images').mkdir()
scripts = {p.relative_to(BASE).as_posix(): sha(p) for p in [*BASE.glob('*.cmd'), *(BASE / 'scripts').glob('*.ps1')]}
assert len(scripts) == 7
spec = importlib.util.spec_from_file_location('lp', 'D:/TB371FC-work/continuation-20260925/tools/lp_probe.py')
lp = importlib.util.module_from_spec(spec); spec.loader.exec_module(lp)
source = BASE / 'images/super-R94.img'
with source.open('rb') as stream: header = stream.read(2 << 20)
parts = {p['name']: p for p in lp.parse_metadata(header, lp.parse_geometry(header))['partitions'] if p['size_bytes']}
assert all(len(p['extents']) == 1 and p['extents'][0]['source'] == p['extents'][0]['type'] == 0 for p in parts.values())
base_parts = {p['name']: p for p in manifest['logical_partitions']}
old_full = hashlib.sha256(); new_full = hashlib.sha256(); partition_hashes = {}; cursor = 0
with source.open('rb') as inp, (OUT / 'images/super-R94.img').open('wb') as dest:
    for name, part in sorted(parts.items(), key=lambda kv: kv[1]['extents'][0]['target_data']):
        start = part['extents'][0]['target_data'] * 512
        while cursor < start:
            data = inp.read(min(16 << 20, start - cursor)); assert data
            old_full.update(data); new_full.update(data); dest.write(data); cursor += len(data)
        replacement = pathlib.Path(result['images'][name]['path']).open('rb') if name in result['images'] else None
        old_hash = hashlib.sha256(); new_hash = hashlib.sha256(); left = part['size_bytes']
        try:
            while left:
                before = inp.read(min(16 << 20, left)); assert before
                after = replacement.read(len(before)) if replacement else before
                assert len(after) == len(before)
                old_full.update(before); old_hash.update(before); new_full.update(after); new_hash.update(after)
                dest.write(after); left -= len(after); cursor += len(after)
            if replacement: assert not replacement.read(1)
        finally:
            if replacement: replacement.close()
        assert old_hash.hexdigest() == base_parts[name]['sha256'], name
        assert new_hash.hexdigest() == (result['images'][name]['sha256'] if name in result['images'] else base_parts[name]['sha256']), name
        partition_hashes[name] = new_hash.hexdigest()
        print('SUPER_PARTITION_VERIFIED', name, flush=True)
    while data := inp.read(16 << 20):
        old_full.update(data); new_full.update(data); dest.write(data); cursor += len(data)
assert cursor == 12884901888
assert old_full.hexdigest() == next(r['sha256'] for r in original['images'] if r['name'] == 'super')
for row in manifest['images']:
    if row['name'] == 'super': row['sha256'] = new_full.hexdigest()
    elif row['name'] == 'boot':
        src = BUILD / 'payloads/boot_a.img'
        assert sha(src) == 'f29c32c15c7276d777f243a322ca35495099c25d6e41e402dd4eacb77121f85b'
        shutil.copyfile(src, OUT / row['path']); row['sha256'] = sha(src)
    else:
        shutil.copyfile(BASE / row['path'], OUT / row['path'])
        assert sha(OUT / row['path']) == row['sha256']
manifest['logical_partitions'] = [dict(name=n, sha256=partition_hashes[n], bytes=parts[n]['size_bytes']) for n in sorted(parts)]
# Current v26 acceptance is separate from inherited v25 component history.
manifest.update(label='ColorOS16 TB371FC v26 r104 本地候选',state='OFFLINE_VERIFIED_DEVICE_PENDING',based_on='Exact v25/r102 animation-default/freezer baseline, r103 get_signal freezer exit fix, r104 dead-panel recovery contract, universal cancelled-task snapshot mapping, six promotional preload removals.',clean_first_boot_tested=False,device_runtime_verified=False,release_channel='local_candidate_not_published')
manifest['kernel']=dict(build='#43 r104-panel-recovery',image_sha256=plan['kernel_image_sha256'],source_commit=plan['kernel_commit'],local_git_ref=plan['kernel_ref'],speaker_native_api=19,physical_tested=True,physical_test_scope='Existing component normal boot and user-confirmed display restored; exceptional dead-panel rail recovery not yet observed. INIT=0x9D root cause NOT proven fixed.')
manifest['v26_changes']=dict(kernel_ref=plan['kernel_ref'],freezer_signal_group_exit_fixed=True,universal_cancel_snapshot_mapping=True,systemui_sha256=plan['changes'][0]['sha256'],preloads_removed=result['removed_preloads'],capsule_user_accepted=True,capsule_diagnostic_and_rejected_prototypes_included=False,usb_source_changed=False,black_screen_root_cause_fixed=False,keyboard_candidate_included=False,exact_archive_clean_flash_tested=False)
manifest['validation_scope']='Offline image readback, original startup checksums, file labels/modes, filesystem checks, full-super partition hashes and archive-member verification. Device installation and USB/display observations have separate receipts; do not inherit full-device success from v25.'
manifest['test_scope_v26']='verification/test-scope-v26.json'
manifest['limitations']=['USB bulk-transfer/bootloader stability remains unresolved; recovery installation does not prove USB repaired.','r104 restores the existing dead-panel power-cycle contract; INIT=0x9D root cause and long-idle recovery remain unproven.','Universal snapshot mapping corrected; black-bar visual acceptance remains user manual testing.','This exact candidate is not yet clean-flash or accessory/long-duration hardware qualified.']
guide='''# TB371FC ColorOS16 v26 r104 本地候选

保留已确认的动画效果与原有四扬等适配，整合冻结退出修复、死屏时的供电恢复契约修正，以及通用取消动画的任务截图编号修正。临时计时、异步统计和未获益的加载器试验均不包含。

精简六项推广预装：阅读、游戏推荐、游戏中心、社区、商城、会员推广。保留输入法、浏览器、文件管理、相册、账号、应用市场、互联与系统硬件服务。

USB 稳定性尚未修复。r104 不是 INIT=0x9D 根因修复，不承诺已根治黑屏。完整包刷入、启动和 USB/显示观察见另附实机记录；本文件的离线生成不代表实机通过。汽水效果由用户确认可用，黑条仍由用户手测。

只用于已解锁 TB371FC，不重新锁定。原七个刷入入口保持字节一致；本机 USB 下载异常时使用已验证的 Recovery 离线写入路径。保留电脑端 v25 完整包作为回退。清空数据入口会删除数据，按实际需要选择。
'''
guide_path=OUT/'刷入说明.md';guide_path.write_text(guide,encoding='utf-8')
verification=OUT/'verification';new_files=[guide_path]
scope=dict(exact_archive_clean_flash_pass=False,device_modified_by_packaging=False,capsule_user_accepted=True,usb_fixed=False,black_screen_root_cause_fixed=False,black_bar_device_retest=False,diagnostic_apk_included=False)
for name,data in [('v26-image-result.json',result),('test-scope-v26.json',scope),('v26-plan.json',plan)]:
 path=verification/name;path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');new_files.append(path)
for name in ['r104-panel-recovery.git.patch','r104-git-record.json']:
 path=verification/name;shutil.copyfile(WORKSPACE/'outputs/display-recovery-r104'/name,path);new_files.append(path)
for name in ['r103-signal-exit.git.patch','r103-git-record.json']:
 path=verification/name;shutil.copyfile(WORKSPACE/'outputs/douyin-startup'/name,path);new_files.append(path)
cancel_source=pathlib.Path(__file__).resolve().parents[2]/'native-animation/cancel-snapshots-r1'
cancel_out=verification/'cancel-snapshots-r1-source';cancel_out.mkdir()
for source in sorted(cancel_source.iterdir()):
 if source.is_file() and source.suffix in ('.java','.py','.md','.json'):
  path=cancel_out/source.name;shutil.copyfile(source,path);new_files.append(path)
source_dir=verification/'v26-build-source';source_dir.mkdir()
for name in ['prepare.py','build_images.py','package_rom.py','archive.py']:
 path=source_dir/name;shutil.copyfile(pathlib.Path(__file__).parent/name,path);new_files.append(path)
accessories={r['path']:r for r in manifest['accessories']}
for path in new_files:
 relative=path.relative_to(OUT).as_posix();accessories[relative]=dict(path=relative,sha256=sha(path))
manifest['accessories']=list(accessories.values())
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(sha(OUT/path)==digest for path,digest in scripts.items())
p=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(OUT/'scripts/Invoke-R91-Clean.ps1')],capture_output=True,timeout=900)
(BUILD/'original-offline-entry.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,(p.stdout+p.stderr)[-2500:]
receipt=dict(state='CANDIDATE_ASSEMBLED_ORIGINAL_OFFLINE_ENTRY_PASS',directory=str(OUT),base=str(BASE),exact_full_archive_clean_flash_pass=False,original_seven_scripts=scripts,image_hashes={r['path']:r['sha256'] for r in manifest['images']},super_bytes=cursor,base_super_verified=True,lp_metadata_and_layout_preserved=True,changed_logical_partitions=['system_a','system_ext_a'],removed_preloads=result['removed_preloads'])
(BUILD/'package-result.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print('V26_PACKAGE_READY',OUT,flush=True)
