"""Archive an offline-verified candidate, then verify every archive member."""
import hashlib
import json
import pathlib
import sys
import zipfile

BUILD = pathlib.Path(sys.argv[1]).resolve()
receipt = json.loads((BUILD / 'package-result.json').read_text(encoding='utf-8'))
assert receipt['state'] == 'CANDIDATE_ASSEMBLED_ORIGINAL_OFFLINE_ENTRY_PASS'
ROOT = pathlib.Path(receipt['directory'])
suffix = '-animation-default-r1' if receipt.get('animation_default_r1', False) else ''
if receipt.get('freezer_fallback_r1', False):
    suffix += '-freezer-fallback-r1'
archive = ROOT.parent / 'ColorOS16_TB371FC_v27_r106_20261103_CANDIDATE.zip'
partial = archive.with_suffix('.zip.partial')
assert not archive.exists() and not partial.exists(), 'Preserve any existing archive.'
manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
expected = {r['path']: r['sha256'] for r in manifest['images']}
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.relative_to(ROOT).parts[0] == 'attempt-logs': continue
    name = path.relative_to(ROOT).as_posix()
    if name == 'verification/package-files.sha256': continue
    if name not in expected:
        with path.open('rb') as stream: expected[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
listing = ROOT / 'verification/package-files.sha256'
listing.write_text(''.join(expected[n] + '  ' + n + '\n' for n in sorted(expected)), encoding='utf-8')
expected['verification/package-files.sha256'] = hashlib.sha256(listing.read_bytes()).hexdigest()
with zipfile.ZipFile(partial, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as target:
    for name in sorted(expected):
        digest = hashlib.sha256()
        with (ROOT / name).open('rb') as source, target.open(name, 'w', force_zip64=True) as out:
            while data := source.read(8 << 20): digest.update(data); out.write(data)
        assert digest.hexdigest() == expected[name], name
        if name.startswith('images/'): print('ARCHIVED', name, flush=True)
print('VERIFYING_ALL_COMPRESSED_MEMBERS', flush=True)
with zipfile.ZipFile(partial) as target:
    assert len(target.namelist()) == len(set(target.namelist()))
    assert set(target.namelist()) == set(expected)
    for name in sorted(expected):
        with target.open(name) as source: digest = hashlib.file_digest(source, 'sha256').hexdigest()
        assert digest == expected[name], name
        if name.startswith('images/'): print('ARCHIVE_READBACK_HASH_AND_CRC_PASS', name, flush=True)
partial.rename(archive)
with archive.open('rb') as stream: digest = hashlib.file_digest(stream, 'sha256').hexdigest()
record = dict(state='LOCAL_CANDIDATE_ARCHIVE_MEMBER_HASH_AND_CRC_PASS', path=str(archive), sha256=digest,
    bytes=archive.stat().st_size, members=len(expected), exact_archive_clean_flash_tested=False,
    published=False, device_modified_by_packaging=False,
    original_seven_scripts_unchanged=True)
(BUILD / 'archive-result.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n', encoding='utf-8')
validation = dict(record, only_partition_changed_from_v26='boot_a', r106_boot_component_tested=True, full_rom_fastboot_flash_tested=False, black_screen_root_cause_fixed=False)
archive.with_suffix('.zip.validation.json').write_text(json.dumps(validation, indent=2)+'\n', encoding='utf-8')
print(json.dumps(record), flush=True)
