"""Verify and merge the guest's changes into the exact, already-flashed KB50 super."""
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re
import runpy
import shutil
import tarfile


HERE = Path(__file__).resolve().parent
PARTS = HERE / 'clean-flash/super-parts-32m'
VM = HERE.parent / 'build-vm'
CHECKSUMS = 'MAGISK-SUPER-SHA256SUMS.txt'
SOURCE_HASH = 'bcfb62c533064fc86ae036ef6a4a01385292b62af7f0b852f98d0ca2f347fe9d'
SYSTEM_START = 65536 * 512
SYSTEM_END = SYSTEM_START + 9932111872
REFERENCE = runpy.run_path(str(HERE.parent / 'package-rom.py'))


def sha(path):
    with path.open('rb') as source:
        return file_digest(source, 'sha256').hexdigest()


def main():
    serial = (VM / 'guest-serial-v13.log').read_text(encoding='utf-8', errors='replace')
    assert 'MAGISK_REMOVAL_RESULT_WRITTEN' in serial and 'TB371FC_VM_EXIT=0' in serial
    source = HERE / 'super-kb50.raw'
    parts = json.loads((PARTS / 'manifest.json').read_bytes())
    assert parts['source_sha256'] == SOURCE_HASH == sha(source)
    assert parts['expanded_size'] == source.stat().st_size == 12884901888
    new = HERE / 'super-kb50-r2.raw'
    with source.open('rb') as inp, new.open('xb') as out:
        shutil.copyfileobj(inp, out, 8 << 20)
    changes = HERE / 'magisk-user-repair'
    changes.mkdir()
    output = []
    with tarfile.open(VM / 'build-result-v13.raw', 'r:') as result, new.open('r+b') as image:
        checks = dict(line.split()[::-1] for line in result.extractfile(CHECKSUMS).read().decode().splitlines())
        assert len(result.getnames()) == len(set(result.getnames())) == len(checks) + 1
        assert set(result.getnames()) == set(checks) | {CHECKSUMS}
        seen = set()
        for name, expected in sorted(checks.items()):
            match = re.fullmatch(r'magisk-system-removal/(\d{4})-(\d+)\.raw', name)
            assert match
            index, start = map(int, match.groups())
            assert index not in seen
            seen.add(index)
            row = parts['parts'][index]
            old_start = row['start']
            old_end = old_start + row['raw_bytes']
            end = min(old_end, SYSTEM_END)
            member = result.getmember(name)
            assert member.isfile() and start == max(old_start, SYSTEM_START) and member.size == end - start > 0
            payload = result.extractfile(member).read()
            assert sha256(payload).hexdigest() == expected
            old_sparse = (PARTS / row['file']).read_bytes()
            old_raw = REFERENCE['part_payload'](old_sparse, row, old_start, parts['expanded_size'])
            image.seek(old_start)
            assert image.read(row['raw_bytes']) == old_raw
            delta_offset = start - old_start
            assert old_raw[delta_offset:delta_offset + len(payload)] != payload
            image.seek(start)
            image.write(payload)
            sparse_offset = 28 + 12 + (12 if old_start else 0) + delta_offset
            data = old_sparse[:sparse_offset] + payload + old_sparse[sparse_offset + len(payload):]
            digest = sha256(data).hexdigest()
            REFERENCE['part_payload'](data, dict(row, sha256=digest), old_start, parts['expanded_size'])
            (changes / row['file']).write_bytes(data)
            output.append(dict(file=row['file'], sha256=digest, bytes=len(data)))
    assert output
    (changes / 'manifest.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(f'R2 super verified {sha(new)}; {len(output)} system-only sparse chunks', flush=True)


if __name__ == '__main__':
    main()
