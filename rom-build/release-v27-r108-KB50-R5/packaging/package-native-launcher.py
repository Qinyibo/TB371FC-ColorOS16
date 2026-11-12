"""Pack the R5 Launcher images into the R4 32 MiB flash layout."""
from contextlib import ExitStack
from hashlib import file_digest, sha256
import json
from pathlib import Path
import runpy
import sys
from zipfile import ZIP_DEFLATED, ZipFile


HERE = Path(__file__).resolve().parent
PACKAGING = runpy.run_path(str(HERE / 'package-kb50.py'))
REFERENCE = PACKAGING['REFERENCE']
PARTS = PACKAGING['PARTS']
LISTING = PACKAGING['LISTING']
REPORT = 'verification/native-launcher.json'
R4_HASH = '463862c4b35024ef9b876cd0a7b0d254285b544f24609032600e1d91e334fa7c'
STARTS = {'system_a': 65536 * 512, 'system_ext_a': 19464192 * 512}
LIMIT = 23396352 * 512


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def package(base, image_dir, output):
    assert digest(base) == R4_HASH
    report = json.loads((image_dir / 'native-launcher-verification.json').read_bytes())
    assert report['filesystem_check'] == 'e2fsck -fn passed'
    assert set(report['partitions']) == set(STARTS)
    for name, entry in report['partitions'].items():
        path = image_dir / f'{name}.img'
        assert path.stat().st_size == entry['bytes'] and digest(path) == entry['sha256']

    with ZipFile(base) as old, ZipFile(output, 'x', ZIP_DEFLATED, compresslevel=1) as new:
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
        assert parts['source_sha256'] == super_image['sha256'] and len(parts['parts']) == 385
        assert original[PACKAGING['MAGISK_PATH']] == PACKAGING['APK_HASH']
        assert original['images/boot_a.img'] == PACKAGING['BOOT_HASH']
        assert STARTS['system_a'] + logical['system_a']['bytes'] == STARTS['system_ext_a']
        assert STARTS['system_ext_a'] + logical['system_ext_a']['bytes'] == LIMIT
        for name, entry in report['partitions'].items():
            assert (entry['before_sha256'], entry['bytes']) == (logical[name]['sha256'], logical[name]['bytes'])

        old_super, new_super = sha256(), sha256()
        old_parts = {name: sha256() for name in STARTS}
        new_parts = {name: sha256() for name in STARTS}
        changed = []
        position = 0
        with ExitStack() as stack:
            sources = {name: stack.enter_context((image_dir / f'{name}.img').open('rb')) for name in STARTS}
            for index, row in enumerate(parts['parts']):
                name = PARTS + row['file']
                chunk = read(name)
                payload = REFERENCE['part_payload'](chunk, row, position, parts['expanded_size'])
                old_super.update(payload)
                end = position + len(payload)
                raw_offset = 28 + 12 + (12 if position else 0)
                updated = chunk
                for partition, offset in STARTS.items():
                    start = max(position, offset)
                    stop = min(end, offset + logical[partition]['bytes'])
                    if start >= stop:
                        continue
                    local = start - position
                    length = stop - start
                    before = payload[local:local + length]
                    after = sources[partition].read(length)
                    assert len(after) == length
                    old_parts[partition].update(before)
                    new_parts[partition].update(after)
                    if before != after:
                        cursor = raw_offset + local
                        updated = updated[:cursor] + after + updated[cursor + length:]
                if updated != chunk:
                    changed.append(row['file'])
                new_super.update(memoryview(updated)[raw_offset:raw_offset + len(payload)])
                write(name, updated)
                row['sha256'] = written[name]
                position = end
                if (index + 1) % 64 == 0 or index == 384:
                    print(f'R5 ZIP {index + 1}/385', flush=True)
            assert all(not stream.read(1) for stream in sources.values())
        assert changed and position == parts['expanded_size']
        assert old_super.hexdigest() == super_image['sha256']
        for name, entry in report['partitions'].items():
            assert old_parts[name].hexdigest() == entry['before_sha256']
            assert new_parts[name].hexdigest() == entry['sha256']
            logical[name]['sha256'] = entry['sha256']
        super_image['sha256'] = parts['source_sha256'] = new_super.hexdigest()
        report.update(source_archive_sha256=R4_HASH, changed_sparse_parts=changed)

        resumable = '清空数据刷入-32M断点续传.cmd'
        guide = read('刷入说明.md').decode('utf-8')
        assert guide.count('KB50 R4') == 1 and guide.count('R4 候选') == 2
        guide = guide.replace('R4 候选', 'R5 候选')
        guide = guide.replace('打开多个应用后，用最近任务手势查看堆叠卡片。',
                              '首次进入桌面后打开多个应用，用最近任务手势验证堆叠卡片。支持堆叠的 Launcher 已预置在系统镜像中。')
        replacements = {
            '刷入说明.md': guide.encode('utf-8'),
            resumable: read(resumable).replace(b'KB50-R4', b'KB50-R5'),
            REPORT: REFERENCE['json_bytes'](report),
            PARTS + 'manifest.json': REFERENCE['json_bytes'](parts),
        }
        accessories = {row['path']: row for row in manifest['accessories']}
        for name, data in replacements.items():
            accessories[name] = dict(path=name, bytes=len(data), sha256=sha256(data).hexdigest())
        manifest['accessories'] = list(accessories.values())
        manifest['label'] = manifest['label'].replace('KB50 R4', 'KB50 R5')
        manifest['based_on'] = 'KB50 R4 with preinstalled stacked-recents Launcher and no runtime Launcher replacement.'
        manifest['validation_scope'] = 'Offline Launcher and filesystem readback and full archive verified. Clean first desktop pending.'
        manifest['native_launcher'] = REPORT
        manifest['kb50_changes']['native_stacked_launcher'] = True
        replacements['manifest.json'] = REFERENCE['json_bytes'](manifest)

        for name in original:
            if name not in written and name not in replacements:
                write(name, read(name))
        for name, data in replacements.items():
            write(name, data)
        new.writestr(LISTING, ''.join(f'{value}  {name}\n' for name, value in sorted(written.items())))


def verify(archive):
    with ZipFile(archive) as package:
        manifest = json.loads(package.read('manifest.json'))
        parts = json.loads(package.read(PARTS + 'manifest.json'))
    logical = {row['name']: row for row in manifest['logical_partitions']}
    vendor_start = LIMIT
    starts = {**STARTS, 'vendor_a': vendor_start}
    hashes = {name: sha256() for name in starts}
    rows = {PARTS + row['file']: row for row in parts['parts']}

    def check_part(name, data):
        row = rows[name]
        position = row['start']
        end = position + row['raw_bytes']
        for partition, offset in starts.items():
            first = max(position, offset)
            last = min(end, offset + logical[partition]['bytes'])
            if first < last:
                raw_offset = 28 + 12 + (12 if position else 0)
                hashes[partition].update(memoryview(data)[raw_offset + first - position:raw_offset + last - position])

    PACKAGING['verify'](archive, on_part=check_part)
    assert all(value.hexdigest() == logical[name]['sha256'] for name, value in hashes.items())


def main():
    base, image_dir, output = map(Path, sys.argv[1:])
    temporary = output.with_suffix('.partial')
    sidecar = output.with_suffix('.zip.sha256')
    assert not output.exists() and not sidecar.exists()
    package(base, image_dir, temporary)
    verify(temporary)
    checksum = digest(temporary)
    temporary.rename(output)
    with sidecar.open('x', encoding='ascii') as stream:
        stream.write(f'{checksum}  {output.name}\n')
    print(f'ARCHIVE_VERIFIED {output.stat().st_size} {checksum}', flush=True)


if __name__ == '__main__':
    main()
