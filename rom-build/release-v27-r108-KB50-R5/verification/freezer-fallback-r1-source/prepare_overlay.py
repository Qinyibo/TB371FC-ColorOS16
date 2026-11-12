"""Create a separate reviewed component overlay; never edit the base overlay.

Arguments: base r91-rom directory, built candidate JAR, absent output directory.
This does not modify an image or a connected device.
"""
import hashlib
import json
from pathlib import Path
import sys

BASE_JAR = 'e73be401835ecede505e6c37c75c007a8f5bd840d9441fe0a99b3f5320c3e3a9'
NEW_JAR = 'a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136'
BASE_APPLY = '381e084be9ac4c4131f15127d2a2da62f178f0e748016c4a6c69eef31471353d'
BASE_SUMS = '0b1d707989f48d9c828f02bf4851ea9d47a24807d51463aba5ee95e2fd38d01f'

def sha(data):
    return hashlib.sha256(data).hexdigest()

base, jar, out = map(lambda s: Path(s).resolve(), sys.argv[1:])
assert not out.exists(), 'Preserve existing output; choose an absent directory'
apply = (base / 'apply.sh').read_bytes()
sums = (base / 'SHA256SUMS').read_bytes()
framework = jar.read_bytes()
assert sha(apply) == BASE_APPLY and sha(sums) == BASE_SUMS
assert sha(framework) == NEW_JAR
assert apply.count(BASE_JAR.encode()) == 1 and sums.count(BASE_APPLY.encode()) == 1
apply = apply.replace(BASE_JAR.encode(), NEW_JAR.encode())
sums = sums.replace(BASE_APPLY.encode(), sha(apply).encode())
files = {'system/framework/oplus-services.jar': (framework, '0644'),
         'system_ext/etc/r91-rom/apply.sh': (apply, '0755'),
         'system_ext/etc/r91-rom/SHA256SUMS': (sums, '0644')}
records = []
for name, (data, mode) in files.items():
    path = out / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    records.append(dict(path=name, bytes=len(data), sha256=sha(data), mode=mode,
                        uid=0, gid=0, selinux='u:object_r:system_file:s0'))
(out / 'component.json').write_text(json.dumps(dict(
    variant='freezer-fallback-r1', files=records,
    whole_image_built=False, original_v25_package_changed=False), indent=2) + '\n', encoding='utf-8')
print('FREEZER_COMPONENT_AND_STARTUP_CHECKSUM_CLOSURE_READY', out)
