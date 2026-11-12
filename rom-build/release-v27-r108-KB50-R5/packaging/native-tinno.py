"""Update the Tinno VINTF pair in a private copy of the R3 vendor image."""
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re
import runpy
import shutil
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


VENDOR_HASH = '78959e36b12aebb30996a94fbe4cf3e4ed53bfb57f2aacdc3c37544494d2ac1b'
MODULE_HASH = '16e3f4ff045d824482efcd5ce92251129a8fcb2326f38bc36978ad6cf3ab2078'
OLD_NAME = b'vendor.mediatek.hardware.tinno_keyboard'
NEW_NAME = b'vendor.qti.hardware.tinno_keyboard'
SERVICE = NEW_NAME.decode() + '@1.0-service'
MATRIX = '/etc/vintf/compatibility_matrix.xml'
FRAGMENT = f'/etc/vintf/manifest/{SERVICE}.xml'
Image = runpy.run_path(str(Path(__file__).with_name('edit-images.py')))['Image']


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def main():
    vendor = Path('vendor.img')
    assert not vendor.exists()
    with open('/dev/vdd', 'rb') as source, vendor.open('xb') as output:
        shutil.copyfileobj(source, output, 8 << 20)
    assert digest(vendor) == VENDOR_HASH
    module = Path('tinno.zip')
    assert digest(module) == MODULE_HASH
    with TemporaryDirectory() as temp, ZipFile(module) as reference:
        scratch = Path(temp)
        image = Image(vendor, scratch)
        old = image.read(MATRIX).read_bytes()
        assert old.count(OLD_NAME) == 1 and NEW_NAME not in old
        matrix = old.replace(OLD_NAME, NEW_NAME, 1)
        assert matrix == reference.read('system/vendor' + MATRIX)
        matrix_hal = [node for node in ET.fromstring(matrix).findall('hal')
                      if node.findtext('name') == NEW_NAME.decode()]
        assert len(matrix_hal) == 1 and matrix_hal[0].get('optional') == 'true'

        fragment = scratch / 'tinno.xml'
        fragment.write_bytes(reference.read('system/vendor' + FRAGMENT))
        fragment_hash = digest(fragment)
        hal = ET.parse(fragment).getroot().find('hal')
        assert hal.findtext('name') == NEW_NAME.decode()
        assert hal.findtext('version') == '1.0'
        assert hal.findtext('interface/name') == 'ITinnoKeyBoard'
        assert hal.findtext('interface/instance') == 'default'
        service_hashes = {}
        for path in (f'/bin/hw/{SERVICE}', f'/etc/init/{SERVICE}.rc'):
            service_hashes[path] = digest(image.read(path))

        listing = image.debugfs('ls -p /etc/vintf/manifest')
        sibling = next(row.split('/')[5] for row in listing.splitlines()
                       if re.match(r'/\d+/100644/', row) and row.split('/')[5].endswith('.xml'))
        context_file = scratch / 'sibling-context'
        image.debugfs(f'ea_get -f {context_file} /etc/vintf/manifest/{sibling} security.selinux')
        context = context_file.read_bytes()
        assert context.startswith(b'u:object_r:') and context.endswith(b'\0')

        image.replace(MATRIX, matrix, 0o100644)
        image.put(fragment, FRAGMENT, label=context)
        assert image.read(MATRIX).read_bytes() == matrix
        assert image.read(FRAGMENT).read_bytes() == fragment.read_bytes()
        for path, expected in service_hashes.items():
            assert digest(image.read(path)) == expected

    subprocess.run(['/usr/sbin/e2fsck', '-fn', str(vendor)], check=True)
    report = {
        'baseline_sha256': VENDOR_HASH,
        'vendor_sha256': digest(vendor),
        'vendor_bytes': vendor.stat().st_size,
        'files': {MATRIX: sha256(matrix).hexdigest(), FRAGMENT: fragment_hash},
        'service_files': service_hashes,
        'filesystem_check': 'e2fsck -fn passed',
    }
    Path('tinno-verification.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
