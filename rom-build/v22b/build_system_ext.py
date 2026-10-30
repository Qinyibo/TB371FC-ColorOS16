"""Mutate a private v22a system_ext copy; preserve labels and read back exact bytes."""
from pathlib import Path
import hashlib, json, re, subprocess

O = Path(__file__).resolve().parent
R = Path('/mnt/d/TB371FC-release/v22b-firstboot-publication-build')
IMAGE = R/'system_ext_a-candidate.img'
READBACK = R/'readback'
assert not READBACK.exists()
READBACK.mkdir()
LOG = O/'image-edit-log.txt'
assert not LOG.exists()
changes = {
    '/etc/init/r94-pen-native-v1.rc': O/'overlay/system_ext/etc/init/r94-pen-native-v1.rc',
    '/etc/r94-pen-native-v4/bootstrap.sh': O/'overlay/system_ext/etc/r94-pen-native-v4/bootstrap.sh',
    '/overlay/R94NativeUI_bootreg.apk': O/'wizard-overlay/R94NativeUI_bootreg.apk',
}
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def debug(command, write=False, absent=False):
    q = subprocess.run(['/usr/sbin/debugfs']+(['-w'] if write else [])+['-R',command,str(IMAGE)], capture_output=True, timeout=90)
    s = (q.stdout+q.stderr).decode('utf-8','replace')
    with LOG.open('a') as f: f.write(command+'\n'+s+'\n')
    assert q.returncode == 0 and not re.search(r'(?i)no space|could not allocate|while writing|usage:|not a directory',s), s
    if absent and 'File not found by ext2_lookup' in s:return None
    assert 'File not found by ext2_lookup' not in s, s
    return s
rows=[]
for i,(target,source) in enumerate(changes.items()):
    st=debug('stat '+target)
    assert 'Type: regular' in st and 'Mode:  0644' in st and re.search(r'User:\s*0\s+Group:\s*0',st)
    assert debug('stat '+target+'.fsv_meta', absent=True) is None, 'Unexpected stale integrity companion; stop for review'
    label=READBACK/(str(i)+'.original.label')
    debug('ea_get -f "'+str(label)+'" '+target+' security.selinux')
    expected_label=label.read_bytes()
    assert expected_label.endswith(b'\0')
    original=READBACK/(str(i)+'.original')
    debug('dump '+target+' "'+str(original)+'"')
    debug('rm '+target,True)
    debug('write "'+str(source)+'" '+target,True)
    for field,value in [('mode','0100644'),('uid','0'),('gid','0')]:debug('set_inode_field '+target+' '+field+' '+value,True)
    debug('ea_set -f "'+str(label)+'" '+target+' security.selinux',True)
    result=READBACK/(str(i)+'.result')
    debug('dump '+target+' "'+str(result)+'"')
    actual_label=READBACK/(str(i)+'.result.label')
    debug('ea_get -f "'+str(actual_label)+'" '+target+' security.selinux')
    assert sha(result)==sha(source) and actual_label.read_bytes()==expected_label
    newstat=debug('stat '+target)
    assert 'Mode:  0644' in newstat and re.search(r'User:\s*0\s+Group:\s*0',newstat)
    rows.append({'target':target,'original_sha256':sha(original),'candidate_sha256':sha(source),'context':expected_label.decode().rstrip('\0'),'metadata_readback_verified':True})
q=subprocess.run(['/usr/sbin/e2fsck','-fn',str(IMAGE)],capture_output=True,timeout=180)
(O/'system_ext-fsck.txt').write_bytes(q.stdout+q.stderr)
assert q.returncode==0
result={'state':'THREE_SCOPED_SYSTEM_EXT_REPLACEMENTS_READBACK_LABEL_FSCK_PASS_HASH_PENDING','changes':rows,
        'new_selinux_rules':False,'boot_kernel_vendor_system_changed':False,'full_clean_boot_tested':False}
(O/'image-mutation-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
