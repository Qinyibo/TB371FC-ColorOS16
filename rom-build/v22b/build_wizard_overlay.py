from pathlib import Path
import hashlib, json, os, re, shutil, subprocess, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'wizard-overlay'
OUT.mkdir(exist_ok=True)
SDK = Path('C:/android-sdk/build-tools/36.0.0')
ORIGINAL = Path('E:/TB371FC-ROM/workspaces/R7-R93/work/r93-magisk/ui-fit/bootreg/res')
CURRENT = ROOT.parent / 'v22a-original-entry-test-20261025/wizard-layout/BootReg-overlay-current.apk'
EXPECTED_CERT = '573041437424dd6923e043a34b8088fa86abd63c221fe420755210da4798c688'

def run(args, env=None):
    p = subprocess.run([str(x) for x in args], capture_output=True, env=env, timeout=60)
    if p.returncode:
        raise RuntimeError((p.stdout+p.stderr).decode('utf-8', 'replace')[-2000:])
    return p.stdout.decode('utf-8', 'replace')

def resources(text):
    result = {}
    name = None
    for line in text.splitlines():
        m = re.search(r'resource 0x[0-9a-f]+ dimen/(\S+)', line)
        if m:
            name = m.group(1)
            result[name] = {}
        else:
            m = re.match(r'\s+\(([^)]*)\) (\S+)\s*$', line)
            if m and name:
                result[name][m.group(1)] = m.group(2)
    return result

shutil.copytree(ORIGINAL, OUT/'res', dirs_exist_ok=True)
q = OUT/'res/values-w600dp-port'
q.mkdir(exist_ok=True)
(q/'dimens.xml').write_text('''<resources>
  <dimen name="large_nav_card_item_width">180dp</dimen>
  <dimen name="large_nav_card_item_height">130dp</dimen>
  <dimen name="rl_gesture_margin_start">30dp</dimen>
</resources>
''', encoding='utf-8')
(OUT/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.tb371fc.r93.uifit.bootreg" android:versionCode="3" android:versionName="1.2-portrait-test">
  <uses-sdk android:minSdkVersion="36" android:targetSdkVersion="36"/>
  <overlay android:targetPackage="com.coloros.bootreg" android:priority="999" android:isStatic="true"/>
  <application android:hasCode="false" android:label="TB371FC local UI fit"/>
</manifest>
''', encoding='utf-8')
run([SDK/'aapt2.exe', 'compile', '--dir', OUT/'res', '-o', OUT/'compiled.zip'])
run([SDK/'aapt2.exe', 'link', '-o', OUT/'unsigned.apk', '--manifest', OUT/'AndroidManifest.xml',
     '-I', 'C:/android-sdk/platforms/android-36/android.jar', '--auto-add-overlay', OUT/'compiled.zip'])
run([SDK/'zipalign.exe', '-f', '4', OUT/'unsigned.apk', OUT/'aligned.apk'])
source = Path('E:/TB371FC-ROM/workspaces/R7-R93/work/r94/ui-local/qs-fonts-v19/build-fonts.py').read_text(encoding='utf-8')
passwords = set(re.findall(r'pass:([A-Za-z0-9_-]+)', source))
assert len(passwords) == 1
sign_env = dict(os.environ)
sign_env['R94_OVERLAY_SIGN_PASS'] = passwords.pop()
apk = OUT/'R94NativeUI_bootreg.apk'
run([SDK/'apksigner.bat', 'sign', '--ks', 'E:/TB371FC-ROM/workspaces/R7-R93/work/r91/launcher/r91-runtime-test.jks',
     '--ks-pass', 'env:R94_OVERLAY_SIGN_PASS', '--out', apk, OUT/'aligned.apk'], env=sign_env)
cert = run([SDK/'apksigner.bat', 'verify', '--verbose', '--print-certs', apk])
assert EXPECTED_CERT in cert
assert EXPECTED_CERT in run([SDK/'apksigner.bat', 'verify', '--print-certs', CURRENT])
old = resources(run([SDK/'aapt2.exe', 'dump', 'resources', CURRENT]))
new_dump = run([SDK/'aapt2.exe', 'dump', 'resources', apk])
new = resources(new_dump)
assert len(old) == 11
assert {k: new[k] for k in old} == old
added = {k: v for k, v in new.items() if k not in old}
assert added == {'large_nav_card_item_height': {'w600dp-port': '130.000000dp'},
                 'large_nav_card_item_width': {'w600dp-port': '180.000000dp'},
                 'rl_gesture_margin_start': {'w600dp-port': '30.000000dp'}}
manifest = run([SDK/'aapt2.exe', 'dump', 'xmltree', apk, '--file', 'AndroidManifest.xml'])
assert re.search(r'isStatic.*=true', manifest)
run([SDK/'zipalign.exe', '-c', '4', apk])
result = {'state': 'SIGNED_SCOPED_PORTRAIT_RRO_READY_FOR_DEVICE_TEST', 'package': 'com.tb371fc.r93.uifit.bootreg',
          'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(), 'bytes': apk.stat().st_size,
          'same_own_signer_sha256': EXPECTED_CERT, 'all_11_existing_dimensions_and_configs_identical': True,
          'added_dimensions': added, 'target_apk_modified': False, 'global_density_changed': False,
          'live_install_performed': False}
(OUT/'resources.txt').write_text(new_dump, encoding='utf-8')
(OUT/'manifest.txt').write_text(manifest, encoding='utf-8')
(OUT/'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
