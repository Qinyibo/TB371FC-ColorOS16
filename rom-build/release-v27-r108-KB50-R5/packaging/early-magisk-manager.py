"""Start the R3 Magisk manager install as soon as Android setup completes."""
from hashlib import file_digest, sha256
import json
from pathlib import Path
import runpy
import subprocess
from tempfile import TemporaryDirectory


Image = runpy.run_path(str(Path(__file__).with_name('edit-images.py')))['Image']
APPLY = '/etc/r91-rom/apply.sh'
SUMS = '/etc/r91-rom/SHA256SUMS'
SETUP = b'while [ "$(settings get secure user_setup_complete)" != 1 ]; do sleep 3; done\n'
INSTALL = (b'if sh /system/etc/r94-magisk-manager/install-manager.sh; then\n'
           b'    /system/bin/log -t R94FirstBoot R94_MAGISK_MANAGER_READY\n'
           b'else\n    /system/bin/log -t R94FirstBoot R94_MAGISK_MANAGER_PENDING\nfi\n')


def rewrite(body):
    assert body.count(SETUP) == 1 and body.count(INSTALL) == 1
    setup_done = body.index(SETUP) + len(SETUP)
    bootstrap = body.index(b'sh /system/etc/r94-animation-v1/bootstrap.sh', setup_done)
    install = body.index(INSTALL, bootstrap)
    install_job = (b'\n# Provision the user app independently of launcher and module initialization.\n'
                   b'(\n' + INSTALL + b') &\nmanager_pid=$!\n')
    return (body[:setup_done] + install_job + body[setup_done:install]
            + b'wait "$manager_pid"\n' + body[install + len(INSTALL):])


def main():
    path = Path('system_ext.img')
    with path.open('rb') as stream:
        before = file_digest(stream, 'sha256').hexdigest()
    with TemporaryDirectory() as temp:
        extension = Image(path, Path(temp))
        original = extension.read(APPLY).read_bytes()
        updated = rewrite(original)
        checksums = extension.read(SUMS).read_bytes()
        old = sha256(original).hexdigest().encode() + b'  apply.sh\n'
        new = sha256(updated).hexdigest().encode() + b'  apply.sh\n'
        assert checksums.count(old) == 1
        extension.replace(APPLY, updated, 0o100755)
        extension.replace(SUMS, checksums.replace(old, new, 1), 0o100644)
        subprocess.run(['/bin/sh', '-n', str(extension.read(APPLY))], check=True)
    subprocess.run(['/usr/sbin/e2fsck', '-fn', str(path)], check=True)
    with path.open('rb') as stream:
        after = file_digest(stream, 'sha256').hexdigest()
    report = dict(baseline_sha256=before, system_ext_sha256=after, system_ext_bytes=path.stat().st_size,
                  original_apply_sha256=old.split()[0].decode(), apply_sha256=new.split()[0].decode(),
                  launch='After Setup Wizard, parallel to launcher initialization and dexopt.',
                  filesystem_check='e2fsck -fn passed', runtime_verified=False)
    Path('early-magisk-verification.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
