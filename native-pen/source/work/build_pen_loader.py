from pathlib import Path
import subprocess,zipfile,hashlib,struct,gzip,json,sys
W=Path(__file__).resolve().parent; O=W.parent/'inputs/pen-native-v1'
A=W/(sys.argv[1] if len(sys.argv)>1 else 'pen-loader-v2');A.mkdir(parents=True,exist_ok=True)
target_root=Path(sys.argv[2]) if len(sys.argv)>2 else O/'system-assets-v4/host-generated'
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p.stdout.decode('utf-8','replace')
props={}; stats={}
for k,pkg,name,srcpath in [('ipe','com.oplus.ipemanager','IPeManager.apk','/my_product/priv-app/IPeManager/IPeManager.apk'),('ws','com.oplus.wirelesssettings','WirelessSettings.apk','/system_ext/priv-app/WirelessSettings/WirelessSettings.apk')]:
 original=O/'runtime-contract-v1'/(pkg+'.apk'); target=target_root/k/name
 ob=original.read_bytes();tb=target.read_bytes(); copied=0
 def payload(raw,e):
  off=e.header_offset;nl,el=struct.unpack_from('<HH',raw,off+26);start=off+30+nl+el
  return start,raw[start:start+e.compress_size]
 with zipfile.ZipFile(original) as oz,zipfile.ZipFile(target) as tz:
  source={e.filename:e for e in oz.infolist()}; spans=[]
  for e in tz.infolist():
   if e.filename not in source:continue
   ts,tdata=payload(tb,e);os,odata=payload(ob,source[e.filename])
   if len(tdata)>16 and tdata==odata:spans.append((ts,os,len(tdata)))
 recipe=bytearray(b'R94PEN02');cursor=0
 for ts,os,length in sorted(spans):
  if cursor<ts:lit=tb[cursor:ts];recipe+=b'\2'+struct.pack('>Q',len(lit))+lit
  recipe+=b'\1'+struct.pack('>QQ',os,length);copied+=length;cursor=ts+length
 if cursor<len(tb):lit=tb[cursor:];recipe+=b'\2'+struct.pack('>Q',len(lit))+lit
 recipe+=b'\0';packed=gzip.compress(recipe,mtime=0);(A/(k+'.recipe.gz')).write_bytes(packed)
 props.update({k+'.source':srcpath,k+'.sourceName':original.name,k+'.sourceSha':sha(ob),k+'.name':name,k+'.outputSha':sha(tb),k+'.outputSize':str(len(tb)),k+'.recipeSha':sha(packed)})
 stats[k]={'source_bytes':len(ob),'target_bytes':len(tb),'copied_bytes':copied,'recipe_bytes':len(packed),'expected_sha256':sha(tb)}
(A/'manifest.properties').write_text('\n'.join(k+'='+v for k,v in sorted(props.items()))+'\n',encoding='ascii',newline='\n')
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk')
C=A/'classes';C.mkdir(exist_ok=True);run([J/'javac.exe','--release','8','-d',C,W/'NativePayloadV2.java'])
jar=A/'classes.jar'
with zipfile.ZipFile(jar,'w')as z:
 for p in C.rglob('*.class'):z.write(p,p.relative_to(C).as_posix())
D=A/'dex';D.mkdir(exist_ok=True);run([S/'build-tools/36.0.0/d8.bat','--min-api','35','--output',D,jar])
with zipfile.ZipFile(A/'bootstrap.jar','w')as z:z.write(D/'classes.dex','classes.dex')
print(run([J/'java.exe','-cp',C,'org.tb371fc.pen.NativePayloadV2',A,A/'host-cache',O/'runtime-contract-v1']))
print(json.dumps(stats,indent=2));(A/'build-result.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
