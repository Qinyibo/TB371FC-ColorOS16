import copy
import hashlib
import pathlib
import subprocess
import sys
import zipfile

BASE_SHA256 = 'ab25a362ff81a90c69dfa55ceaa3a2ae201775bd339abb04da5b1c2b71330467'
W = pathlib.Path(__file__).resolve().parent
base = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
assert hashlib.sha256(base.read_bytes()).hexdigest() == BASE_SHA256, 'unexpected base framework'
out.mkdir(parents=True, exist_ok=True)
jdk = pathlib.Path('C:/Program Files/Java/jdk-21/bin')
sdk = pathlib.Path('C:/android-sdk')
libraries = [p for p in (sdk / 'cmdline-tools/latest/lib').rglob('*.jar') if any(k in str(p) for k in ['smali', 'guava', 'failureaccess'])]
cp = ';'.join(str(p) for p in libraries)
assert libraries, 'Android SDK dexlib2 dependencies missing'
subprocess.run([str(jdk / 'javac.exe'), '-cp', cp, '-d', str(out), str(W / 'ChargerCompatPatch.java')], check=True)
with zipfile.ZipFile(base) as source:
    assert source.testzip() is None
    (out / 'before.dex').write_bytes(source.read('classes.dex'))
    subprocess.run([str(jdk / 'java.exe'), '-cp', str(out) + ';' + cp, 'ChargerCompatPatch',
                    str(out / 'before.dex'), str(out / 'classes.dex'), str(out / 'focused.dex'), str(out / 'original-focused.dex')], check=True)
    target = out / 'oplus-services.charger-compat.jar'
    assert target != base
    with zipfile.ZipFile(target, 'w') as dest:
        for item in source.infolist():
            payload = (out / 'classes.dex').read_bytes() if item.filename == 'classes.dex' else source.read(item)
            dest.writestr(copy.copy(item), payload)
    with zipfile.ZipFile(target) as result:
        assert result.testzip() is None
        assert result.namelist() == source.namelist()
        assert all(result.read(n) == source.read(n) for n in source.namelist() if n != 'classes.dex')
print(hashlib.sha256(target.read_bytes()).hexdigest(), target)
