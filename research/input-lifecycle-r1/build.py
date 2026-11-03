"""Build a bounded Launcher cleanup candidate without touching a device."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import zipfile

SOURCE = Path(__file__).resolve().parent
BASE = Path(sys.argv[1]).resolve()
BUILD = Path(sys.argv[2]).resolve()
JAVA = Path('C:/Program Files/Java/jdk-21/bin')
EXPECTED = 'bdd74a3218e51a2b0a19d66bed5dae1d53c7b7794038bd1835b801c070a28b9d'
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == EXPECTED, 'Wrong Launcher baseline'
assert not BUILD.exists(), 'Preserve previous candidate and evidence'
BUILD.mkdir(parents=True)
compiler = BUILD/'compiler'
compiler.mkdir()
libs = [p for p in Path('C:/android-sdk/cmdline-tools/latest/lib').rglob('*.jar')
        if any(key in str(p).lower() for key in ('smali','guava','failureaccess'))]
cp = ';'.join(map(str, libs))
subprocess.run([str(JAVA/'javac.exe'), '-cp', cp, '-d', str(compiler),
                str(SOURCE/'InputLifecyclePatch.java'), str(SOURCE/'VerifyDex.java')], check=True)
subprocess.run([str(JAVA/'java.exe'), '-cp', str(compiler)+';'+cp,
                'InputLifecyclePatch', str(BASE), str(BUILD)], check=True)
sys.path.insert(0, str(SOURCE.parent/'source/work'))
from apk_dex_replace import replace_dex
name = (BUILD/'dex-name.txt').read_text(encoding='utf-8')
raw = replace_dex(BASE.read_bytes(), name, (BUILD/'candidate.dex').read_bytes())
target = BUILD/'OplusLauncher-input-lifecycle-r1.apk'
target.write_bytes(raw)
with zipfile.ZipFile(BASE) as before, zipfile.ZipFile(target) as after:
    assert before.namelist() == after.namelist()
    changed = [entry for entry in before.namelist() if before.read(entry) != after.read(entry)]
    assert changed == [name], changed
    assert after.testzip() is None
comparison = subprocess.run([str(JAVA/'java.exe'), '-cp', str(compiler)+';'+cp,
    'VerifyDex', str(BASE), str(target), name], capture_output=True, check=True)
(BUILD/'final-apk-method-comparison.txt').write_bytes(comparison.stdout+comparison.stderr)
print(comparison.stdout.decode(errors='replace'), flush=True)
record = dict(state='CANDIDATE_BUILT_REGRESSION_PENDING', source_sha256=EXPECTED,
    candidate_sha256=hashlib.sha256(raw).hexdigest(), candidate_bytes=len(raw),
    changed_apk_entries=changed, changed_methods=1,
    change='resetState: timeout-absent return -> existing unconditional cleanup',
    new_retry_or_polling=False, kernel_modified=False, device_modified=False,
    reported_interaction_failure_root_cause_proven=False, device_fix_claimed=False)
(BUILD/'build-result.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(json.dumps(record), flush=True)
