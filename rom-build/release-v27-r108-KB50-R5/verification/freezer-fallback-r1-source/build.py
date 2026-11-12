import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile

BASE_SHA256 = 'e73be401835ecede505e6c37c75c007a8f5bd840d9441fe0a99b3f5320c3e3a9'
source = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest() == BASE_SHA256, 'unexpected framework base'
out.mkdir(parents=True, exist_ok=True)
target = out / 'oplus-services.freezer-fallback.jar'
assert not target.exists(), 'existing candidate; use a new output directory'
jdk = Path('C:/Program Files/Java/jdk-21/bin')
libraries = [p for p in Path('C:/android-sdk/cmdline-tools/latest/lib').rglob('*.jar')
             if any(k in str(p).lower() for k in ('smali', 'guava', 'failureaccess'))]
assert libraries
cp = ';'.join(str(p) for p in libraries)
subprocess.run([str(jdk / 'javac.exe'), '-cp', cp, '-d', str(out),
                str(Path(__file__).with_name('FreezerFallbackPatch.java'))], check=True)
with zipfile.ZipFile(source) as archive:
    assert archive.testzip() is None
    (out / 'before.dex').write_bytes(archive.read('classes.dex'))
    subprocess.run([str(jdk / 'java.exe'), '-cp', str(out) + ';' + cp, 'FreezerFallbackPatch',
                    str(out / 'before.dex'), str(out / 'classes.dex'), str(out / 'focused.dex'),
                    str(out / 'original-focused.dex')], check=True)
    with zipfile.ZipFile(target, 'w') as result:
        for entry in archive.infolist():
            data = (out / 'classes.dex').read_bytes() if entry.filename == 'classes.dex' else archive.read(entry)
            result.writestr(copy.copy(entry), data)
    with zipfile.ZipFile(target) as result:
        assert result.testzip() is None
        assert result.namelist() == archive.namelist()
        assert all(result.read(n) == archive.read(n) for n in archive.namelist() if n != 'classes.dex')
for name, dex in [('candidate-focused.jar', 'focused.dex'), ('old-focused.jar', 'original-focused.dex')]:
    with zipfile.ZipFile(out / name, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(out / dex, 'classes.dex')
print(hashlib.sha256(target.read_bytes()).hexdigest(), target)
