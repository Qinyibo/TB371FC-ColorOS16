"""Build the deployed API19 companion; does not package or install it."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jdk', type=Path, required=True)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    cc = args.ndk / 'toolchains/llvm/prebuilt/windows-x86_64/bin/aarch64-linux-android30-clang.cmd'
    android = args.sdk / 'platforms/android-36/android.jar'
    d8 = args.sdk / 'build-tools/36.0.0/lib/d8.jar'
    javac = args.jdk / 'bin/javac.exe'
    java = args.jdk / 'bin/java.exe'
    for tool in [cc, android, d8, javac, java]:
        if not tool.is_file():
            parser.error(f'Missing build input: {tool}')

    def run(command):
        subprocess.run(list(map(str, command)), check=True)

    for name, flags in [('direction.so', ['-shared', '-fPIC']), ('directionctl', ['-DR94_CLI'])]:
        run([cc, '-O2', '-Wall', '-Wextra', '-Werror', *flags,
             source / 'route_jni.c', '-o', output / name])
    with tempfile.TemporaryDirectory(prefix='tb371fc-speaker-') as temporary:
        classes = Path(temporary)
        run([javac, '-source', '8', '-target', '8', '-classpath', android,
             '-d', classes, source / 'R94SpeakerDirection.java'])
        run([java, '-cp', d8, 'com.android.tools.r8.D8', '--min-api', '31',
             '--lib', android, '--output', output / 'direction.jar',
             *classes.glob('*.class')])
    hashes = {name: hashlib.sha256((output / name).read_bytes()).hexdigest()
              for name in ['direction.jar', 'direction.so', 'directionctl']}
    (output / 'sha256.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(hashes, indent=2))


if __name__ == '__main__':
    main()
