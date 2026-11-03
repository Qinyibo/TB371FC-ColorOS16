"""Stage exact reviewed payloads; no device commands and no publishing."""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
workspace = pathlib.Path(sys.argv[1]).resolve()
build = pathlib.Path(sys.argv[2]).resolve()
assert sys.argv[3:] in ([], ['--freezer-fallback-r1']), 'Unknown variant option'
freezer_fallback_r1 = bool(sys.argv[3:])
assert not build.exists(), 'Use an absent build directory; preserve existing work.'
payloads = build / 'payloads'
payloads.mkdir(parents=True)
specs = [
    ('framework.jar', workspace / 'work/charger-compat/oplus-services.charger-compat.jar', 'e73be401835ecede505e6c37c75c007a8f5bd840d9441fe0a99b3f5320c3e3a9', 'system_a', '/system/framework/oplus-services.jar', '0644', 'ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467'),
    ('apply.sh', ROOT / 'rom-build/native-overlay/system_ext/etc/r91-rom/apply.sh', '381e084be9ac4c4131f15127d2a2da62f178f0e748016c4a6c69eef31471353d', 'system_ext_a', '/etc/r91-rom/apply.sh', '0755', 'e127d961575603d5773662d2adbe91db4f00023bebf2f2fea13828a844c26020'),
    ('SHA256SUMS', ROOT / 'rom-build/native-overlay/system_ext/etc/r91-rom/SHA256SUMS', '0b1d707989f48d9c828f02bf4851ea9d47a24807d51463aba5ee95e2fd38d01f', 'system_ext_a', '/etc/r91-rom/SHA256SUMS', '0644', '1f4182bbe821d9598364abd18a0d982f9bb2af451a8855891eac6f170c2dfbd6'),
    ('init.target.rc', ROOT / 'rom-build/native-overlay/vendor/etc/init/hw/init.target.rc', '49eb0c6e60fe4a748b489179f7d64fe9a48890e28b35a667bf80b726ae89c56b', 'vendor_a', '/etc/init/hw/init.target.rc', '0644', None),
    ('hqkit.rc', ROOT / 'rom-build/native-overlay/vendor/etc/init/vendor.stc.hardware.hqkitservice@1.0-service.rc', '4e19ca269cf23af0d7147d4b27c63c077af4f63b0f73e9142d6251860204601c', 'vendor_a', '/etc/init/vendor.stc.hardware.hqkitservice@1.0-service.rc', '0644', '3a0c88aef2be3db887c4c6b504ced1fc611d7673417cee88e30288b0d21f9e8f'),
]
def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
if freezer_fallback_r1:
    component = build / 'freezer-component'
    subprocess.run([sys.executable, str(ROOT / 'native-freezer/prepare_overlay.py'),
        str(ROOT / 'rom-build/native-overlay/system_ext/etc/r91-rom'),
        str(workspace / 'work/performance-current/freezer-build/oplus-services.freezer-fallback.jar'),
        str(component)], check=True)
    replacements = [
        ('system/framework/oplus-services.jar', 'a5928b090b68085bd2f32d9ecd39d76d1f4919ffee7072a071ef978232f46136'),
        ('system_ext/etc/r91-rom/apply.sh', 'fefea417fb6620bdd8bbc3e330dce3d627f27d55b1d9d1204d1ce456a71753bd'),
        ('system_ext/etc/r91-rom/SHA256SUMS', '57846b97b5d1ccca02ce350f7dcb324924527b73ba401f878a017efbc10d0570'),
    ]
    for index, (path, digest) in enumerate(replacements):
        name, _, _, partition, target, mode, before = specs[index]
        specs[index] = (name, component / path, digest, partition, target, mode, before)
changes = []
for name, source, digest, partition, target, mode, before in specs:
    assert sha(source) == digest, source
    shutil.copyfile(source, payloads / name)
    changes.append(dict(payload=name, sha256=digest, partition=partition, target=target, mode=mode, expected_before=before))
boot = workspace / 'work/battery-telemetry/boot-r102-batt-avg.img'
assert sha(boot) == '1d84543e6e3c026aaf0560e79c45f73a90c7e2efa7dc876c4395022ccbbaa9e9'
shutil.copyfile(boot, payloads / 'boot_a.img')
plan = dict(base_package='D:/TB371FC-release/R94T-v24-20261101-TEST',
            base_images='D:/TB371FC-release/v24-build', changes=changes,
            boot_sha256=sha(boot), kernel_commit='d981748399d68a57bcbe5faeb25c196589d9bc9c',
            keyboard_candidate_included=False, exact_archive_clean_flash_tested=False,
            animation_default_r1=True)
if freezer_fallback_r1:
    plan['freezer_fallback_r1'] = True
(build / 'plan.json').write_text(json.dumps(plan, indent=2), encoding='utf-8')
print('REVIEWED_PAYLOADS_STAGED', build, flush=True)
