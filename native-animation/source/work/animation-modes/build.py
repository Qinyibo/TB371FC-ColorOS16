from pathlib import Path
import subprocess,zipfile,re,hashlib,json,sys,struct,zlib,io
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
W=Path(__file__).resolve().parent;ROOT=W.parent.parent;sys.path.insert(0,str(W.parent))
from apk_dex_replace import replace_dex
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk');B=W/'build';B.mkdir(exist_ok=True)
SDK=S/'platforms/android-36/android.jar';BT=S/'build-tools/36.0.0'
def run(args,name):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=180)
 log=(p.stdout+p.stderr).decode('utf-8','replace');(B/(name+'.log')).write_text(log,encoding='utf-8')
 if p.returncode:raise RuntimeError(name+'\n'+log[-4000:])
 return log
def append_dex(raw,name,data):
 # Preserve original signer identity and existing native-library offsets.
 tail=raw.rfind(b'PK\x05\x06');sz,off=struct.unpack_from('<II',raw,tail+12)
 assert raw[off-16:off]==b'APK Sig Block 42'
 sigstart=off-(struct.unpack_from('<Q',raw,off-24)[0]+8)
 buf=io.BytesIO()
 with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:z.writestr(name,data)
 extra=buf.getvalue();e=extra.rfind(b'PK\x05\x06');cs,co=struct.unpack_from('<II',extra,e+12)
 local=extra[:co];central=bytearray(extra[co:co+cs]);struct.pack_into('<I',central,42,sigstart)
 ending=bytearray(raw[tail:]);entries=struct.unpack_from('<H',ending,10)[0]+1
 struct.pack_into('<HHII',ending,8,entries,entries,sz+len(central),off+len(local))
 return raw[:sigstart]+local+raw[sigstart:off]+raw[off:off+sz]+central+ending
libs=[p for p in(S/'cmdline-tools/latest/lib').rglob('*.jar')if any(k in str(p)for k in['smali','guava','failureaccess'])]
cp=';'.join(map(str,libs));P=B/'patcher';P.mkdir(exist_ok=True)
run([J/'javac.exe','-cp',cp,'-d',P,W/'AnimationDexPatch.java'],'patcher')
stubs=B/'stubs';stubs.mkdir(exist_ok=True)
run([J/'javac.exe','--release','8','-cp',SDK,'-d',stubs,*list((W/'stubs').rglob('*.java'))],'stubs')
stubjar=B/'stubs.jar'
with zipfile.ZipFile(stubjar,'w')as z:
 for p in stubs.rglob('*.class'):z.write(p,p.relative_to(stubs).as_posix())
payloads={}
for mode,src in [('settings','AnimationSettings.java'),('launcher','LauncherCompat.java')]:
 C=B/(mode+'-classes');C.mkdir(exist_ok=True)
 run([J/'javac.exe','--release','8','-cp',str(SDK)+';'+str(stubjar),'-d',C,W/'src/org/tb371fc/animation'/src],mode+'-javac')
 jar=B/(mode+'-helper.jar')
 with zipfile.ZipFile(jar,'w')as z:
  for p in C.rglob('*.class'):z.write(p,p.relative_to(C).as_posix())
 D=B/(mode+'-dex');D.mkdir(exist_ok=True)
 run([BT/'d8.bat','--min-api','35','--lib',SDK,'--classpath',stubjar,'--output',D,jar],mode+'-d8')
 payloads[mode]=(D/'classes.dex').read_bytes()
sources={'launcher':Path('D:/TB371FC-work/codex-20261028/Launcher-live-20261030.apk'),'settings':Path('D:/TB371FC-work/codex-20261028/Settings-live-20261030.apk'),'assistant':W/'inputs/AssistantScreen-live.apk'}
rows=json.loads((B/'result.json').read_text())if(B/'result.json').exists()else{}
for mode,source in sources.items():
 if len(sys.argv)>1 and mode not in sys.argv[1:]:continue
 T=B/mode;T.mkdir(exist_ok=True);raw=source.read_bytes();changed=[];count=0;moved=[]
 with zipfile.ZipFile(source)as z:
  names=[n for n in z.namelist()if re.fullmatch(r'classes\d*\.dex',n)]
  for n in names:
   inp=T/n;inp.write_bytes(z.read(n));out=T/(n+'.patched')
   log=run([J/'java.exe','-cp',str(P)+';'+cp,'AnimationDexPatch',inp,out,mode],mode+'-'+n)
   edits=int(re.search(r'PATCHED (\d+)',log)[1]);count+=edits
   if edits:
    raw=replace_dex(raw,n,out.read_bytes());changed.append(n);print(log.strip(),flush=True)
    if mode!='assistant':moved.append(Path(str(out)+'.moved').read_bytes())
  if mode in payloads:moved.append(payloads[mode])
  nextdex=max(1 if n=='classes.dex'else int(re.search(r'\d+',n)[0])for n in names)+1
  for data in moved:
   extra='classes'+str(nextdex)+'.dex';nextdex+=1
   raw=append_dex(raw,extra,data);changed.append(extra)
  target=T/(source.name.replace('-live-20261030','').replace('-live',''))
  target.write_bytes(raw)
  with zipfile.ZipFile(target)as dest:
   assert dest.testzip()is None
   for e in z.infolist():
    if e.filename not in changed:assert dest.read(e.filename)==z.read(e.filename),e.filename
  run([BT/'zipalign.exe','-c','-P','4','4',target],mode+'-alignment')
  assert count>0,mode
  rows[mode]={'source':str(source),'target':str(target),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(raw).hexdigest(),'edits':count,'dex':changed}
(B/'result.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
