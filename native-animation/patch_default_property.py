"""Patch the factory default in the final OEM property layer; keep user choices."""
import hashlib
from pathlib import Path
import sys

INPUT_SHA256 = '18a97f39d6334bb734ede32891d33c1320e793cf60bc448f43000afa07916d91'
KEY = b'persist.sys.oplus.anim_level='

def patch(data):
    if hashlib.sha256(data).hexdigest() != INPUT_SHA256:
        raise ValueError('Unexpected /my_manifest/build.prop input')
    before = KEY + b'2\n'
    if data.count(before) != 1:
        raise ValueError('Expected exactly one factory animation default')
    return data.replace(before, KEY + b'4\n', 1)

if __name__ == '__main__':
    source, output = map(Path, sys.argv[1:])
    if output.exists():
        raise FileExistsError(output)
    output.write_bytes(patch(source.read_bytes()))
