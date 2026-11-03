from pathlib import Path
import subprocess,zipfile,struct,gzip,hashlib,json,sys,shutil
W=Path(__file__).resolve().parent;B=W/'build';A=W/'native/system/etc/r94-animation-v1';A.mkdir(parents=True,exist_ok=True)
rows=json.loads((B/'result.json').read_text());props={};stats={}
# The stock Assistant runs before the boot-completed overlay. Fix its exact
# unsupported-level predicate too, otherwise it persists a disabled switch.
boot=json.loads((B/'assistant-boot-patch.json').read_text())
boot_apk=W/'native/my_stock/app/AssistantScreen/AssistantScreen.apk'
boot_apk.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(B/'assistant-boot/AssistantScreen.apk',boot_apk)
shutil.copyfile(B/'assistant-boot-patch.json',A/'assistant-boot-patch.json')
rom=W/'native/system_ext/etc/r91-rom'
apply=rom/'apply.sh';text=apply.read_text(encoding='utf-8')
assert text.count(boot['source_sha256'])+text.count(boot['target_sha256'])==1
text=text.replace(boot['source_sha256'],boot['target_sha256'])
old='''mount -o bind /data/adb/r91-assistant/AssistantScreen.apk "$assistant_target" || rollback assistant_apk
for s in art dex vdex; do
    cache_target "$assistant_prefix.$s"
    mount -o bind /data/adb/r91-assistant/aot/AssistantScreen.$s "$assistant_prefix.$s" || rollback assistant_cache
done
/data/adb/r91-assistant/bind-readonly --paired || rollback assistant_readonly'''
if 'R94_ASSISTANT_DIRECT_NATIVE_ASSETS' not in text:
 assert text.count(old)==1
 text=text.replace(old,'# R94_ASSISTANT_DIRECT_NATIVE_ASSETS: the animation bootstrap mounts the final code.\n# Do not briefly run the intermediate Assistant or its old ART files.')
apply.write_text(text,encoding='utf-8',newline='\n')
checks=rom/'SHA256SUMS';lines=checks.read_text().splitlines()
for i,line in enumerate(lines):
 if line.split(None,1)[1].lstrip('./')=='apply.sh':
  lines[i]=hashlib.sha256(apply.read_bytes()).hexdigest()+'  apply.sh'
checks.write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
targets={'launcher':('/system_ext/priv-app/OplusLauncher/OplusLauncher.apk','OplusLauncher.apk'),'settings':('/system_ext/priv-app/Settings/Settings.apk','Settings.apk'),'assistant':('/system_ext/etc/r91-rom/assistant/AssistantScreen.apk','AssistantScreen.apk')}
def sha(b):return hashlib.sha256(b).hexdigest()
for k,row in rows.items():
 source=Path(row['source']);target=Path(row['target']);ob=source.read_bytes();tb=target.read_bytes();spans=[]
 def payload(raw,e):
  off=e.header_offset;nl,el=struct.unpack_from('<HH',raw,off+26);start=off+30+nl+el
  return start,raw[start:start+e.compress_size]
 with zipfile.ZipFile(source)as oz,zipfile.ZipFile(target)as tz:
  original={e.filename:e for e in oz.infolist()}
  for e in tz.infolist():
   if e.filename not in original:continue
   ts,tdata=payload(tb,e);os,odata=payload(ob,original[e.filename])
   if len(tdata)>16 and tdata==odata:spans.append((ts,os,len(tdata)))
 recipe=bytearray(b'R94PEN02');cursor=0;rebuilt=bytearray()
 for ts,os,length in sorted(spans):
  if cursor<ts:
   lit=tb[cursor:ts];recipe+=b'\2'+struct.pack('>Q',len(lit))+lit;rebuilt+=lit
  recipe+=b'\1'+struct.pack('>QQ',os,length);rebuilt+=ob[os:os+length];cursor=ts+length
 if cursor<len(tb):
  lit=tb[cursor:];recipe+=b'\2'+struct.pack('>Q',len(lit))+lit;rebuilt+=lit
 assert rebuilt==tb,k
 recipe+=b'\0';packed=gzip.compress(recipe,mtime=0);(A/(k+'.recipe.gz')).write_bytes(packed)
 path,name=targets[k]
 props.update({k+'.source':path,k+'.sourceName':source.name,k+'.sourceSha':row['source_sha256'],k+'.name':name,k+'.outputSha':row['target_sha256'],k+'.outputSize':str(len(tb)),k+'.recipeSha':sha(packed)})
 stats[k]={'recipe_bytes':len(packed),'sha256':row['target_sha256']}
(A/'manifest.properties').write_text('\n'.join(k+'='+v for k,v in sorted(props.items()))+'\n',encoding='ascii',newline='\n')
template=Path('D:/TB371FC-release/public-source/TB371FC-ColorOS16/native-pen/source/work/NativePayloadV2.java').read_text()
source=template.replace('package org.tb371fc.pen;','package org.tb371fc.animation;').replace('NativePayloadV2','NativeAssets').replace('new String[]{"ipe","ws"}','new String[]{"launcher","settings","assistant"}').replace('BOTH_VERIFIED','ALL_VERIFIED')
# Verify caches first, allowing safe repeat invocation with our own mounts active.
needle='''      File src=new File(args.length==3?new File(args[2],cfg.getProperty(k+".sourceName")).getPath():cfg.getProperty(k+".source"));
      if(!sha(src).equals(cfg.getProperty(k+".sourceSha")))'''
replacement='''      File current=new File(new File(output,k),cfg.getProperty(k+".name"));
      if(current.isFile() && sha(current).equals(cfg.getProperty(k+".outputSha"))) continue;
      File src=new File(args.length==3?new File(args[2],cfg.getProperty(k+".sourceName")).getPath():cfg.getProperty(k+".source"));
      if(!sha(src).equals(cfg.getProperty(k+".sourceSha")))'''
assert needle in source;source=source.replace(needle,replacement)
source=source.replace('if(target.isFile()){if(!sha(target).equals(expected))throw new SecurityException("Cache differs: "+k);System.out.println("CURRENT "+k);continue;}','if(target.isFile() && sha(target).equals(expected)){System.out.println("CURRENT "+k);continue;}')
(W/'NativeAssets.java').write_text(source,encoding='utf-8')
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk');C=B/'native-classes';C.mkdir(exist_ok=True)
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=90)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
run([J/'javac.exe','--release','8','-d',C,W/'NativeAssets.java']);jar=B/'native-classes.jar'
with zipfile.ZipFile(jar,'w')as z:
 for p in C.rglob('*.class'):z.write(p,p.relative_to(C).as_posix())
D=B/'native-dex';D.mkdir(exist_ok=True);run([S/'build-tools/36.0.0/d8.bat','--min-api','35','--output',D,jar])
with zipfile.ZipFile(A/'bootstrap.jar','w')as z:z.write(D/'classes.dex','classes.dex')
# Small static arm64 executable: mount(NULL, argv[1], NULL,
# MS_BIND|MS_REMOUNT|MS_RDONLY|MS_NOSUID|MS_NODEV, NULL). No Magisk/BusyBox dependency.
# Linux arm64 mount=40, exit=93. All nonzero mount results become exit 1.
code=[0xf94003e9,0xf100093f,0,0xf9400be1,0xaa1f03e0,0xaa1f03e2,
      0xd2a00083,0xaa1f03e4,0xd2800508,0xd4000001, # MS_PRIVATE
      0xf9400be1,0xaa1f03e0,0xaa1f03e2,0xd28204e3,0xaa1f03e4,
      0xd2800508,0xd4000001,0xd37ffc00,0xd2800ba8,0xd4000001,
      0xd2800040,0xd2800ba8,0xd4000001]
code[2]=0x54000001|((20-2)<<5)
native=b''.join(struct.pack('<I',v)for v in code);size=120+len(native)
ident=b'\x7fELF\x02\x01\x01'+bytes(9)
elf=ident+struct.pack('<HHIQQQIHHHHHH',2,183,1,0x400078,64,0,0,64,56,1,0,0,0)
elf+=struct.pack('<IIQQQQQQ',1,5,0,0x400000,0x400000,size,size,4096)+native
(A/'bind-readonly').write_bytes(elf)
sh='''#!/system/bin/sh
set -eu
assets=/system/etc/r94-animation-v1
cache=/data/local/r94-animation-v1
mkdir -p "$cache"
chmod 755 "$cache"
setprop debug.r94.animation_active_level "$(getprop persist.sys.oplus.anim_level)"
CLASSPATH="$assets/bootstrap.jar" app_process /system/bin org.tb371fc.animation.NativeAssets "$assets" "$cache"
for k in launcher settings assistant; do
    chmod 755 "$cache/$k"
    chmod 644 "$cache/$k/"*.apk
    chcon u:object_r:system_file:s0 "$cache/$k" "$cache/$k/"*.apk
done
run_cli() { local result rc=0; result=$("$@" 2>&1) || rc=$?; printf '%s\\n' "$result"; return "$rc"; }
run_cli am force-stop com.android.settings
run_cli am force-stop com.android.launcher
run_cli am force-stop com.coloros.assistantscreen
# The previous assistant's ART files describe its old dex; never keep them bound.
prefix=/data/dalvik-cache/arm64/my_stock@app@AssistantScreen@AssistantScreen.apk@classes
for s in art dex vdex; do umount -l "$prefix.$s" 2>/dev/null || true; done
bind_apk() {
    mount -o bind "$1" "$2"
    "$assets/bind-readonly" "$2"
}
if [ ! -f "$cache/launcher/OplusLauncher.apk.prof" ]; then
    cp /system_ext/priv-app/OplusLauncher/OplusLauncher.apk.prof "$cache/launcher/"
    chmod 644 "$cache/launcher/OplusLauncher.apk.prof"
    chcon u:object_r:system_file:s0 "$cache/launcher/OplusLauncher.apk.prof"
fi
# Bind the launcher directory so ART cannot select the donor's stale read-only oat directory.
bind_apk "$cache/launcher" /system_ext/priv-app/OplusLauncher
if [ ! -f "$cache/settings/Settings.apk.prof" ]; then
    cp /system_ext/priv-app/Settings/Settings.apk.prof "$cache/settings/"
    chmod 644 "$cache/settings/Settings.apk.prof"
    chcon u:object_r:system_file:s0 "$cache/settings/Settings.apk.prof"
fi
bind_apk "$cache/settings" /system_ext/priv-app/Settings
bind_apk "$cache/assistant" /my_stock/app/AssistantScreen
if [ ! -f "$cache/compiled-REPLACE_DIGEST" ]; then
    complete=1
    for package in com.android.launcher com.android.settings com.coloros.assistantscreen; do
        result=$(run_cli cmd package compile --primary-dex -m speed -f "$package") || complete=0
        printf '%s\\n' "$result"
        printf '%s\\n' "$result" | grep -q '^Success' || complete=0
    done
    if [ "$complete" = 1 ]; then touch "$cache/compiled-REPLACE_DIGEST"; fi
fi
run_cli cmd pinner repin || true
# One-time recovery from the old unsupported-tier preferences; later respect the user.
if [ ! -f "$cache/defaults-v2" ]; then
    run_cli settings --user 0 put secure key_recent_style stacked
    run_cli settings --user 0 put secure disable_assistant_screen 0
    touch "$cache/defaults-v2"
fi
# Discard any Launcher relaunched while the APK directories were being bound.
# Its classes and cached stack support must come from the final mounted APK.
run_cli am force-stop com.android.launcher
if [ "$(run_cli am get-started-user-state 0)" = RUNNING_UNLOCKED ]; then
    run_cli am start -a android.intent.action.MAIN -c android.intent.category.HOME
fi
setprop debug.r94.animation_ready 1
echo R94_ANIMATION_MODES_READY
'''
digest=sha(('directory-ro-v3'+''.join(row['target_sha256']for row in rows.values())).encode())[:16]
(A/'bootstrap.sh').write_text(sh.replace('REPLACE_DIGEST',digest),encoding='utf-8',newline='\n')
(W/'native-build.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2));print('ASSET_TOTAL',sum(p.stat().st_size for p in A.iterdir()))
