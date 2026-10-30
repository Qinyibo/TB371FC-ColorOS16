"""Build the tested device state into independent EXT4 images (Linux/WSL)."""
from pathlib import Path
import hashlib,json,subprocess,re,posixpath,sys
O=Path('/mnt/c/Users/Administrator/Documents/Codex/2026-10-28/yu/work/release-v23')
R=Path('/mnt/d/TB371FC-release/R94T-v23-build');P=R/'payloads';D=R/'readback';D.mkdir(exist_ok=True)
plan=json.loads((O/'plan.json').read_text(encoding='utf-8'));assert plan['status']=='PAYLOADS_AND_INDEPENDENT_BASE_IMAGES_READY'
log=O/'image-edit.log';rows=[];removed=[];counter=0
resume='--resume' in sys.argv
previous_log=log.read_text(encoding='utf-8',errors='replace') if resume else ''
if resume:counter=1000
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def debug(image,command,write=False,absent=False):
 q=subprocess.run(['/usr/sbin/debugfs']+(['-w'] if write else [])+['-R',command,str(image)],capture_output=True,timeout=120)
 text=(q.stdout+q.stderr).decode('utf-8','replace')
 with log.open('a') as out:out.write(command+'\n'+text+'\n')
 assert q.returncode==0 and not re.search(r'(?i)no space|could not allocate|while writing|usage:|not a directory',text),text
 if absent and 'File not found by ext2_lookup' in text:return None
 assert 'File not found by ext2_lookup' not in text,text
 return text
def dump(image,target):
 global counter;counter+=1;f=D/(str(counter)+'-'+Path(target).name);debug(image,'dump '+target+' '+str(f));assert f.exists();return f
def label(image,target):
 global counter;counter+=1;f=D/(str(counter)+'.label');debug(image,'ea_get -f '+str(f)+' '+target+' security.selinux');return f
for partition,changes in plan['changes'].items():
 image=R/(partition+'.img');assert image.stat().st_size==plan['images'][partition]['bytes']
 for target,name in changes.items():
  src=P/name;assert sha(src)==plan['payloads'][name]
  st=debug(image,'stat '+target);assert 'Type: regular' in st
  if resume:
   current=dump(image,target)
   assert sha(current)==sha(src),'Resume is limited to already verified replacements'
   old_path=next(line.split(' ',2)[2] for line in previous_log.splitlines() if line.startswith('dump '+target+' '))
   context=label(image,target);mode=re.search(r'Mode:\s+(0[0-7]+)',st)[1]
   original_context=Path(next(line.split()[2] for line in previous_log.splitlines() if line.startswith('ea_get -f ') and line.endswith(' '+target+' security.selinux')))
   if context.read_bytes()!=original_context.read_bytes():
    assert target=='/etc/r94-native/module-delivery/SHA256SUMS'
    debug(image,'ea_set -f '+str(original_context)+' '+target+' security.selinux',True)
    context=label(image,target);assert context.read_bytes()==original_context.read_bytes()
   rows.append({'partition':partition,'target':target,'base_sha256':sha(Path(old_path)),'new_sha256':sha(src),'mode':mode,'context':context.read_text(encoding='utf-8').rstrip('\0'),'verified_existing_edit':True})
   continue
  original=dump(image,target);context=label(image,target);mode=re.search(r'Mode:\s+(0[0-7]+)',st)[1]
  assert re.search(r'User:\s*0\s+Group:\s*0',st)
  assert debug(image,'stat '+target+'.fsv_meta',absent=True) is None,'Review existing file integrity sidecar before replacing'
  debug(image,'rm '+target,True);debug(image,'write '+str(src)+' '+target,True)
  for key,value in [('mode','0100'+mode[-3:]),('uid','0'),('gid','0')]:debug(image,'set_inode_field '+target+' '+key+' '+value,True)
  debug(image,'ea_set -f '+str(context)+' '+target+' security.selinux',True)
  actual=dump(image,target);new_context=label(image,target)
  assert sha(actual)==sha(src) and new_context.read_bytes()==context.read_bytes()
  newstat=debug(image,'stat '+target);assert 'Type: regular' in newstat and ('Mode:  '+mode) in newstat
  rows.append({'partition':partition,'target':target,'base_sha256':sha(original),'new_sha256':sha(src),'mode':mode,'context':context.read_text().rstrip('\0')})
 # Remove only obsolete compilation/profile companions of the two changed code files.
 companions=(['/system/framework/oat/arm64/oplus-services.'+x for x in ['art','odex','vdex']]
             if partition=='system_a' else ['/priv-app/SystemUI/oat/arm64/SystemUI.'+x for x in ['art','odex','vdex']]+['/priv-app/SystemUI/SystemUI.apk.prof'])
 for target in companions:
  for suffix in ['', '.fsv_meta']:
   path=target+suffix;st=debug(image,'stat '+path,absent=True)
   if st is not None:
    assert 'Type: regular' in st
    original=dump(image,path);removed.append({'partition':partition,'target':path,'sha256':sha(original)})
    debug(image,'rm '+path,True)
 # Independently check every entry in the two nested native first-boot lists.
 if partition=='system_ext_a':
  for root in ['/etc/r91-rom','/etc/r94-native/module-delivery']:
   checks=dump(image,root+'/SHA256SUMS').read_text(encoding='utf-8')
   for line in checks.splitlines():
    want,name=line.split(None,1);target=posixpath.normpath(root+'/'+name.strip())
    assert target.startswith('/etc/r91-rom/') or target.startswith('/etc/r94-native/module-delivery/'),target
    assert sha(dump(image,target))==want,target
 q=subprocess.run(['/usr/sbin/e2fsck','-fn',str(image)],capture_output=True,timeout=300)
 (O/(partition+'-fsck.txt')).write_bytes(q.stdout+q.stderr);assert q.returncode==0
 plan['images'][partition]['sha256']=sha(image);print('IMAGE_EDIT_AND_FSCK_PASS',partition,flush=True)
plan.update(status='IMAGES_EDITED_READBACK_CHECKSUM_CLOSURE_FSCK_PASS',changed_files=rows,removed_stale_companions=removed,clean_flash_tested=False)
(O/'image-result.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');print('IMAGE_BUILD_COMPLETE',flush=True)
