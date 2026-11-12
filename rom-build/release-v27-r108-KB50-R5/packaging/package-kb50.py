"""Build the KB50 candidate with the established v27 sparse partition layout."""
from hashlib import file_digest, sha256
import json
from pathlib import Path, PurePosixPath
import runpy
import sys
from zipfile import ZIP_DEFLATED, ZipFile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'outputs/ColorOS16_TB371FC_v27_r108_KB46_20261110_CANDIDATE.zip'
BOOT = ROOT / 'outputs/boot-r108-kb50-magisk-v31.1.img'
MAGISK = HERE.parent / 'magisk-v31.1/Magisk-v31.1.apk'
MAGISK_PATH = 'assets/root/Magisk-v31.1.apk'
BOOT_HASH = '9cce59f34b1c67cfbfbd0fbc4b8947788d9520e35580f50ca9bfd4fb6e341a21'
APK_HASH = '89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7'
CAMERA_HASH = '0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e'
PARTS = 'super-parts-32m/'
LISTING = 'verification/package-files.sha256'
REFERENCE = runpy.run_path(str(HERE.parent / 'package-rom.py'))


def checksums(archive):
    names = archive.namelist()
    assert len(names) == len(set(names))
    for name in names:
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in name
    rows = dict(line.split('  ', 1)[::-1] for line in archive.read(LISTING).decode().splitlines())
    assert set(rows) | {LISTING} == set(names)
    return rows


def replace_manifest(manifest, boot, parts, replacements, revision):
    assert (manifest['product'], manifest['slot'], manifest['wipe_userdata']) == ('spinel', 'a', True)
    super_image = next(row for row in manifest['images'] if row['name'] == 'super')
    super_image['sha256'] = parts['source_sha256']
    next(row for row in manifest['images'] if row['name'] == 'boot').update(sha256=BOOT_HASH, bytes=len(boot))
    manifest.update(label=f'ColorOS16 TB371FC v27 / r108 KB50 {revision} 候选整包',
                    based_on='v27 system with direct Camera preload, KB50 wake kernel and Magisk 31.1.',
                    magisk='31.1', clean_first_boot_tested=False, device_runtime_verified=False,
                    runtime_component_set_verified=False, validation_scope='Exact archive and edited filesystems checked offline. Clean first boot and camera hardware checks pending.',
                    inherited_component_notes_scope='Versioned v23–v27 and KB46 notes describe previous releases. Current scope is kernel, kb50_changes and offline_magisk_manager.')
    manifest['kernel'].update(build='#50 r108-force-rek-keyboard-bias-wake-idle-ab',
                              image_sha256='36ecd89712bc20b0b86da94909447d401f6ad441efe4212cbfdfd8629d0faa03',
                              partition_readback_verified=False, normal_boot_verified=True)
    manifest['offline_magisk_manager'].update(path=MAGISK_PATH, sha256=APK_HASH, version='31.1',
        version_code=31100, installation='user_app', entry='安装Magisk.cmd', auto_grant_root=False)
    camera = manifest['camera_media_compat']['APK']
    assert camera['sha256'] == CAMERA_HASH and camera['version_code'] == 160070001
    camera.pop('exact_full_update', None)
    camera.update(system_base='/system/app/ZuiCamera/ZuiCamera.apk',
                  delivery='Complete signed APK and ARM64 libraries scanned by PackageManager at boot.')
    manifest['kb50_changes'] = dict(camera_system_preload=True, magisk_system_preload=False,
        camera_post_setup_installer_removed=True, changed_super_partitions=['system_a', 'system_ext_a'],
        exact_archive_clean_flash_verified=False, camera_physical_verified=False,
        low_frequency_wake_failure_ruled_out=False)
    if revision == 'R3':
        manifest['offline_magisk_manager'].update(installation='firstboot_user_app',
            firstboot_asset='/system/etc/r94-magisk-manager/Magisk-v31.1.apk')
        manifest['kb50_changes'].update(magisk_firstboot_package_manager_install=True,
                                        stacked_launcher_ready_before_dexopt=True)
    accessories = {entry['path']: entry for entry in manifest['accessories']}
    accessories.pop('assets/root/Magisk-v30.7.apk', None)
    for name, data in replacements.items():
        accessories[name] = dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest())
    manifest['accessories'] = list(accessories.values())
    return manifest


def build(archive, raw, revision):
    assert raw.stat().st_size == 12884901888
    with ZipFile(BASE) as old, ZipFile(archive, 'x', ZIP_DEFLATED, compresslevel=1) as new:
        original = checksums(old)

        def read(name):
            data = old.read(name)
            assert sha256(data).hexdigest() == original[name], name
            return data

        manifest = json.loads(read('manifest.json'))
        parts = json.loads(read(PARTS + 'manifest.json'))
        assert len(parts['parts']) == 385
        boot = REFERENCE['read_checked'](BOOT, BOOT_HASH)
        apk = REFERENCE['read_checked'](MAGISK, APK_HASH)
        resumable = '清空数据刷入-32M断点续传.cmd'
        camera_guide = next(name for name in original if name.startswith('assets/camera/') and name.endswith('.md'))
        replacements = {
            MAGISK_PATH: apk,
            resumable: read(resumable).replace(b'v27-r108-KB46', f'v27-r108-KB50-{revision}'.encode()),
            '刷入说明.md': (HERE / ('刷入说明-R3.md' if revision == 'R3' else '刷入说明.md')).read_bytes(),
            '安装Magisk.cmd': (HERE / '安装Magisk.cmd').read_bytes(),
            'scripts/Install-Magisk.ps1': (HERE / 'Install-Magisk.ps1').read_bytes(),
            camera_guide: ('# ZUI 相机\n\n完整版已内置，完成 Android 初始设置后直接打开。'
                           '首次使用时按需授权拍照和录音。此整包的前后摄像头预览、拍照和保存待清刷验收。\n').encode(),
        }
        written = {}

        def write(name, data):
            assert name not in written
            new.writestr(name, data)
            written[name] = sha256(data).hexdigest()

        reconstructed = sha256()
        with raw.open('rb') as source:
            for index, row in enumerate(parts['parts']):
                name = PARTS + row['file']
                old_chunk = read(name)
                prior = REFERENCE['part_payload'](old_chunk, row, source.tell(), raw.stat().st_size)
                data = source.read(row['raw_bytes'])
                assert len(data) == row['raw_bytes']
                reconstructed.update(data)
                offset = len(old_chunk) - len(prior) - (12 if source.tell() < raw.stat().st_size else 0)
                write(name, old_chunk[:offset] + data + old_chunk[offset + len(data):])
                row['sha256'] = written[name]
                if (index + 1) % 64 == 0 or index == 384:
                    print(f'ZIP_WRITE {index + 1}/385', flush=True)
            assert source.tell() == parts['expanded_size'] and not source.read(1)
        parts['source_sha256'] = reconstructed.hexdigest()
        replacements[PARTS + 'manifest.json'] = REFERENCE['json_bytes'](parts)
        replace_manifest(manifest, boot, parts, replacements, revision)
        replacements.update({'manifest.json': REFERENCE['json_bytes'](manifest), 'images/boot_a.img': boot})
        for name in original:
            if name not in written and name not in replacements and name != 'assets/root/Magisk-v30.7.apk':
                write(name, read(name))
        for name, data in replacements.items():
            write(name, data)
        new.writestr(LISTING, ''.join(f'{value}  {name}\n' for name, value in sorted(written.items())))


def verify(archive, on_part=None):
    with ZipFile(archive) as package:
        hashes = checksums(package)
        manifest = json.loads(package.read('manifest.json'))
        parts = json.loads(package.read(PARTS + 'manifest.json'))
        super_image = next(row for row in manifest['images'] if row['name'] == 'super')
        part_hashes = {PARTS + row['file']: row['sha256'] for row in parts['parts']}
        assert all(hashes[name] == value for name, value in part_hashes.items())
        for name in hashes.keys() - part_hashes.keys():
            assert sha256(package.read(name)).hexdigest() == hashes[name], name
        for row in (*manifest['tools'], *manifest['accessories'],
                    *(entry for entry in manifest['images'] if entry['name'] != 'super')):
            assert hashes[row['path']] == row['sha256'], row['path']
        REFERENCE['validate_parts'](package.read, parts, super_image, on_part=on_part)


if __name__ == '__main__':
    raw, output = map(Path, sys.argv[1:3])
    revision = sys.argv[3] if len(sys.argv) > 3 else 'R2'
    assert revision in ('R2', 'R3')
    temporary = output.with_suffix('.partial')
    sidecar = output.with_suffix('.zip.sha256')
    assert not output.exists() and not sidecar.exists()
    build(temporary, raw, revision)
    verify(temporary)
    with temporary.open('rb') as stream:
        checksum = file_digest(stream, 'sha256').hexdigest()
    temporary.rename(output)
    with sidecar.open('x', encoding='ascii') as stream:
        stream.write(f'{checksum}  {output.name}\n')
    print(f'ARCHIVE_VERIFIED {output.stat().st_size} {checksum}', flush=True)
