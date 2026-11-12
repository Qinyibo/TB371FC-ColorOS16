"""Add ordinary manager provisioning and start the bound launcher before dexopt."""
from hashlib import sha256
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


Image = runpy.run_path('edit-images.py')['Image']
APK_HASH = '89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7'
CAMERA_HASH = '0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e'
BOOTSTRAP = '/system/etc/r94-animation-v1/bootstrap.sh'
APPLY = '/etc/r91-rom/apply.sh'
SUMS = '/etc/r91-rom/SHA256SUMS'


def digest(data):
    return sha256(data).hexdigest()


def rewrite_bootstrap(body):
    assert digest(body) == 'ba3233fa3b588a019637af99f0bdd1321cea461f41a6730830a2eed0b877e95d'
    compile_start = body.index(b'if [ ! -f "$cache/compiled-')
    defaults_start = body.index(b'# One-time recovery', compile_start)
    compile_body = body[compile_start:defaults_start]
    updated = body[:compile_start] + body[defaults_start:]
    assert updated.endswith(b'echo R94_ANIMATION_MODES_READY\n')
    return (updated + b'/system/bin/log -t R94FirstBoot R94_ANIMATION_MODES_READY\n'
            b'\n# Compile the final bound APKs after the desktop can use stacked recents.\n'
            + compile_body + b'/system/bin/log -t R94FirstBoot R94_ANIMATION_DEXOPT_DONE\n')


def rewrite_apply(body):
    assert digest(body) == '11447f52a6607f8930a514ccef26f5fe8316d555a4da130876ab9cdc6e0135d5'
    # The animation bootstrap compiles the final bound launcher. The legacy
    # early pass compiles the donor launcher before it is replaced.
    early = body.index(b'# Preserve the accepted launcher speed compilation')
    next_step = body.index(b'sh /system_ext/etc/r94-native/module-delivery/delivery.sh provision-market', early)
    assert b'cmd package compile -m speed -f com.android.launcher' in body[early:next_step]
    body = body[:early] + body[next_step:]
    module_delivery = b'sh /system_ext/etc/r94-native/module-delivery/delivery.sh reconcile || echo R94_MODULE_DELIVERY_PENDING\n'
    assert body.count(module_delivery) == 1
    body = body.replace(module_delivery, b'', 1)
    marker = b'echo "R91_ROM_READY launcher_native=1 $(date)"\n'
    assert body.count(marker) == 1
    manager = (b'if sh /system/etc/r94-magisk-manager/install-manager.sh; then\n'
               b'    /system/bin/log -t R94FirstBoot R94_MAGISK_MANAGER_READY\n'
               b'else\n    /system/bin/log -t R94FirstBoot R94_MAGISK_MANAGER_PENDING\nfi\n')
    return body.replace(marker, marker + b'\n' + module_delivery + manager, 1)


def collect_deltas():
    start = 65536 * 512
    limit = start + 9932111872 + 2013265920
    chunk = 33550336
    target = Path('firstboot-deltas')
    target.mkdir()
    with open('/dev/vdd', 'rb') as baseline, open('system.img', 'rb') as system, open('system_ext.img', 'rb') as extension:
        baseline.seek(start)
        for index in range(start // chunk, (limit - 1) // chunk + 1):
            offset = max(start, index * chunk)
            length = min(limit, (index + 1) * chunk) - offset
            old = baseline.read(length)
            new = system.read(length)
            if len(new) < length:
                new += extension.read(length - len(new))
            assert len(old) == len(new) == length
            if old != new:
                (target / f'{index:04d}-{offset}.raw').write_bytes(new)
        assert not system.read(1) and not extension.read(1)
    print(f'FIRSTBOOT_DELTAS {len(list(target.iterdir()))}', flush=True)


with TemporaryDirectory() as scratch:
    system = Image('system.img', Path(scratch))
    extension = Image('system_ext.img', Path(scratch))
    apk = Path('Magisk-v31.1.apk')
    installer = Path('install-manager.sh')
    assert digest(apk.read_bytes()) == APK_HASH
    assert digest(system.read('/system/app/ZuiCamera/ZuiCamera.apk').read_bytes()) == CAMERA_HASH
    system.debugfs('stat /system/app/Magisk', absent=True)
    system.directory('/system/etc/r94-magisk-manager')
    system.put(apk, '/system/etc/r94-magisk-manager/Magisk-v31.1.apk')
    system.put(installer, '/system/etc/r94-magisk-manager/install-manager.sh', 0o100755)
    system.replace(BOOTSTRAP, rewrite_bootstrap(system.read(BOOTSTRAP).read_bytes()), 0o100755)
    original = extension.read(APPLY).read_bytes()
    updated = rewrite_apply(original)
    sums = extension.read(SUMS).read_bytes()
    old_hash = digest(original).encode()
    assert sums.count(old_hash + b'  apply.sh\n') == 1
    extension.replace(APPLY, updated, 0o100755)
    extension.replace(SUMS, sums.replace(old_hash, digest(updated).encode(), 1), 0o100644)
    for script in (installer, system.read(BOOTSTRAP)):
        subprocess.run(['/bin/sh', '-n', str(script)], check=True)
    subprocess.run(['/bin/sh', '-n', str(extension.read(APPLY))], check=True)
    for image in (system, extension):
        subprocess.run(['/usr/sbin/e2fsck', '-fn', str(image.path)], check=True)

collect_deltas()
