"""Run in WSL with e2fsprogs; edit independent copies of verified v24 images."""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

build = pathlib.Path(sys.argv[1]).resolve()
base = pathlib.Path('/mnt/d/TB371FC-release/v25-r102-freezer-r1-build')
package = pathlib.Path('/mnt/d/TB371FC-release/R94T-v25-r102-20261102-CANDIDATE-animation-default-r1-freezer-fallback-r1')
manifest = json.loads((package / 'manifest.json').read_text(encoding='utf-8-sig'))
expected = {r['name']: r for r in manifest['logical_partitions']}
plan = json.loads((build / 'plan.json').read_text())
readback = build / 'readback'; readback.mkdir()
log = build / 'image-build.log'
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def cmd(image, command, write=False, absent=False):
    p = subprocess.run(['debugfs'] + (['-w'] if write else []) + ['-R', command, str(image)], capture_output=True, timeout=120)
    text = (p.stdout + p.stderr).decode('utf-8', 'replace')
    with log.open('a') as output: output.write(command + '\n' + text + '\n')
    if absent and 'File not found by ext2_lookup' in text: return None
    assert p.returncode == 0 and not re.search(r'no space|Could not allocate|File not found|while writing|Usage:', text, re.I), (command, text)
    return text
def dump(image, target, name):
    out = readback / name
    assert not out.exists(), out
    cmd(image, f'dump {target} {out}')
    assert out.exists(), out
    return out
for name in ['system_a', 'system_ext_a', 'vendor_a']:
    source = base / (name + '.img'); dest = build / (name + '.img')
    assert not dest.exists(), dest
    digest = hashlib.sha256()
    with source.open('rb') as inp, dest.open('wb') as out:
        while data := inp.read(16 << 20): digest.update(data); out.write(data)
    assert digest.hexdigest() == expected[name]['sha256'], name
    print('BASE_IMAGE_COPY_VERIFIED', name, flush=True)
if plan.get('animation_default_r1', False):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'native-animation'))
    from patch_default_property import INPUT_SHA256, patch
    old = dump(build / 'system_a.img', '/my_manifest/build.prop', 'animation-default-input')
    payload = build / 'payloads/animation-default-build.prop'
    payload.write_bytes(patch(old.read_bytes()))
    plan['changes'].append(dict(payload=payload.name, sha256=sha(payload), partition='system_a',
        target='/my_manifest/build.prop', mode='0644', expected_before=INPUT_SHA256))
changes = []
for index, item in enumerate(plan['changes']):
    image = build / (item['partition'] + '.img'); target = item['target']
    old = dump(image, target, f'{index}-before')
    if item['expected_before']: assert sha(old) == item['expected_before'], target
    source = build / 'payloads' / item['payload']
    assert sha(source) == item['sha256']
    # WLAN diagnostic policy must be the exact existing file plus the scoped
    # opt-in rule, not a replacement from a different device/vendor image.
    if item['payload'] == 'init.target.rc':
        before = old.read_text(); after = source.read_text()
        assert 'service vendor.cnss_diag ' in before and 'service vendor.cnss_diag ' in after
        assert 'persist.vendor.r94.wlan_diag' in after
        (build / 'wlan-before.rc').write_bytes(old.read_bytes())
    label = readback / f'{index}-selinux'
    cmd(image, f'ea_get -f {label} {target} security.selinux')
    assert label.read_bytes(), target
    cmd(image, 'rm ' + target, True)
    cmd(image, f'write {source} {target}', True)
    for field, value in [('mode', '0100' + item['mode'][-3:]), ('uid', '0'), ('gid', '0')]: cmd(image, f'set_inode_field {target} {field} {value}', True)
    cmd(image, f'ea_set -f {label} {target} security.selinux', True)
    actual = dump(image, target, f'{index}-after')
    assert sha(actual) == item['sha256'], target
    stat = cmd(image, 'stat ' + target)
    assert re.search(r'Mode:\s+0?' + item['mode'][-3:] + r'\b', stat), stat
    assert re.search(r'User:\s+0\s+Group:\s+0\b', stat), stat
    label_after = readback / f'{index}-selinux-after'
    cmd(image, f'ea_get -f {label_after} {target} security.selinux')
    assert label_after.read_bytes() == label.read_bytes()
    changes.append({**item, 'before_sha256': sha(old)})
    print('PAYLOAD_READBACK_METADATA_VERIFIED', item['partition'], target, flush=True)
# Remove only the six named promotional preloads, preserving ordinary apps/services.
removed=[]
def remove_tree(target):
    assert target.startswith(('/my_product/del-app/','/my_stock/del-app/'))
    listing=cmd(build/'system_a.img','ls -p '+target)
    rows=[line.split('/') for line in listing.splitlines() if line.startswith('/')]
    assert rows,target
    for row in rows:
        name=row[5]
        if name in ('.','..'):continue
        child=target+'/'+name
        if row[2].startswith('04'):remove_tree(child)
        else:
            assert row[2].startswith('10'),(child,row)
            cmd(build/'system_a.img','rm '+child,True)
    cmd(build/'system_a.img','rmdir '+target,True)
for target in plan['removals']:
    assert cmd(build/'system_a.img','stat '+target,absent=True) is not None,target
    remove_tree(target)
    assert cmd(build/'system_a.img','stat '+target,absent=True) is None,target
    removed.append(target);print('PRELOAD_REMOVED',target,flush=True)
# Remove any stale compiled companions of this exact changed SystemUI APK.
removed_oat=[]
for extension in ['odex','vdex','art']:
    target='/priv-app/SystemUI/oat/arm64/SystemUI.'+extension
    if cmd(build/'system_ext_a.img','stat '+target,absent=True) is not None:
        cmd(build/'system_ext_a.img','rm '+target,True);removed_oat.append(target)

# Verify the actual image's existing startup closure, not just payload files.
image = build / 'system_ext_a.img'
checks = dump(image, '/etc/r91-rom/SHA256SUMS', 'closure-list').read_text()
import posixpath
for index, line in enumerate(checks.splitlines()):
    digest, name = line.split(None, 1)
    target = posixpath.normpath('/etc/r91-rom/' + name.strip())
    assert sha(dump(image, target, f'closure-{index}')) == digest, target
# Preserve the previously reproduced speaker binaries byte-for-byte.
for name, digest in [('direction.so', 'c32f9b49c8a1e4aadd06ea72bcefdc8283f321c71a06a14d7e0b4a705f4aa675'),
                     ('directionctl', 'a4cdf0686a98d8dc455b3543b8bb71c27d3bef0b74d538c9741645ff67b7d679'),
                     ('direction.jar', 'd11f3cf3e9fb8739c1a25c2e48a5cd266a4f07a1d97fdf3b820d606bfe835add')]:
    path = '/etc/r94-native/module-delivery/modules/r94_speaker_direction/' + name
    assert sha(dump(image, path, 'speaker-' + name)) == digest, path
# v23 already removed stale OAT companions of the changed framework.
for extension in ['odex', 'vdex', 'art']:
    path = '/system/framework/oat/arm64/oplus-services.' + extension
    assert cmd(build / 'system_a.img', 'stat ' + path, absent=True) is None, 'Stale framework companion needs explicit handling: ' + path
result = dict(state='INDEPENDENT_IMAGES_READBACK_CLOSURE_FSCK_PASS', changes=changes, removed_preloads=removed, removed_stale_companions=removed_oat, images={})
if plan.get('animation_default_r1', False):
    result['animation_default_r1'] = True
if plan.get('freezer_fallback_r1', False):
    result['freezer_fallback_r1'] = True
for name in ['system_a', 'system_ext_a', 'vendor_a']:
    image = build / (name + '.img')
    p = subprocess.run(['e2fsck', '-fn', str(image)], capture_output=True, timeout=300)
    (build / (name + '-fsck.txt')).write_bytes(p.stdout + p.stderr)
    assert p.returncode == 0, (name, p.returncode)
    # The packager runs on Windows. Preserve the actual variant build path,
    # rather than accidentally referring to an older build's images.
    image_path = subprocess.check_output(['wslpath', '-w', str(image)], text=True).strip()
    result['images'][name] = dict(path=image_path, sha256=sha(image), bytes=image.stat().st_size)
    print('FSCK_AND_IMAGE_HASH_PASS', name, flush=True)
(build / 'image-result.json').write_text(json.dumps(result, indent=2))
print('V26_R104_IMAGES_READY', flush=True)
