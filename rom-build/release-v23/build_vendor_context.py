from pathlib import Path
import os,json,hashlib,subprocess,re,importlib.util,shutil
if os.name=='nt':
 O=Path(__file__).resolve().parent;R=Path(r'D:\TB371FC-release\R94T-v23-build');B=R.parent/'R94T-v22b-FIRSTBOOT-CAMERA-PRIVATE_TEST';p=R/'vendor_a.img';assert not p.exists()
 spec=importlib.util.spec_from_file_location('lp',r'D:\TB371FC-work\continuation-20260925\tools\lp_probe.py');lp=importlib.util.module_from_spec(spec);spec.loader.exec_module(lp)
 with (B/'images/super-R94.img').open('rb') as f:
  header=f.read(2<<20);part=next(v for v in lp.parse_metadata(header,lp.parse_geometry(header))['partitions'] if v['name']=='vendor_a')
  assert len(part['extents'])==1;f.seek(part['extents'][0]['target_data']*512);left=part['size_bytes'];h=hashlib.sha256()
  with p.open('wb') as out:
   while left:
    b=f.read(min(left,8<<20));assert b;out.write(b);h.update(b);left-=len(b)
 assert h.hexdigest()=='2bc961b4868a5d5a770c7d2129ab4226beb7dfc86cbf183ae26fe2febca436a8'
 shutil.copyfile(O/'r91-rom.rc',R/'payloads/r91-rom.rc');print('VENDOR_BASE_EXTRACTED',flush=True)
else:
 O=Path('/mnt/c/Users/Administrator/Documents/Codex/2026-10-28/yu/work/release-v23');R=Path('/mnt/d/TB371FC-release/R94T-v23-build');p=R/'vendor_a.img';D=R/'vendor-init-context-readback';D.mkdir(exist_ok=False)
 def dbg(cmd,write=False):
  q=subprocess.run(['debugfs']+(['-w'] if write else [])+['-R',cmd,str(p)],capture_output=True,check=True);s=(q.stdout+q.stderr).decode('utf-8','replace')
  assert not re.search(r'(?i)no space|could not allocate|while writing|usage:|not a directory|File not found',s),s
  return s
 target='/etc/init/r91-rom.rc';old=D/'original.rc';label=D/'label';actual=D/'readback.rc'
 dbg('dump '+target+' '+str(old));assert hashlib.sha256(old.read_bytes()).hexdigest()=='e69e563723c8f0fe7ee3a46b07b20758d92ce6864c642938630e1b4667c24800'
 stat=dbg('stat '+target);assert 'Mode:  0644' in stat and re.search(r'User:\s*0\s+Group:\s*0',stat)
 dbg('ea_get -f '+str(label)+' '+target+' security.selinux')
 assert label.read_bytes().rstrip(b'\0')==b'u:object_r:vendor_configs_file:s0'
 dbg('rm '+target,True);dbg('write '+str(R/'payloads/r91-rom.rc')+' '+target,True)
 for field,value in [('mode','0100644'),('uid','0'),('gid','0')]:dbg('set_inode_field '+target+' '+field+' '+value,True)
 dbg('ea_set -f '+str(label)+' '+target+' security.selinux',True);dbg('dump '+target+' '+str(actual));assert actual.read_bytes()==(R/'payloads/r91-rom.rc').read_bytes()
 q=subprocess.run(['e2fsck','-fn',str(p)],capture_output=True);(O/'vendor_a-fsck.txt').write_bytes(q.stdout+q.stderr);assert q.returncode==0
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 result=json.loads((O/'image-result.json').read_text(encoding='utf-8'))
 result['images']['vendor_a']={'path':r'D:\TB371FC-release\R94T-v23-build\vendor_a.img','bytes':p.stat().st_size,'sha256':h}
 result['changes']['vendor_a']={target:'r91-rom.rc'};result['payloads']['r91-rom.rc']=hashlib.sha256(actual.read_bytes()).hexdigest()
 result['changed_files'].append({'partition':'vendor_a','target':target,'base_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'new_sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'mode':'0644','context':label.read_bytes().rstrip(b'\0').decode()})
 result['init_context_fix']='Use existing Magisk domain instead of KernelSU domain which disappears after Magisk environment initialization.'
 (O/'image-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('VENDOR_CONTEXT_IMAGE_READBACK_FSCK_PASS',h,flush=True)
