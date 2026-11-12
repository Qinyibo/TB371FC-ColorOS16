from pathlib import Path
import hashlib,json,subprocess,sys,zipfile
b=Path(sys.argv[2]).resolve();b.mkdir(parents=True,exist_ok=True)
source=Path(sys.argv[1]).resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='56bc35af0c908ec00151ec792f3df048985d1cf0db06260b6a86f42614d76928','Unexpected SystemUI base'
jdk=Path('C:/Program Files/Java/jdk-21/bin')
libs=[p for p in Path('C:/android-sdk/cmdline-tools/latest/lib').rglob('*.jar') if any(k in str(p).lower() for k in ('smali','guava','failureaccess'))]
assert libs
cp=';'.join(map(str,libs))
subprocess.run([str(jdk/'javac.exe'),'-cp',cp,'-d',str(b),str(Path(__file__).with_name('CancelSnapshotPatch.java'))],check=True)
subprocess.run([str(jdk/'java.exe'),'-cp',str(b)+';'+cp,'CancelSnapshotPatch',str(source),str(b)],check=True)
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'source/work'))
from apk_dex_replace import replace_dex
name=(b/'dex-name.txt').read_text();raw=replace_dex(source.read_bytes(),name,(b/'candidate.dex').read_bytes())
target=b/'SystemUI-cancel-snapshots-r1.apk'
assert not target.exists(),'Use a new output directory'
target.write_bytes(raw)
with zipfile.ZipFile(source) as old,zipfile.ZipFile(target) as new:
 assert new.testzip() is None and old.namelist()==new.namelist()
 changed=[n for n in old.namelist() if old.read(n)!=new.read(n)]
 assert changed==[name],changed
print(json.dumps(dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),changed_payloads=changed,output=str(target)),indent=2))
