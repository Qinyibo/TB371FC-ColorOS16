"""Prepare existing native animation assets for the cleanup candidate; no device I/O."""
from pathlib import Path
import gzip
import hashlib
import json
import re
import struct
import subprocess
import sys
import zipfile

SOURCE = Path(__file__).resolve().parent
ORIGINAL = Path(sys.argv[1]).resolve()
BUILD = Path(sys.argv[2]).resolve()
BASE = Path(sys.argv[3]).resolve()
OUT = Path(sys.argv[4]).resolve()
assert not OUT.exists(), 'Preserve previous component'
record = json.loads((BUILD/'build-result.json').read_text(encoding='utf-8'))
contract = json.loads((BUILD/'contract-result.json').read_text(encoding='utf-8'))
assert contract['state'] == 'HOST_EXTRACTED_DEX_CONTRACT_PASS'
candidate = BUILD/'OplusLauncher-input-lifecycle-r1.apk'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
props = dict(line.split('=',1) for line in (BASE/'manifest.properties').read_text(encoding='ascii').splitlines() if '=' in line)
old_props = dict(props)
before = ORIGINAL.read_bytes(); after = candidate.read_bytes()
assert sha(before) == props['launcher.sourceSha']
assert sha(after) == record['candidate_sha256']
assert props['launcher.outputSha'] == record['source_sha256']
spans = []
with zipfile.ZipFile(ORIGINAL) as old, zipfile.ZipFile(candidate) as new:
    originals = {entry.filename: entry for entry in old.infolist()}
    def payload(raw, entry):
        offset = entry.header_offset
        names, extra = struct.unpack_from('<HH', raw, offset+26)
        start = offset+30+names+extra
        return start, raw[start:start+entry.compress_size]
    for entry in new.infolist():
        if entry.filename not in originals: continue
        target, data = payload(after, entry)
        source, previous = payload(before, originals[entry.filename])
        if len(data)>16 and data==previous: spans.append((target,source,len(data)))
recipe = bytearray(b'R94PEN02'); cursor=0
for target, source, count in sorted(spans):
    if cursor<target:
        literal=after[cursor:target];recipe+=b'\2'+struct.pack('>Q',len(literal))+literal
    recipe+=b'\1'+struct.pack('>QQ',source,count);cursor=target+count
if cursor<len(after):
    literal=after[cursor:];recipe+=b'\2'+struct.pack('>Q',len(literal))+literal
recipe+=b'\0'
assets=OUT/'system/etc/r94-animation-v1';assets.mkdir(parents=True)
packed=gzip.compress(recipe,mtime=0)
(assets/'launcher.recipe.gz').write_bytes(packed)
props.update({'launcher.outputSha':sha(after),'launcher.outputSize':str(len(after)), 'launcher.recipeSha':sha(packed)})
(assets/'manifest.properties').write_text(''.join(k+'='+props[k]+'\n' for k in sorted(props)),encoding='ascii',newline='\n')
# Retain the existing compilation marker protocol, changing its identity with
# the new output hashes so an old AOT-completion marker is not inherited.
order=['launcher','settings','assistant']
digest=lambda p:sha(('directory-ro-v3'+''.join(p[k+'.outputSha'] for k in order)).encode())[:16]
bootstrap=(BASE/'bootstrap.sh').read_text(encoding='utf-8')
old_marker='compiled-'+digest(old_props); new_marker='compiled-'+digest(props)
assert bootstrap.count(old_marker)==2
(assets/'bootstrap.sh').write_text(bootstrap.replace(old_marker,new_marker),encoding='utf-8',newline='\n')
probe=BUILD/'recipe-probe';probe.mkdir()
wrapper=probe/'RecipeProbe.java'
wrapper.write_text('''package org.tb371fc.animation;
import java.io.File;
public class RecipeProbe { public static void main(String[] a)throws Exception {
 NativeAssets.apply(new File(a[0]),new File(a[1]),new File(a[2]),Long.parseLong(a[3]));
 System.out.println(NativeAssets.sha(new File(a[2]))); } }
''',encoding='utf-8',newline='\n')
native=SOURCE.parent/'source/work/animation-modes/NativeAssets.java'
java=Path('C:/Program Files/Java/jdk-21/bin')
subprocess.run([str(java/'javac.exe'),'-d',str(probe),str(native),str(wrapper)],check=True)
p=subprocess.run([str(java/'java.exe'),'-cp',str(probe),'org.tb371fc.animation.RecipeProbe',
    str(ORIGINAL),str(assets/'launcher.recipe.gz'),str(probe/'rebuilt.apk'),str(len(after))],capture_output=True,check=True)
assert p.stdout.decode().strip()==sha(after)
assert (probe/'rebuilt.apk').read_bytes()==after
files=[]
for path in sorted(assets.iterdir()):
    files.append(dict(path=path.relative_to(OUT).as_posix(),sha256=sha(path.read_bytes()),
        previous_sha256=sha((BASE/path.name).read_bytes()),mode='0644',uid=0,gid=0,selinux='u:object_r:system_file:s0'))
component=dict(state='NATIVE_COMPONENT_READY_DEVICE_NOT_INSTALLED', files=files,
    owner='existing r94-animation-v1 native bootstrap',candidate_sha256=sha(after),
    source_sha256=props['launcher.sourceSha'],previous_launcher_sha256=record['source_sha256'],
    production_recipe_applier_host_readback_pass=True,compile_marker=new_marker,
    settings_and_assistant_unchanged=True,device_modified=False,
    source_incident_fixed_claimed=False,rollback='Restore the three previous assets from the accepted baseline; normal native startup rebuilds its exact previous Launcher.')
(OUT/'component.json').write_text(json.dumps(component,indent=2)+'\n',encoding='utf-8')
print(json.dumps(component),flush=True)
