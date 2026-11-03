"""Package the accepted v26 system with the deployed r106 boot; never flash."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding='utf-8')
WORKSPACE = Path(sys.argv[1]).resolve()
BUILD = Path(sys.argv[2]).resolve()
BASE = Path(sys.argv[3]).resolve()
OUT = Path(sys.argv[4]).resolve()
assert BASE.is_dir() and not OUT.exists() and not BUILD.exists(), 'Preserve existing outputs.'
BUILD.mkdir(parents=True)
OUT.mkdir(parents=True)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


manifest = json.loads((BASE/'manifest.json').read_text(encoding='utf-8'))
original = copy.deepcopy(manifest)
assert manifest['product'] == 'spinel' and manifest['slot'] == 'a'
assert manifest['v26_changes']['capsule_user_accepted']
assert manifest['v26_changes']['freezer_signal_group_exit_fixed']
archive = BASE.parent/'ColorOS16_TB371FC_v26_r104_20261103_CANDIDATE.zip'
with zipfile.ZipFile(archive) as source:
    assert source.read('manifest.json') == (BASE/'manifest.json').read_bytes()
    listing = source.read('verification/package-files.sha256').decode('utf-8')
    expected = dict((line.split('  ', 1)[1], line.split('  ', 1)[0])
                    for line in listing.splitlines())
    assert set(expected) | {'verification/package-files.sha256'} == set(source.namelist())
assert len(manifest['images']) == 4
boot = WORKSPACE/'work/r106-recovery-state/boot-r106-recovery-state.img'
boot_sha = '899860494f70ec1b63241a9ebbd25946502bdb7e932558bc114632f908ae0920'
assert boot.stat().st_size == 100663296 and sha(boot) == boot_sha
kernel_validation = json.loads((WORKSPACE/'outputs/r106-recovery-state/validation.json').read_text(encoding='utf-8'))
assert kernel_validation['boot_sha256'] == boot_sha
assert kernel_validation['full_image_build_pass'] and kernel_validation['partition_readback_pass']
rom_repo = Path(__file__).resolve().parents[2]
usb = json.loads((rom_repo/'docs/usb-retest-20261103.json').read_text(encoding='utf-8'))
assert usb['fastboot']['image_sha256'] == boot_sha and usb['fastboot']['normal_boot_pass']

# Copy only the previously archived set, excluding transient attempt logs and
# the old generated hash list. Check every copied preimage against that list.
scripts = {}
for name in sorted(expected):
    if name.startswith('attempt-logs/'):
        continue
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    if name == 'images/boot_a.img':
        continue
    target = OUT/name
    target.parent.mkdir(parents=True, exist_ok=True)
    with (BASE/name).open('rb') as inp, target.open('wb') as dest:
        digest = hashlib.sha256()
        while data := inp.read(16 << 20):
            digest.update(data)
            dest.write(data)
    assert digest.hexdigest() == expected[name], name
    if (name.endswith('.cmd') and '/' not in name) or name.startswith('scripts/') and name.endswith('.ps1'):
        scripts[name] = digest.hexdigest()
    if name.startswith('images/'):
        print('VERIFIED_BASE_IMAGE', name, flush=True)
assert len(scripts) == 7
shutil.copyfile(boot, OUT/'images/boot_a.img')
assert sha(OUT/'images/boot_a.img') == boot_sha
for image in manifest['images']:
    if image['name'] == 'boot':
        image['sha256'] = boot_sha
        image['bytes'] = boot.stat().st_size
    else:
        assert image == next(row for row in original['images'] if row['name'] == image['name'])

manifest.update(label='ColorOS16 TB371FC v27 r106 本地候选',
    state='OFFLINE_VERIFIED_DEVICE_PENDING', based_on='Exact v26/r104 system and accepted runtime components, with the deployed r106 recovery-state boot only.',
    clean_first_boot_tested=False, device_runtime_verified=False,
    runtime_component_set_verified=True, release_channel='local_candidate_not_published')
manifest.pop('tested_device_serial', None)
manifest['kernel'] = dict(build='#43 r106-recovery-state',
    image_sha256=kernel_validation['image_sha256'], source_commit='4b397325943e70d3dbaaff63b5f622ab48668d62',
    source_record_commit='5920918c017ded5440f2a974956b21cf02cdb0f2',
    source_branch='recovery-state-r106', speaker_native_api=19,
    normal_boot_verified=True, partition_readback_verified=True, physical_pixels_confirmed=False,
    exceptional_recovery_exercised=False, init_0x9d_root_cause_fixed=False)
scope = dict(exact_archive_clean_flash_tested=False, full_rom_fastboot_flash_tested=False,
    packaging_modified_device=False, normal_runtime_components_verified=True,
    r106_boot_fastboot_flash_readback_normal_boot_pass=True,
    rear_usb_bidirectional_16mib_pass=True, usb_kernel_code_changed=False,
    use_rear_motherboard_usb=True, black_screen_root_cause_fixed=False,
    exceptional_display_recovery_exercised=False, new_gemini_suggested_patch_included=False)
manifest['v27_changes'] = dict(only_partition_changed_from_v26='boot_a',
    retains_v26_super_and_vbmeta=True, recovery_flag_lifetime_and_generation_guard=True,
    usb_source_changed=False, rejected_r105_included=False, keyboard_candidate_included=False,
    capsule_and_freezer_baseline_preserved=True, firmware_reset_crc_changed=False)
manifest['test_scope_v27'] = 'verification/test-scope-v27.json'
manifest['validation_scope'] = 'Exact v26 super/vbmeta payload hashes preserved; r106 boot already flashed, read back and normally booted. Original offline entry and every archive member verified. This exact full archive has not been clean-flashed or installed through full-ROM fastboot.'
manifest['limitations'] = [
    'Use the verified rear motherboard USB port. Previous front-path failures do not establish a tablet-kernel USB fault; no USB patch is included.',
    'INIT=0x9D root cause remains unresolved. r106 preserves software recovery eligibility; exceptional hardware recovery has not been observed.',
    'This exact full archive has not passed clean first boot or full-ROM fastboot installation; component boot and transfer tests do not replace those checks.',
    'Existing user-accepted experience is preserved. Black-bar acceptance remains user testing; pen lacks hardware validation.',
    'A transient loss of ordinary touch/home interaction was reported while the multi-finger mini-window gesture still worked; it recovered without an agent reboot. Cause remains unknown.',
]
manifest['known_issues_v27'] = 'verification/v27-build-source/known-issues.json'
manifest['inherited_component_notes_scope'] += ' Versioned v23-v26 fields and old verification files remain historical. v27 identity and scope are kernel, v27_changes and test_scope_v27.'
guide = '''# TB371FC ColorOS16 v27 / r106 候选版

当前 v26 系统镜像与已实机刷入的 r106 内核组合。保留汽水胶囊、通用动画取消、冻结退出、四扬与旋转、键盘触控板等现有实现，以及六项推广预装精简。

r106 修正恢复失败后过早清除故障标志的问题，防止旧恢复提交覆盖新故障。35 项源码回归、完整内核构建、boot 分区回读和正常启动通过。INIT=0x9D 根因仍未解决，异常恢复尚待自然故障验证。

另有一次普通触摸与回桌面操作暂时失效的用户反馈，当时多指缩成小窗仍有效，随后恢复。原因尚未确认，未按触控硬件完全失灵定性；本包仍为候选版。

请固定使用电脑主板后置 USB 口。本机在该路径下已通过 16 MiB 双向传输及 fastboot 刷入 96 MiB 同版 boot；之前前置连接路径失败。本整包尚未完成完整 fastboot 或双清首启验收。

沿用原刷机入口与分区布局。先运行“核验ROM”和连接、刷前检查；“清空数据刷入”会删除应用、账号和个人文件，须先备份。仅用于已解锁 TB371FC / spinel / A 槽，不重新锁定。

原 v26/r104 包保留；需回退内核时使用其精确 boot_a.img，SHA256 为 f29c32c15c7276d777f243a322ca35495099c25d6e41e402dd4eacb77121f85b。
'''
(OUT/'刷入说明.md').write_text(guide, encoding='utf-8')
verification = OUT/'verification'
dump(verification/'test-scope-v27.json', scope)
dump(verification/'r106-validation.json', kernel_validation)
dump(verification/'usb-retest-20261103.json', usb)
shutil.copyfile(WORKSPACE/'outputs/r106-recovery-state/r106.git.patch', verification/'r106.git.patch')
source_dir = verification/'v27-build-source'
source_dir.mkdir()
for name in ['package_rom.py', 'archive.py', 'README.md', 'known-issues.json']:
    shutil.copyfile(Path(__file__).parent/name, source_dir/name)
accessories = {row['path']: row for row in manifest['accessories']}
for name in ['刷入说明.md', 'verification/test-scope-v27.json', 'verification/r106-validation.json',
             'verification/usb-retest-20261103.json', 'verification/r106.git.patch',
             *[f'verification/v27-build-source/{name}' for name in ['package_rom.py','archive.py','README.md','known-issues.json']]]:
    accessories[name] = dict(path=name, sha256=sha(OUT/name))
manifest['accessories'] = list(accessories.values())
dump(OUT/'manifest.json', manifest)
assert all(sha(OUT/name) == digest for name, digest in scripts.items())
p = subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',
                    str(OUT/'scripts/Invoke-R91-Clean.ps1')], capture_output=True, timeout=900)
(BUILD/'original-offline-entry.log').write_bytes(p.stdout+p.stderr)
assert p.returncode == 0, (p.stdout+p.stderr)[-2500:]
receipt = dict(state='CANDIDATE_ASSEMBLED_ORIGINAL_OFFLINE_ENTRY_PASS', directory=str(OUT),
    base=str(BASE), original_seven_scripts=scripts,
    image_hashes={row['path']:row['sha256'] for row in manifest['images']},
    only_partition_changed_from_v26='boot_a', original_offline_entry_pass=True,
    device_modified_by_packaging=False, exact_full_archive_clean_flash_pass=False)
dump(BUILD/'package-result.json', receipt)
print('V27_PACKAGE_READY', OUT, flush=True)
