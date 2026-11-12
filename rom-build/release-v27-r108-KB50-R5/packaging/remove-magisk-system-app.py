"""Remove only the verified Magisk system APK and its bundled ARM64 libraries."""
from hashlib import sha256
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory

from zipfile import ZipFile

from importlib.util import module_from_spec, spec_from_file_location


spec = spec_from_file_location('edit_images', 'edit-images.py')
tools = module_from_spec(spec)
spec.loader.exec_module(tools)
magisk = '/system/app/Magisk'
apk = Path('Magisk-v31.1.apk')
expected = '89cefac0a318afa39fb3880c45c87b036c05bc1ebf02a7a715b7f8d7c26ac6e7'
camera_hash = '0c72c201cef16bb4e187257690d7963b3c49c13dfa990ebb3cc1b53da57e7b7e'
assert tools.digest(apk) == expected
with TemporaryDirectory() as scratch, ZipFile(apk) as package:
    system = tools.Image('system.img', Path(scratch))
    assert tools.digest(system.read(f'{magisk}/Magisk.apk')) == expected
    for member in package.namelist():
        if member.startswith('lib/arm64-v8a/'):
            name = member.rsplit('/', 1)[1]
            assert re.fullmatch(r'lib[\w.+-]+\.so', name)
            target = f'{magisk}/lib/arm64/{name}'
            assert tools.digest(system.read(target)) == sha256(package.read(member)).hexdigest()
            system.remove(target)
    system.remove(f'{magisk}/Magisk.apk')
    for path in (f'{magisk}/lib/arm64', f'{magisk}/lib', magisk):
        system.remove(path, directory=True)
    assert tools.digest(system.read('/system/app/ZuiCamera/ZuiCamera.apk')) == camera_hash
    subprocess.run(['/usr/sbin/e2fsck', '-fn', str(system.path)], check=True)

# Compare only the system extent to the previously tested super image.
chunk_size = 33550336
system_start = 65536 * 512
system_size = 9932111872
system_end = system_start + system_size
changed = Path('magisk-system-removal')
changed.mkdir()
with open('/dev/vdd', 'rb') as baseline, open('system.img', 'rb') as updated:
    for index in range(system_start // chunk_size, (system_end - 1) // chunk_size + 1):
        chunk_start = index * chunk_size
        start = max(chunk_start, system_start)
        end = min(chunk_start + chunk_size, system_end)
        baseline.seek(start)
        new = updated.read(end - start)
        old = baseline.read(end - start)
        assert len(new) == len(old) == end - start
        if new != old:
            (changed / f'{index:04d}-{start}.raw').write_bytes(new)
    assert updated.tell() == system_size and not updated.read(1)
assert any(changed.iterdir())
print(f'MAGISK_SYSTEM_APP_REMOVED changed_parts={len(list(changed.iterdir()))}', flush=True)
