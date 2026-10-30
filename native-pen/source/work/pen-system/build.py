from pathlib import Path
import subprocess,zipfile,hashlib,re,json,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
W=Path(__file__).resolve().parent;B=W/'build';B.mkdir(exist_ok=True);S=Path('C:/android-sdk');J=Path('C:/Program Files/Java/jdk-21/bin')
def run(a,name):
 p=subprocess.run(list(map(str,a)),capture_output=True,timeout=120);out=(p.stdout+p.stderr).decode('utf-8','replace');(B/(name+'.log')).write_text(out,encoding='utf-8')
 if p.returncode:raise RuntimeError(name+'\n'+out[-2500:])
 return out
C=B/'classes';C.mkdir(exist_ok=True);src=list((W/'src').rglob('*.java'))+list((W/'stubs').rglob('*.java'))
run([J/'javac.exe','--release','8','-cp',S/'platforms/android-36/android.jar','-d',C,*src],'javac')
jar=B/'helper-classes.jar'
with zipfile.ZipFile(jar,'w')as z:
 for p in (C/'org').rglob('*.class'):z.write(p,p.relative_to(C).as_posix())
D=B/'dex';D.mkdir(exist_ok=True);run([S/'build-tools/36.0.0/d8.bat','--min-api','35','--lib',S/'platforms/android-36/android.jar','--output',D,jar],'d8')
libs=[p for p in(S/'cmdline-tools/latest/lib').rglob('*.jar')if any(k in str(p)for k in['smali','guava','failureaccess'])];cp=';'.join(map(str,libs));P=B/'patcher';P.mkdir(exist_ok=True)
run([J/'javac.exe','-cp',cp,'-d',P,W/'ServicesPenPatch.java'],'patcher')
source=W.parent/'pen-v3/services-live.jar';target=B/'services.jar';replacements={};count=0;checks={}
with zipfile.ZipFile(source)as z:
 names=[n for n in z.namelist()if re.fullmatch(r'classes\d*\.dex',n)]
 for n in names:
  original=z.read(n);(B/n).write_bytes(original);patched=B/(n+'.patched');out=run([J/'java.exe','-cp',str(P)+';'+cp,'ServicesPenPatch',B/n,patched],n)
  changed=int(re.search(r'PATCHED (\d+)',out)[1]);count+=changed
  if changed:replacements[n]=patched.read_bytes()
  checks[n]={'changed':bool(changed),'source_sha256':hashlib.sha256(original).hexdigest()}
 assert count==2,('Expected only systemReady and pen-key interception',count)
 extra='classes'+str(max(1 if n=='classes.dex'else int(re.search(r'\d+',n)[0])for n in names)+1)+'.dex'
 with zipfile.ZipFile(target,'w')as dest:
  for e in z.infolist():dest.writestr(e,replacements.get(e.filename,z.read(e.filename)))
  dest.writestr(extra,(D/'classes.dex').read_bytes())
result={'base_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'patched_methods':count,'extra_dex':extra,'dex':checks,'not_physical_tested':True}
(B/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
