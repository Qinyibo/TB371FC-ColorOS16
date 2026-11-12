"""Install exact APKs into private copies of the two v27 ext4 images."""
from hashlib import file_digest, sha256
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


class Image:
    def __init__(self, name, scratch):
        self.path = Path(name)
        self.scratch = scratch

    def debugfs(self, command, write=False, absent=False):
        args = ['/usr/sbin/debugfs', *(['-w'] if write else []), '-R', command, str(self.path)]
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        report = result.stdout + result.stderr
        if absent:
            assert 'File not found by ext2_lookup' in report, report
        else:
            assert not re.search(r'file not found|could not|no space|while (writing|reading)|usage:|already exists|not a directory', report, re.I), report
        return report

    def read(self, target):
        output = self.scratch / 'readback'
        output.unlink(missing_ok=True)
        self.debugfs(f'dump {target} {output}')
        assert output.is_file()
        return output

    def metadata(self, target, mode, label):
        self.debugfs(f'set_inode_field {target} mode 0{mode:o}', True)
        label_file = self.scratch / 'label'
        label_file.write_bytes(label)
        self.debugfs(f'ea_set -f {label_file} {target} security.selinux', True)
        self.debugfs(f'ea_get -f {label_file} {target} security.selinux')
        assert label_file.read_bytes() == label
        info = self.debugfs(f'stat {target}')
        assert re.search(rf'Mode:\s+0{mode & 0o777:03o}\b', info), info
        assert re.search(r'User:\s+0\s+Group:\s+0\b', info), info

    def put(self, source, target, mode=0o100644, label=b'u:object_r:system_file:s0\0'):
        self.debugfs(f'stat {target}', absent=True)
        self.debugfs(f'write {source} {target}', True)
        self.metadata(target, mode, label)
        assert digest(self.read(target)) == digest(source), target

    def directory(self, target):
        self.debugfs(f'stat {target}', absent=True)
        self.debugfs(f'mkdir {target}', True)
        self.metadata(target, 0o40755, b'u:object_r:system_file:s0\0')

    def remove(self, target, directory=False):
        self.debugfs(f'{"rmdir" if directory else "rm"} {target}', True)
        self.debugfs(f'stat {target}', absent=True)

    def replace(self, target, content, mode):
        label_file = self.scratch / 'old-label'
        label_file.unlink(missing_ok=True)
        self.debugfs(f'ea_get -f {label_file} {target} security.selinux')
        label = label_file.read_bytes()
        assert label.startswith(b'u:object_r:') and label.endswith(b'\0')
        source = self.scratch / 'replacement'
        source.write_bytes(content)
        self.remove(target)
        self.put(source, target, mode, label)


def preload(image, apk, name, expected_hash, expected_libs):
    assert digest(apk) == expected_hash
    target = f'/system/app/{name}'
    for directory in (target, f'{target}/lib', f'{target}/lib/arm64'):
        image.directory(directory)
    image.put(apk, f'{target}/{name}.apk')
    with ZipFile(apk) as package:
        entries = [item for item in package.namelist() if item.startswith('lib/arm64-v8a/')]
        assert len(entries) == len(set(entries)) == expected_libs
        for member in entries:
            filename = member.removeprefix('lib/arm64-v8a/')
            assert re.fullmatch(r'lib[\w.+-]+\.so', filename)
            library = image.scratch / filename
            library.write_bytes(package.read(member))
            assert library.read_bytes()[:4] == b'\x7fELF'
            image.put(library, f'{target}/lib/arm64/{filename}', 0o100755)
    print(f'APK_READBACK_OK {target} {expected_hash} arm64_libraries={len(entries)}', flush=True)


def main():
    with TemporaryDirectory() as temp:
        system = Image('system.img', Path(temp))
        extension = Image('system_ext.img', Path(temp))
        expected = {
            '/system/app/ZuiCameraSeed/ZuiCameraSeed.apk': '3019d0e8d7815a5e0a5b60dafed7803172954e42883e5ae17c109401e020d511',
            '/system/etc/r94-camera-v7/ZuiCamera.apk.xz': '47c319d28086f0d9819ecb8404f27c5694c90d8dc843a01bdf67f6a4f753793c',
            '/system/etc/r94-camera-v7/install-once.sh': '6e4a8b40086bd10e24cbe07de508dba5db17493710c22c517b9aa0c23ed4affc',
        }
        for path, checksum in expected.items():
            assert digest(system.read(path)) == checksum, path
        for path in expected:
            system.remove(path)
        for path in ('/system/app/ZuiCameraSeed', '/system/etc/r94-camera-v7'):
            system.remove(path, directory=True)
        preload(system, Path('ZuiCamera.apk'), 'ZuiCamera',
                '0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e', 39)
        preload(system, Path('Magisk-v31.1.apk'), 'Magisk',
                '89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7', 7)

        apply_path = '/etc/r91-rom/apply.sh'
        sums_path = '/etc/r91-rom/SHA256SUMS'
        apply = extension.read(apply_path).read_bytes()
        old_hash = sha256(apply).hexdigest()
        assert old_hash == 'fefea417fb6620bdd8bbc3e330dce3d627f27d55b1d9d1204d1ce456a71753bd'
        callback = b'sh /system/etc/r94-camera-v7/install-once.sh || echo R94_CAMERA_PRELOAD_PENDING\n'
        assert apply.count(callback) == 1
        updated = apply.replace(callback, b'', 1)
        sums = extension.read(sums_path).read_bytes()
        assert sums.count(old_hash.encode() + b'  apply.sh\n') == 1
        extension.replace(apply_path, updated, 0o100755)
        extension.replace(sums_path, sums.replace(old_hash.encode(), sha256(updated).hexdigest().encode(), 1), 0o100644)
        subprocess.run(['/bin/sh', '-n', str(extension.read(apply_path))], check=True)
        for image in (system, extension):
            subprocess.run(['/usr/sbin/e2fsck', '-fn', str(image.path)], check=True)


if __name__ == '__main__':
    main()
