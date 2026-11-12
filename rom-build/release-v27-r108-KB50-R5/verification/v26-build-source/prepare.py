"""Stage v26/r104 inputs without touching the device."""
from pathlib import Path
import sys,json,hashlib,shutil
workspace=Path(sys.argv[1]).resolve();build=Path(sys.argv[2]).resolve()
assert not build.exists(), 'Preserve existing builds'
build.mkdir();(build/'payloads').mkdir()
base=Path('D:/TB371FC-release/R94T-v25-r102-20261102-CANDIDATE-animation-default-r1-freezer-fallback-r1')
manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sysui=workspace/'work/capsule-wechat-source/cancel-contract/SystemUI-cancel-snapshots-candidate.apk'
boot=workspace/'work/display-recovery-r104/boot-r104-panel-recovery.img'
assert sha(sysui)=='8ad70cc761213ed3854650f1f477a010fb443b39f96c48c0de62c347f2f39b4a'
assert sha(boot)=='f29c32c15c7276d777f243a322ca35495099c25d6e41e402dd4eacb77121f85b'
shutil.copyfile(sysui,build/'payloads/SystemUI.apk');shutil.copyfile(boot,build/'payloads/boot_a.img')
changes=[dict(payload='SystemUI.apk',sha256=sha(sysui),partition='system_ext_a',target='/priv-app/SystemUI/SystemUI.apk',mode='0644',expected_before='56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928')]
removals=['/my_product/del-app/HeytapReader','/my_product/del-app/HotGamesFolder','/my_stock/del-app/Gamecenter','/my_stock/del-app/OPCommunity','/my_stock/del-app/OPPOStore','/my_stock/del-app/KeKeUserCenterMember']
plan=dict(base_package=str(base),base_images='D:/TB371FC-release/v25-r102-freezer-r1-build',changes=changes,removals=removals,boot_sha256=sha(boot),kernel_commit='455927db6665e2b3696aa8a96bc97fb09c20bd3a',kernel_ref='local/r104-reviewed',kernel_image_sha256='cd216f2cd47c38bd7a86499f87c8a1eca065f428cf4997d62454d13a24812e50',inherited_animation_default_r1=True,inherited_freezer_fallback_r1=True,capsule_user_accepted=True,usb_code_changed=False,black_screen_root_cause_fixed=False,keyboard_candidate_included=False,diagnostic_apk_included=False)
(build/'plan.json').write_text(json.dumps(plan,indent=2));print('V26_INPUTS_STAGED',build,flush=True)
