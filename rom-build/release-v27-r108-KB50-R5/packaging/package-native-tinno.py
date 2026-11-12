"""Create and verify the R4 candidate from the verified R3 archive and vendor image."""
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
from pathlib import Path
import runpy
import struct
import sys
from zipfile import ZIP_DEFLATED, ZipFile


HERE = Path(__file__).resolve().parent
PACKAGING = runpy.run_path(str(HERE / 'package-kb50.py'))
REFERENCE = PACKAGING['REFERENCE']
PARTS = PACKAGING['PARTS']
LISTING = PACKAGING['LISTING']
MODULE = 'assets/root/tb371fc_tinno_vintf_pair.zip'
REPORT = 'verification/native-tinno.json'
MAGISK_REPORT = 'verification/early-magisk-manager.json'
SYSTEM_START = 65536 * 512
EXTENSION_START = 19464192 * 512
VENDOR_START = 23396352 * 512
R3_HASH = 'b980c2163a8c96ca6e4ea00e088e2becfcce13da2ea6d334fe30d9fd7b98f6c9'


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def edit_guide(data):
    guide = data.decode('utf-8')
    lines = guide.splitlines(keepends=True)
    old = [index for index, line in enumerate(lines) if line.startswith('6. ') and MODULE in line]
    assert len(old) == 1
    lines[old[0]] = ('6. Tinno 键盘配置已内置到 vendor 镜像。清刷进入桌面后，验证磁吸键盘打字、触控板、'
                     '重新吸附和休眠唤醒后的输入。R4 候选尚待上述实机验收。\n')
    guide = ''.join(lines).replace('KB50 R3 候选整包', 'KB50 R4 候选整包', 1)
    return guide.replace('系统会加载桌面动画组件，并在后台调用 Android 安装 Magisk 管理器为普通应用。',
                         '开机引导完成后，Android 开始把 Magisk 管理器安装为普通应用，桌面动画组件同时初始化。',
                         1).encode('utf-8')


def build(base, vendor, report_path, extension, magisk_report_path, temporary):
    assert digest(base) == R3_HASH
    report = json.loads(report_path.read_bytes())
    assert report['filesystem_check'] == 'e2fsck -fn passed'
    assert report['vendor_sha256'] == digest(vendor)
    assert report['vendor_bytes'] == vendor.stat().st_size
    magisk_report = json.loads(magisk_report_path.read_bytes())
    assert magisk_report['filesystem_check'] == 'e2fsck -fn passed'
    assert magisk_report['system_ext_sha256'] == digest(extension)
    assert magisk_report['system_ext_bytes'] == extension.stat().st_size
    partition_updates = [
        ('system_ext_a', EXTENSION_START, extension, magisk_report['baseline_sha256'], magisk_report['system_ext_sha256']),
        ('vendor_a', VENDOR_START, vendor, report['baseline_sha256'], report['vendor_sha256']),
    ]

    with ZipFile(base) as old, ZipFile(temporary, 'x', ZIP_DEFLATED, compresslevel=1) as new:
        original = PACKAGING['checksums'](old)
        written = {}

        def read(name):
            data = old.read(name)
            assert sha256(data).hexdigest() == original[name], name
            return data

        def write(name, data):
            assert name not in written, name
            new.writestr(name, data)
            written[name] = sha256(data).hexdigest()

        manifest = json.loads(read('manifest.json'))
        parts = json.loads(read(PARTS + 'manifest.json'))
        super_image = next(row for row in manifest['images'] if row['name'] == 'super')
        logical = {row['name']: row for row in manifest['logical_partitions']}
        vendor_image = logical['vendor_a']
        assert vendor_image['sha256'] == report['baseline_sha256']
        assert logical['system_a']['bytes'] == EXTENSION_START - SYSTEM_START
        assert logical['system_ext_a']['bytes'] == VENDOR_START - EXTENSION_START
        assert all(logical[name]['bytes'] == path.stat().st_size for name, _, path, _, _ in partition_updates)
        assert original[PACKAGING['MAGISK_PATH']] == PACKAGING['APK_HASH']
        assert original['images/boot_a.img'] == PACKAGING['BOOT_HASH']
        assert parts['source_sha256'] == super_image['sha256'] and len(parts['parts']) == 385
        vbmeta = read('images/vbmeta_a.img')
        assert vbmeta[:4] == b'AVB0' and struct.unpack_from('>I', vbmeta, 120) == (3,)

        image_hash = sha256()
        source_hash = sha256()
        system_hash = sha256()
        changed = {name: [] for name, *_ in partition_updates}
        before_hashes = {name: sha256() for name, *_ in partition_updates}
        position = 0
        with ExitStack() as stack:
            streams = {name: stack.enter_context(path.open('rb')) for name, _, path, _, _ in partition_updates}
            for index, row in enumerate(parts['parts']):
                name = PARTS + row['file']
                chunk = read(name)
                payload = REFERENCE['part_payload'](chunk, row, position, parts['expanded_size'])
                source_hash.update(payload)
                end = position + len(payload)
                system_start, system_end = max(position, SYSTEM_START), min(end, EXTENSION_START)
                if system_start < system_end:
                    system_hash.update(payload[system_start - position:system_end - position])
                raw_offset = 28 + 12 + (12 if position else 0)
                for part, offset, *_ in partition_updates:
                    overlap_start = max(position, offset)
                    overlap_end = min(end, offset + logical[part]['bytes'])
                    if overlap_start >= overlap_end:
                        continue
                    start = overlap_start - position
                    length = overlap_end - overlap_start
                    old_slice = payload[start:start + length]
                    new_slice = streams[part].read(length)
                    assert len(new_slice) == length
                    before_hashes[part].update(old_slice)
                    if old_slice != new_slice:
                        cursor = raw_offset + start
                        chunk = chunk[:cursor] + new_slice + chunk[cursor + length:]
                        changed[part].append(row['file'])
                image_hash.update(memoryview(chunk)[raw_offset:raw_offset + len(payload)])
                write(name, chunk)
                row['sha256'] = written[name]
                position = end
                if (index + 1) % 64 == 0 or index == 384:
                    print(f'R4 ZIP {index + 1}/385', flush=True)
            assert all(not stream.read(1) for stream in streams.values())
        assert all(changed.values()) and position == parts['expanded_size']
        for name, _, _, before, after in partition_updates:
            assert before_hashes[name].hexdigest() == before, name
            logical[name]['sha256'] = after
        logical['system_a']['sha256'] = system_hash.hexdigest()
        assert source_hash.hexdigest() == super_image['sha256']
        super_image['sha256'] = parts['source_sha256'] = image_hash.hexdigest()
        report.update(source_archive_sha256=R3_HASH, vendor_start=VENDOR_START, changed_sparse_parts=changed['vendor_a'],
                      vbmeta={row['name']: row['sha256'] for row in manifest['images']
                              if row['name'] in ('vbmeta', 'vbmeta_system')},
                      inherited_top_level_avb_flags=3,
                      runtime_verified=False)
        magisk_report.update(system_ext_start=EXTENSION_START, changed_sparse_parts=changed['system_ext_a'])

        manifest['label'] = manifest['label'].replace('KB50 R3', 'KB50 R4')
        manifest['based_on'] = 'KB50 R3 with native Tinno VINTF and earlier Magisk manager provisioning.'
        manifest['validation_scope'] = 'Edited filesystems, readback and full archive verified offline. Device runtime pending.'
        manifest['native_tinno'] = REPORT
        manifest['early_magisk_manager'] = MAGISK_REPORT
        manifest['state'] = 'OFFLINE_VERIFIED_DEVICE_PENDING'
        manifest['kernel']['physical_keyboard_gestures_verified'] = False
        for field in ('clean_first_boot_tested', 'device_runtime_verified', 'runtime_component_set_verified'):
            manifest[field] = False
        changes = manifest['kb50_changes']
        changes['exact_archive_clean_flash_verified'] = False
        changes['changed_super_partitions'] = ['system_a', 'system_ext_a', 'vendor_a']
        changes['native_tinno_vintf'] = True
        changes['magisk_manager_started_before_launcher_dexopt'] = True
        resumable = '清空数据刷入-32M断点续传.cmd'
        replacements = {
            '刷入说明.md': edit_guide(read('刷入说明.md')),
            resumable: read(resumable).replace(b'KB50-R3', b'KB50-R4'),
            REPORT: REFERENCE['json_bytes'](report),
            MAGISK_REPORT: REFERENCE['json_bytes'](magisk_report),
            PARTS + 'manifest.json': REFERENCE['json_bytes'](parts),
        }
        accessories = {entry['path']: entry for entry in manifest['accessories']}
        del accessories[MODULE]
        for name, data in replacements.items():
            accessories[name] = dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest())
        manifest['accessories'] = list(accessories.values())
        replacements['manifest.json'] = REFERENCE['json_bytes'](manifest)

        for name in original:
            if name not in written and name not in replacements and name != MODULE:
                write(name, read(name))
        for name, data in replacements.items():
            write(name, data)
        new.writestr(LISTING, ''.join(f'{value}  {name}\n' for name, value in sorted(written.items())))


def verify_partitions(archive):
    with ZipFile(archive) as package:
        parts = json.loads(package.read(PARTS + 'manifest.json'))
        manifest = json.loads(package.read('manifest.json'))
        logical = {row['name']: row for row in manifest['logical_partitions']}
        ranges = [('system_ext_a', EXTENSION_START), ('vendor_a', VENDOR_START)]
        actual = {name: sha256() for name, _ in ranges}
        for row in parts['parts']:
            for name, offset in ranges:
                start = max(row['start'], offset)
                end = min(row['start'] + row['raw_bytes'], offset + logical[name]['bytes'])
                if start >= end:
                    continue
                data = package.read(PARTS + row['file'])
                payload = REFERENCE['part_payload'](data, row, row['start'], parts['expanded_size'])
                actual[name].update(payload[start - row['start']:end - row['start']])
        assert all(value.hexdigest() == logical[name]['sha256'] for name, value in actual.items())
        assert MODULE not in package.namelist()


def main():
    base, vendor, report, extension, magisk_report, output = map(Path, sys.argv[1:])
    temporary = output.with_suffix('.partial')
    sidecar = output.with_suffix('.zip.sha256')
    assert not output.exists() and not sidecar.exists()
    build(base, vendor, report, extension, magisk_report, temporary)
    PACKAGING['verify'](temporary)
    verify_partitions(temporary)
    checksum = digest(temporary)
    temporary.rename(output)
    with sidecar.open('x', encoding='ascii') as stream:
        stream.write(f'{checksum}  {output.name}\n')
    print(f'ARCHIVE_VERIFIED {output.stat().st_size} {checksum}', flush=True)


if __name__ == '__main__':
    main()
