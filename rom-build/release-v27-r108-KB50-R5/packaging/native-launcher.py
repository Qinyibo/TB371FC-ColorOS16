"""Install the tested Launcher in the R4 image and retire its runtime overlay."""
from hashlib import sha256
import json
from pathlib import Path
import re
import runpy
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory


helpers = runpy.run_path(str(Path(__file__).with_name('edit-images.py')))
Image = helpers['Image']
digest = helpers['digest']

LAUNCHER = '/priv-app/OplusLauncher/OplusLauncher.apk'
ASSETS = '/system/etc/r94-animation-v1'
APPLY = '/etc/r91-rom/apply.sh'
SUMS = '/etc/r91-rom/SHA256SUMS'
DONOR = '1f04f79c4564c58b03673f4ca575e270f08bc10d926ccc6509797aef15cb5024'
STACKED = 'bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d'
BASE_HASHES = {
    'system_a': 'f37e1063c1033459cfa7ed0de9b7a22e53a4269414e89d63b8df82baa9c32885',
    'system_ext_a': 'd9341f23e31a62221e8339487c86f26a2e5e6b000aa04704a2d11ea72747f2d9',
}


def checked_bytes(image, target, expected):
    data = image.read(target).read_bytes()
    assert sha256(data).hexdigest() == expected, target
    return data


def replace_once(data, old, new=b''):
    assert data.count(old) == 1, old
    return data.replace(old, new, 1)


def prepare_bootstrap(data):
    data = replace_once(data, b'for k in launcher settings assistant; do', b'for k in settings assistant; do')
    assert data.count(b'run_cli am force-stop com.android.launcher\n') == 2
    data = data.replace(b'run_cli am force-stop com.android.launcher\n', b'')
    start = data.index(b'if [ ! -f "$cache/launcher/OplusLauncher.apk.prof" ]; then\n')
    end = data.index(b'if [ ! -f "$cache/settings/Settings.apk.prof" ]; then\n', start)
    assert b'bind_apk "$cache/launcher" /system_ext/priv-app/OplusLauncher\n' in data[start:end]
    data = data[:start] + data[end:]
    start = data.index(b'# Discard any Launcher relaunched')
    end = data.index(b'setprop debug.r94.animation_ready 1\n', start)
    assert b'run_cli am start -a android.intent.action.MAIN -c android.intent.category.HOME\n' in data[start:end]
    data = data[:start] + data[end:]
    data = replace_once(data, b'    run_cli settings --user 0 put secure key_recent_style stacked\n')
    assert b'cache/launcher' not in data and b'force-stop com.android.launcher' not in data
    return data


def remove_preopt(image):
    removed = []
    candidates = (LAUNCHER + '.prof', *(
        f'/priv-app/OplusLauncher/oat/arm64/OplusLauncher.{extension}'
        for extension in ('odex', 'vdex', 'art')
    ))
    for target in candidates:
        report = subprocess.run(['/usr/sbin/debugfs', '-R', f'stat {target}', str(image.path)],
                                capture_output=True, text=True, check=True)
        if 'File not found by ext2_lookup' in report.stderr:
            continue
        assert re.search(r'Type:\s+regular', report.stdout), (target, report.stdout, report.stderr)
        image.remove(target)
        removed.append(target)
    return removed


def image_size(path):
    info = path.stat()
    if stat.S_ISBLK(info.st_mode):
        return int(subprocess.check_output(['/usr/sbin/blockdev', '--getsize64', str(path)]))
    return info.st_size


def main():
    names = tuple(BASE_HASHES)
    inputs = sys.argv[1:] or [f'{name}.img' for name in names]
    files = dict(zip(names, map(Path, inputs), strict=True))
    assert all(digest(files[name]) == expected for name, expected in BASE_HASHES.items())
    apk, jar = Path('OplusLauncher.apk'), Path('bootstrap.jar')
    assert digest(apk) == STACKED
    with TemporaryDirectory() as temp:
        scratch = Path(temp)
        system = Image(files['system_a'], scratch)
        extension = Image(files['system_ext_a'], scratch)

        assert digest(extension.read(LAUNCHER)) == DONOR
        extension.replace(LAUNCHER, apk.read_bytes(), 0o100644)
        removed = remove_preopt(extension)
        old_apply = checked_bytes(extension, APPLY, '3e7bc9053a78044e630367815492fb615b002138b973e7f0bb9984556778befa')
        apply = replace_once(old_apply, DONOR.encode(), STACKED.encode())
        assert apply.count(b'key_recent_style stacked') == 1
        old_entry = sha256(old_apply).hexdigest().encode() + b'  apply.sh\n'
        new_entry = sha256(apply).hexdigest().encode() + b'  apply.sh\n'
        sums = replace_once(extension.read(SUMS).read_bytes(), old_entry, new_entry)
        extension.replace(APPLY, apply, 0o100755)
        extension.replace(SUMS, sums, 0o100644)

        boot = checked_bytes(system, f'{ASSETS}/bootstrap.sh', 'a27fef1517955bdd7afb0aabbade628779716d059e41444f1ae199214243e4be')
        system.replace(f'{ASSETS}/bootstrap.sh', prepare_bootstrap(boot), 0o100755)
        props = checked_bytes(system, f'{ASSETS}/manifest.properties', '6738fb51106a27fac9d500ae9ac044a73f88361fcc9a965ef2c8d6dc1e4c2ed0')
        assert b'launcher.delivery=' not in props
        props = b'launcher.delivery=preinstalled\n' + b''.join(
            line for line in props.splitlines(keepends=True)
            if not line.startswith((b'launcher.sourceSha=', b'launcher.recipeSha='))
        )
        system.replace(f'{ASSETS}/manifest.properties', props, 0o100644)
        assert digest(system.read(f'{ASSETS}/bootstrap.jar')) == 'ff416f671bf09b839b2d889312ef85c90bd68c2e8515bfaf4e5ec89edcd760f7'
        system.replace(f'{ASSETS}/bootstrap.jar', jar.read_bytes(), 0o100644)
        assert digest(system.read(f'{ASSETS}/launcher.recipe.gz')) == '0e66a68177c14faa135f95ee0f2d2860f89b83f2e7fed8aa44987385b744706d'
        system.remove(f'{ASSETS}/launcher.recipe.gz')

        for image, target in ((system, f'{ASSETS}/bootstrap.sh'), (extension, APPLY)):
            subprocess.run(['/bin/sh', '-n', str(image.read(target))], check=True)
        assert digest(extension.read(LAUNCHER)) == STACKED
        assert digest(system.read(f'{ASSETS}/bootstrap.jar')) == digest(jar)

    partitions = {}
    for name, path in files.items():
        subprocess.run(['/usr/sbin/e2fsck', '-fn', str(path)], check=True)
        partitions[name] = dict(bytes=image_size(path), before_sha256=BASE_HASHES[name], sha256=digest(path))
    report = dict(launcher_sha256=STACKED, launcher_path='/system_ext' + LAUNCHER,
                  bootstrap_sha256=digest(jar), partitions=partitions, removed_launcher_artifacts=removed,
                  filesystem_check='e2fsck -fn passed', first_desktop_verified=False)
    Path('native-launcher-verification.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
