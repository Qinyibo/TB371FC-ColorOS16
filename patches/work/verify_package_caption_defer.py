import pathlib,struct,zlib,hashlib,json,zipfile,re
from loguru import logger
logger.remove()
from androguard.core.dex import DEX
p=pathlib.Path('work/systemui-caption-defer');old=p.joinpath('classes2-original.dex').read_bytes();new=p.joinpath('classes2-candidate.dex').read_bytes()
assert hashlib.sha1(new[32:]).digest()==new[12:32]
assert zlib.adler32(new[12:])&0xffffffff==struct.unpack_from('<I',new,8)[0]
def methods(b):
 d=DEX(b);out={}
 for c in d.get_classes():
  for m in c.get_methods():
   ins=list(m.get_instructions_idx());indices={off:i for i,(off,it) in enumerate(ins)};items=[]
   for off,it in ins:
    n=it.get_name();ops=[]
    for op in it.get_operands():
     typ=int(op[0])
     if typ==3:ops.append(('target',indices.get(off+op[1]*2,off+op[1]*2)))
     elif len(op)>2:ops.append((typ,str(op[-1])))
     else:ops.append((typ,op[1]))
    if n=='const-string/jumbo':n='const-string'
    if n.startswith('goto'):n='goto'
    if n.endswith('payload'):ops.append(('payload',it.get_output()))
    items.append((n,ops))
   out[c.get_name()+'->'+m.get_name()+m.get_descriptor()]=items
 return out
x=methods(old);y=methods(new);changed=[k for k in x.keys()|y.keys() if x.get(k)!=y.get(k)]
C='Lcom/android/wm/shell/windowdecor/viewholder/FullscreenCaptionHandleViewHolder;'
unexpected=[k for k in changed if not k.startswith(C+'->')]
print('changed methods',len(changed),'unexpected',len(unexpected));print('\n'.join(sorted(changed)[:18]))
if unexpected:
 print('First unexpected old/new',unexpected[0],x.get(unexpected[0]),y.get(unexpected[0]));raise RuntimeError('semantic difference outside targeted holder')
# Rebuild the one ZIP entry while retaining original bytes and signer block.
base=pathlib.Path(r'D:\TB371FC-work\codex-20261028');src=base/'SystemUI-live-20261029.apk';raw=src.read_bytes();z=zipfile.ZipFile(src);eocd=raw.rfind(b'PK\x05\x06');cdsize,cdoff=struct.unpack_from('<II',raw,eocd+12)
assert raw[cdoff-16:cdoff]==b'APK Sig Block 42'
sigsz=struct.unpack_from('<Q',raw,cdoff-24)[0]+8;sigstart=cdoff-sigsz;sig=raw[sigstart:cdoff]
info=z.getinfo('classes2.dex');off=info.header_offset;header=bytearray(raw[off:off+30]);flags,method=struct.unpack_from('<HH',header,6);nl,el=struct.unpack_from('<HH',header,26)
assert method in (0,8)
co=zlib.compressobj(6,zlib.DEFLATED,-15);comp=(co.compress(new)+co.flush()) if method==8 else new;crc=zlib.crc32(new)&0xffffffff
extra=raw[off+30:off+30+nl+el];end=off+30+nl+el+info.compress_size
if flags&8:
 desc=raw[end:end+4]==b'PK\x07\x08';end+=16 if desc else 12
 descriptor=(b'PK\x07\x08' if desc else b'')+struct.pack('<III',crc,len(comp),len(new))
else:descriptor=b''
struct.pack_into('<III',header,14,crc,len(comp),len(new))
local=bytes(header)+extra+comp+descriptor
padding=(-(len(local)-(end-off)))%4096
local+=bytes(padding)
delta=len(local)-(end-off)
assert delta%4096==0
cd=bytearray(raw[cdoff:cdoff+cdsize]);at=0
while at<len(cd):
 assert cd[at:at+4]==b'PK\x01\x02'
 namesz,exsz,commentsz=struct.unpack_from('<HHH',cd,at+28);name=bytes(cd[at+46:at+46+namesz]).decode('utf-8');entryoff=struct.unpack_from('<I',cd,at+42)[0]
 if name=='classes2.dex':struct.pack_into('<III',cd,at+16,crc,len(comp),len(new))
 if entryoff>off:struct.pack_into('<I',cd,at+42,entryoff+delta)
 at+=46+namesz+exsz+commentsz
ending=bytearray(raw[eocd:]);struct.pack_into('<I',ending,16,cdoff+delta)
result=raw[:off]+local+raw[end:sigstart]+sig+bytes(cd)+bytes(ending)
out=p/'SystemUI-caption-defer-candidate.apk';out.write_bytes(result);q=zipfile.ZipFile(out);assert q.testzip() is None
payload_changed=[i.filename for i in z.infolist() if hashlib.sha256(z.read(i.filename)).digest()!=hashlib.sha256(q.read(i.filename)).digest()]
assert payload_changed==['classes2.dex'],payload_changed
for ent in q.infolist():
 if ent.filename.startswith('lib/') and ent.filename.endswith('.so') and ent.compress_type==0:
  nl,el=struct.unpack_from('<HH',result,ent.header_offset+26)
  assert (ent.header_offset+30+nl+el)%4096==0,ent.filename
report={'status':'OFFLINE_ONLY_NOT_DEPLOYED','candidate_apk_sha256':hashlib.sha256(result).hexdigest(),'base_apk_sha256':hashlib.sha256(raw).hexdigest(),'changed_zip_payloads':payload_changed,'changed_methods':sorted(changed),'unexpected_semantic_method_changes':unexpected,'dex_header_checksums_valid':True,'zip_crc_valid':True,'original_signer_block_sha256':hashlib.sha256(sig).hexdigest(),'original_signer_block_preserved':True,'apk_full_signature_integrity':'ORIGINAL_ALREADY_INVALID; signer block retained; runtime system APK loading NOT TESTED','delay_ms':400}
(p/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('OFFLINE_CANDIDATE_OK',len(result),'bytes')
