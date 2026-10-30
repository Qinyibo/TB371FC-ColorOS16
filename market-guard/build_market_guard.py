from pathlib import Path
import copy, hashlib, json, re, shutil, subprocess, zipfile
W=Path(__file__).resolve().parent;O=W/'market'
source=Path('D:/TB371FC-ROM-R92-20261011/apps/current/com.heytap.market/base.apk')
SOURCE_SHA='391a2fb1e9bd5d22331656b44d42837ef9048ab754b1a72996f24daeb0a49179'
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()==SOURCE_SHA
packages=['com.android.launcher','com.coloros.assistantscreen','com.oplus.ota','com.heytap.market']
changes=[]
for name,signature,param,result in [
 ('r05','.method public ޒ(Ljava/lang/String;)Lcom/heytap/market/download/api/type/DownloadStatus;','p1',
  'sget-object v0, Lcom/heytap/market/download/api/type/DownloadStatus;->INSTALLED:Lcom/heytap/market/download/api/type/DownloadStatus;\n    return-object v0'),
 ('mwg','.method public static ބ(Ljava/lang/String;)Z','p0','const/4 v0, 0x1\n    return v0')]:
 p=O/'smali5/a/a/a'/(name+'.smali');s=p.read_text(encoding='utf8')
 backup=O/(name+'-original.smali')
 if backup.exists():s=backup.read_text(encoding='utf8')
 else:backup.write_text(s,encoding='utf8')
 assert s.count(signature)==1
 start=s.index(signature);end=s.index('.end method',start)
 method=s[start:end];assert '.registers ' in method
 insert=method.index('\n',method.index('.registers '))+1
 prefix='\n'
 for pkg in packages:
  prefix+=f'    const-string v0, "{pkg}"\n    invoke-virtual {{v0, {param}}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z\n    move-result v0\n    if-nez v0, :r93_protected\n'
 prefix+='    goto :r93_original\n    :r93_protected\n    '+result+'\n    :r93_original\n'
 patched=method[:insert]+prefix+method[insert:]
 assert patched.replace(prefix,'',1)==method
 p.write_text(s[:start]+patched+s[end:],encoding='utf8')
 changes.append(dict(class_name=name,method=signature,unprotected_original_body_preserved=True))
p=subprocess.run(['C:/Program Files/Java/jdk-21/bin/java.exe','-cp',
 'C:/Users/Administrator/Documents/Codex/2026-07-30/x/work/*','org.jf.smali.Main','assemble',
 str(O/'smali5'),'-o',str(O/'classes5-patched.dex')],capture_output=True)
assert p.returncode==0,p.stdout+p.stderr
dest=O/'Market-protected-candidate.apk'
shutil.copyfile(source,dest)
original_size=source.stat().st_size
# Store only a small append-only ZIP tail in the ROM. All unchanged ZIP members
# retain their exact original compressed bytes and offsets. No duplicate names.
with zipfile.ZipFile(dest,'a') as out:
 infos=[copy.copy(i) for i in out.infolist() if i.filename!='classes5.dex' and
        not re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)|META-INF/MANIFEST.MF',i.filename,re.I)]
 out.filelist=infos;out.NameToInfo={i.filename:i for i in infos}
 out.start_dir=original_size
 info=zipfile.ZipInfo('classes5.dex',(2026,10,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
 out.writestr(info,(O/'classes5-patched.dex').read_bytes())
with source.open('rb') as a,dest.open('rb') as b:
 for block in iter(lambda:a.read(8<<20),b''):assert b.read(len(block))==block
 tail=b.read()
(O/'market-apk-tail.bin').write_bytes(tail)
with zipfile.ZipFile(source) as a,zipfile.ZipFile(dest) as b:
 assert b.testzip() is None
 assert len(b.namelist())==len(set(b.namelist()))
 for n in b.namelist():
  if n!='classes5.dex':assert a.read(n)==b.read(n),n
manifest=dict(state='BUILT_RUNTIME_PENDING',original_sha256=SOURCE_SHA,
 candidate_sha256=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest(),
 tail_sha256=hashlib.sha256(tail).hexdigest(),tail_bytes=len(tail),original_bytes=original_size,
 protected_packages=packages,changes=changes,original_signed_apk_must_be_scanned_first=True,
 all_other_zip_members_identical=True,no_duplicate_zip_names=True)
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(manifest,ensure_ascii=False,indent=2),flush=True)
