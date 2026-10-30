import zipfile,struct,zlib,io
def replace_dex(raw,name,new):
 z=zipfile.ZipFile(io.BytesIO(raw));eocd=raw.rfind(b'PK\x05\x06');cdsize,cdoff=struct.unpack_from('<II',raw,eocd+12)
 assert raw[cdoff-16:cdoff]==b'APK Sig Block 42'
 sigsz=struct.unpack_from('<Q',raw,cdoff-24)[0]+8;sigstart=cdoff-sigsz
 info=z.getinfo(name);off=info.header_offset;header=bytearray(raw[off:off+30]);flags,method=struct.unpack_from('<HH',header,6);nl,el=struct.unpack_from('<HH',header,26)
 assert method in (0,8)
 co=zlib.compressobj(6,zlib.DEFLATED,-15);comp=co.compress(new)+co.flush() if method==8 else new;crc=zlib.crc32(new)&0xffffffff
 extra=raw[off+30:off+30+nl+el];end=off+30+nl+el+info.compress_size
 if flags&8:
  desc=raw[end:end+4]==b'PK\x07\x08';end+=16 if desc else 12
  descriptor=(b'PK\x07\x08' if desc else b'')+struct.pack('<III',crc,len(comp),len(new))
 else:descriptor=b''
 struct.pack_into('<III',header,14,crc,len(comp),len(new));local=bytes(header)+extra+comp+descriptor
 local+=bytes((-(len(local)-(end-off)))%4096);delta=len(local)-(end-off);assert delta%4096==0
 cd=bytearray(raw[cdoff:cdoff+cdsize]);at=0
 while at<len(cd):
  assert cd[at:at+4]==b'PK\x01\x02'
  namesz,exsz,commentsz=struct.unpack_from('<HHH',cd,at+28);entry=bytes(cd[at+46:at+46+namesz]).decode();entryoff=struct.unpack_from('<I',cd,at+42)[0]
  if entry==name:struct.pack_into('<III',cd,at+16,crc,len(comp),len(new))
  if entryoff>off:struct.pack_into('<I',cd,at+42,entryoff+delta)
  at+=46+namesz+exsz+commentsz
 ending=bytearray(raw[eocd:]);struct.pack_into('<I',ending,16,cdoff+delta)
 return raw[:off]+local+raw[end:sigstart]+raw[sigstart:cdoff]+bytes(cd)+bytes(ending)
