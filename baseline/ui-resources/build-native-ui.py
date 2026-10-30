from pathlib import Path
import zipfile,struct,subprocess,re,json,hashlib,time,sys
O=Path(__file__).parent/'ui-resources';D=O/'native';D.mkdir(exist_ok=True)
assert not (D/'result.json').exists()
import os
password='pass:'+os.environ['TB371FC_SIGN_KEY_PASSWORD']
key=Path(os.environ['TB371FC_SIGN_KEYSTORE'])
sdk=Path(os.environ.get('ANDROID_BUILD_TOOLS','C:/android-sdk/build-tools/36.0.0'))

def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True)
 if p.returncode:raise RuntimeError('Android packaging/signature step failed: '+(p.stdout+p.stderr).decode('utf-8','replace')[-1200:])
 return p.stdout.decode('utf-8','replace')
def strings(b,p):
 _,header,size,count,styles,flags,start,styleStart=struct.unpack_from('<HHIIIIII',b,p)
 offsets=struct.unpack_from('<'+'I'*count,b,p+header);values=[]
 for offset in offsets:
  q=p+start+offset
  def u8length(q):
   n=b[q];return ((n&127)<<8|b[q+1],q+2) if n&128 else (n,q+1)
  if flags&256:
   chars,q=u8length(q);length,q=u8length(q);values.append(bytes(b[q:q+length]).decode('utf-8'))
  else:
   n=struct.unpack_from('<H',b,q)[0];q+=2
   if n&32768:n=(n&32767)<<16|struct.unpack_from('<H',b,q)[0];q+=2
   values.append(bytes(b[q:q+n*2]).decode('utf-16le'))
 return values
rows=[]
for row in json.loads((O/'inspection.json').read_text())['rows']:
 name=row['name'];old=O/name;unsigned=D/(name+'.unsigned');aligned=D/(name+'.aligned');signed=D/name
 with zipfile.ZipFile(old) as z:
  manifest=bytearray(z.read('AndroidManifest.xml'));p=8;pool=None;changes=0
  while p<len(manifest):
   kind,header,size=struct.unpack_from('<HHI',manifest,p)
   if kind==1:pool=strings(manifest,p)
   elif kind==0x102:
    ns,element,start,attrsize,count=struct.unpack_from('<IIHHH',manifest,p+16)
    if pool[element]=='overlay':
     for i in range(count):
      a=p+16+start+i*attrsize;attrName=struct.unpack_from('<I',manifest,a+4)[0]
      if pool[attrName]=='isStatic':
       assert manifest[a+15]==0x12 and struct.unpack_from('<I',manifest,a+16)[0]==0
       struct.pack_into('<I',manifest,a+16,0xffffffff);changes+=1
   assert size>=header and size>0;p+=size
  assert changes==1
  with zipfile.ZipFile(unsigned,'w') as out:
   for e in z.infolist():out.writestr(e,bytes(manifest) if e.filename=='AndroidManifest.xml' else z.read(e.filename))
 run([sdk/'zipalign.exe','-f','4',unsigned,aligned])
 run([sdk/'apksigner.bat','sign','--ks',key,'--ks-pass',password,'--out',signed,aligned])
 sig=run([sdk/'apksigner.bat','verify','--verbose','--print-certs',signed])
 assert '573041437424dd6923e043a34b8088fa86abd63c221fe420755210da4798c688' in sig
 xml=run([sdk/'aapt2.exe','dump','xmltree',signed,'--file','AndroidManifest.xml'])
 assert re.search(r'isStatic.*=true',xml)
 run([sdk/'zipalign.exe','-c','4',signed])
 with zipfile.ZipFile(old) as a,zipfile.ZipFile(signed) as b:
  for n in a.namelist():
   if n!='AndroidManifest.xml' and not n.startswith('META-INF/'):assert a.read(n)==b.read(n),(name,n)
 rows.append({'name':name,'original_sha256':row['sha256'],'native_sha256':hashlib.sha256(signed.read_bytes()).hexdigest(),'native_bytes':signed.stat().st_size,'same_own_signer':True,'all_resources_byte_identical':True,'default_enabled_static_manifest':True,'manifest':xml})
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
save(D/'result.json',{'time':time.time(),'state':'SIGNED_NATIVE_DEFAULT_RROS_BUILT_NOT_DEPLOYED','rows':rows,'changed_existing_oem_partition_config':False,'no_global_signature_relaxation':True,'no_runtime_enable_script_needed_for_native_defaults':True})
print(json.dumps({'state':'Built three signed native default resource overlays','rows':[{k:r[k] for k in ('name','native_sha256','native_bytes','same_own_signer','all_resources_byte_identical')} for r in rows]},ensure_ascii=False,indent=2))
