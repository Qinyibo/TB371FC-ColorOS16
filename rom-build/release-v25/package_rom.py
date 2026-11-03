"""Assemble a local v25/r102 candidate with the unchanged offline flash tools."""
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
BASE = pathlib.Path('D:/TB371FC-release/R94T-v24-20261101-TEST')
result = json.loads((BUILD / 'image-result.json').read_text(encoding='utf-8'))
animation_default_r1 = result.get('animation_default_r1', False)
freezer_fallback_r1 = result.get('freezer_fallback_r1', False)
suffix = ('-animation-default-r1' if animation_default_r1 else '') + ('-freezer-fallback-r1' if freezer_fallback_r1 else '')
OUT = BASE.parent / ('R94T-v25-r102-20261102-CANDIDATE' + suffix)
assert not OUT.exists(), 'Preserve any existing candidate; inspect before rebuilding.'
assert result['state'] == 'INDEPENDENT_IMAGES_READBACK_CLOSURE_FSCK_PASS'
framework_sha = next(r['sha256'] for r in result['changes'] if r['target'] == '/system/framework/oplus-services.jar')
assert framework_sha == ('a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136' if freezer_fallback_r1 else 'e73be401835ecede505e6c37c75c007a8f5bd840d9441fe0a99b3f5320c3e3a9')
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
        assert sha(src) == '1d84543e6e3c026aaf0560e79c45f73a90c7e2efa7dc876c4395022ccbbaa9e9'
        shutil.copyfile(src, OUT / row['path']); row['sha256'] = sha(src)
    else:
        shutil.copyfile(BASE / row['path'], OUT / row['path'])
        assert sha(OUT / row['path']) == row['sha256']
manifest['logical_partitions'] = [dict(name=n, sha256=partition_hashes[n], bytes=parts[n]['size_bytes']) for n in sorted(parts)]
manifest.update(label='ColorOS16 TB371FC R94T v25 r102 本地候选',
    based_on='Exact verified v24 images plus reviewed r102 kernel, optional charger-query version guard, opt-in WLAN diagnostics and no autostart for undeclared factory helper.',
    state='OFFLINE_VERIFIED_DEVICE_PENDING', clean_first_boot_tested=False, device_runtime_verified=False,
    release_channel='local_candidate_not_published',
    validation_scope='Changed components have scoped device evidence; these exact full images/archive have NOT been clean-flashed. Offline checks do not establish first-boot or all-hardware acceptance.')
manifest.pop('test_scope_v24', None)
manifest.pop('user_requested_package_without_factory_reset_test', None)
manifest['test_scope_v25'] = 'verification/test-scope-v25.json'
manifest['firstboot_runtime_delivery_fix']['correct_exact_framework_sha256'] = framework_sha
manifest['kernel'] = dict(build='#43 r102-batt-avg', image_sha256='88c89d140042fe5103bd7ac7c516cb8b35a4e77af9ba26de1873197114bd8c43',
    local_git_ref='local/r102-reviewed', source_commit='d981748399d68a57bcbe5faeb25c196589d9bc9c', speaker_native_api=19,
    change='Retains r97 touch/display diagnostics, r98/r99 DSP fixes; adds normalized battery CURRENT_AVG. Unaccepted r100 keyboard candidate excluded.',
    physical_tested=True, physical_test_scope='Normal component boot and live Health average-current read-path verified; no whole-ROM clean-flash, full charging cycle or wake acceptance.')
manifest['v25_changes'] = dict(kernel_ref='local/r102-reviewed', keyboard_candidate_included=False,
    framework_sha256=framework_sha,
    native_startup_checksum_chain_updated=True, wlan_diagnostic_opt_in=True, undeclared_factory_helper_autostart=False,
    speaker_binaries_unchanged=True, layout_and_flash_scripts_unchanged=True, exact_archive_clean_flash_tested=False)
if animation_default_r1:
    manifest['v25_changes']['animation_default_r1'] = True
    manifest['label'] += ' animation-default-r1'
    manifest['based_on'] += ' Factory animation default4 at the authoritative my_manifest property layer.'
if freezer_fallback_r1:
    manifest['v25_changes']['freezer_fallback_r1'] = True
    manifest['label'] += ' freezer-fallback-r1'
    manifest['based_on'] += ' Uses existing Android cached freezing when HANS is not ready; quota and ready-HANS paths retained.'
manifest['inherited_component_notes_scope'] = 'Retained versioned feature notes and old verification files are historical v24/source evidence. Current candidate identity and acceptance are v25_changes, kernel.physical_test_scope and test_scope_v25; none upgrades an earlier feature to full-device acceptance.'
manifest['limitations'][0] = 'This exact v25/r102 image/archive has not been clean-flashed; first-boot, accessory and cross-device acceptance remain unproven.'
manifest['test_ready']['communication'] = 'v24/v17 oneshot baseline preserved; no phone shared-data/call/SMS acceptance added.'
manifest['test_ready']['battery_average'] = 'r102 component boot and actual HAL battery/current_avg path passed; full charge/discharge and power calibration untested.'
guide = '''# TB371FC ColorOS16 v25 r102 本地候选

以v24为基线，整合已分别验证的后续修改：r102内核（含显示/触控诊断、音频DSP回复与会话归属修正、平均电流方向修正），旧充电接口兼容，以及无线诊断按需启动、未声明工厂服务停止自动重试。原动画、四扬、相机、笔、通信和布局载荷保持基线。键盘候选未包含。

本完整包只完成离线镜像与文件检查，尚未用它双清刷入。组件启动通过不能替代首启验收；双击亮屏、长待机、真笔、键盘、手机通信及完整充放电仍有未验收项。不宣称独立四声道或续航改善。

仅供已解锁TB371FC本地评审。刷入入口与v24一致，执行清空数据刷入会删除数据；本次构建没有执行刷机或清空操作，也没有发布。勿混用其他包镜像、勿重新锁定。此前r6/v24是回退基线，不要把旧验证文件当成本候选整包的实机结论。
'''
if animation_default_r1:
    guide += '\n本变体 animation-default-r1 另将 /my_manifest/build.prop 的出厂动画默认值改为4。原用户持久化选择仍有优先级；该新变体的整包验收不得沿用原v25的实机记录。\n'
if freezer_fallback_r1:
    guide += '\n本变体 freezer-fallback-r1 修复 HANS 未就绪时缓存应用仅虚拟冻结的问题。组件实机冻结、广播解冻和前台服务生命周期已通过；完整包首启、消息推送与媒体兼容、离线待机收益仍需各自验证。\n'
guide_path = OUT / '刷入说明.md'; guide_path.write_text(guide, encoding='utf-8')
verification = OUT / 'verification'
new_files = [guide_path]
if freezer_fallback_r1:
    target = verification / 'freezer-component-validation-20261102.json'
    source = pathlib.Path(__file__).resolve().parents[2] / 'native-freezer/validation-20261102.json'
    data = json.loads(source.read_text(encoding='utf-8'))
    assert data['framework_after'] == framework_sha
    shutil.copyfile(source, target)
    new_files.append(target)
    source_dir = source.parent
    preserved = verification / 'freezer-fallback-r1-source'
    preserved.mkdir()
    for filename in ['FreezerFallbackPatch.java', 'build.py', 'prepare_overlay.py', 'README.md']:
        target = preserved / filename
        shutil.copyfile(source_dir / filename, target)
        new_files.append(target)
for filename, data in [('v25-image-result.json', result), ('test-scope-v25.json', dict(exact_full_archive_clean_flash_pass=False, device_modified_by_packaging=False,
    r102_component_runtime_verified=True, charger_guard_component_runtime_verified=True, wake_tests_not_run=True,
    freezer_fallback_r1_included=freezer_fallback_r1, freezer_component_runtime_verified=freezer_fallback_r1,
    independent_quad_claimed=False, pen_keyboard_phone_acceptance_added=False, source_scope='retained historical verification files describe their named earlier builds, not this exact archive'))]:
    path = verification / filename; path.write_text(json.dumps(data, indent=2), encoding='utf-8'); new_files.append(path)
for filename in ['r102-current-average.git.patch', 'r102-git-record.json']:
    target = verification / filename; shutil.copyfile(WORKSPACE / 'outputs/battery-telemetry' / filename, target); new_files.append(target)
target = verification / 'r99-local-series.patch'
shutil.copyfile(WORKSPACE / 'outputs/TB371FC_r99_local_series.patch', target); new_files.append(target)
accessories = {r['path']: r for r in manifest['accessories']}
for path in new_files:
    relative = path.relative_to(OUT).as_posix(); accessories[relative] = dict(path=relative, sha256=sha(path))
manifest['accessories'] = list(accessories.values())
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert all(sha(OUT / path) == digest for path, digest in scripts.items())
# No Execute/CheckDevice flags: the original entry returns after file hashes.
p = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(OUT / 'scripts/Invoke-R91-Clean.ps1')], capture_output=True, timeout=900)
(BUILD / 'original-offline-entry.log').write_bytes(p.stdout + p.stderr)
assert p.returncode == 0, (p.stdout + p.stderr)[-2500:]
receipt = dict(state='CANDIDATE_ASSEMBLED_ORIGINAL_OFFLINE_ENTRY_PASS', directory=str(OUT), base=str(BASE),
    animation_default_r1=animation_default_r1,
    freezer_fallback_r1=freezer_fallback_r1,
    exact_full_archive_clean_flash_pass=False, original_seven_scripts=scripts,
    image_hashes={r['path']: r['sha256'] for r in manifest['images']}, super_bytes=cursor,
    base_super_verified=True, lp_metadata_and_layout_preserved=True, changed_logical_partitions=list(result['images']))
(BUILD / 'package-result.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print('ORIGINAL_OFFLINE_ENTRY_PASS_LOCAL_CANDIDATE_READY', OUT, flush=True)
