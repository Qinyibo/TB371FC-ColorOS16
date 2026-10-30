from pathlib import Path
import sys,json,hashlib,zipfile,copy,zlib,struct
source=Path(sys.argv[1]);output=Path(sys.argv[2]);assert source.resolve()!=output.resolve()
assert hashlib.sha256(source.read_bytes()).hexdigest()=='fbbac634895ef14c8168d3b955f5eb7ca11499b447d4f994f71cb137bcfc38f3'
r=json.loads(Path(__file__).with_name('surface-guard.json').read_text(encoding='utf-8'))
with zipfile.ZipFile(source) as original,zipfile.ZipFile(output,'w') as out:
 b=bytearray(original.read('classes.dex'));at=r['instruction_offset'];old=bytes.fromhex(r['instruction_before']);new=bytes.fromhex(r['instruction_after']);assert b[at:at+len(old)]==old;b[at:at+len(new)]=new
 b[12:32]=hashlib.sha1(b[32:]).digest();struct.pack_into('<I',b,8,zlib.adler32(b[12:])&0xffffffff)
 for info in original.infolist():out.writestr(copy.copy(info),bytes(b) if info.filename=='classes.dex' else original.read(info.filename))
print(hashlib.sha256(output.read_bytes()).hexdigest())
