from pathlib import Path
import hashlib,json,re,subprocess
O=Path(__file__).resolve().parent
R=Path('/mnt/d/TB371FC-release/v22b-firstboot-publication-build')
D=R/'camera-readback';assert not D.exists();D.mkdir()
LOG=O/'camera-image-edit-log.txt';assert not LOG.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
class Editor:
 counter=0
 def __init__(self,name):self.name=name;self.image=R/(name+'-candidate.img')
 def run(self,command,write=False,absent=False):
  p=subprocess.run(['/usr/sbin/debugfs']+(['-w'] if write else [])+['-R',command,str(self.image)],capture_output=True,timeout=120)
  s=(p.stdout+p.stderr).decode('utf-8','replace')
  with LOG.open('a') as f:f.write(self.name+' '+command+'\n'+s+'\n')
  assert not p.returncode and not re.search(r'(?i)no space|could not allocate|while writing|usage:|not a directory',s),s
  if absent and 'File not found by ext2_lookup' in s:return None
  assert 'File not found by ext2_lookup' not in s,s
  return s
 def dump(self,path):
  Editor.counter+=1;p=D/(str(Editor.counter)+'-'+Path(path).name);self.run('dump '+path+' "'+str(p)+'"');assert p.exists();return p
 def metadata(self,path,mode,label):
  for k,v in [('mode',mode),('uid','0'),('gid','0')]:self.run('set_inode_field '+path+' '+k+' '+v,True)
  Editor.counter+=1;p=D/(str(Editor.counter)+'.label');p.write_bytes(label);self.run('ea_set -f "'+str(p)+'" '+path+' security.selinux',True)
 def mkdir(self,path):
  assert self.run('stat '+path,absent=True) is None
  self.run('mkdir '+path,True);self.metadata(path,'040755',b'u:object_r:system_file:s0\0')
 def put(self,path,source,new=False,mode='0100644'):
  if new:assert self.run('stat '+path,absent=True) is None;label=b'u:object_r:system_file:s0\0'
  else:
   st=self.run('stat '+path);assert 'Type: regular' in st
   Editor.counter+=1;l=D/(str(Editor.counter)+'.old-label');self.run('ea_get -f "'+str(l)+'" '+path+' security.selinux');label=l.read_bytes();assert label.endswith(b'\0');self.run('rm '+path,True)
  self.run('write "'+str(source)+'" '+path,True);self.metadata(path,mode,label)
  assert sha(self.dump(path))==sha(source)
  Editor.counter+=1;l=D/(str(Editor.counter)+'.readback-label');self.run('ea_get -f "'+str(l)+'" '+path+' security.selinux');assert l.read_bytes()==label
  st=self.run('stat '+path);assert re.search(r'User:\s*0\s+Group:\s*0',st)
  return {'path':path,'sha256':sha(source),'context':label.decode().rstrip('\0'),'mode':mode}
 def remove_camera_tree(self,path,removed):
  assert path=='/my_product/app/Camera' or path.startswith('/my_product/app/Camera/')
  st=self.run('stat '+path)
  if 'Type: regular' in st:
   p=self.dump(path);removed.append({'path':path,'sha256':sha(p),'bytes':p.stat().st_size});self.run('rm '+path,True);return
  assert 'Type: directory' in st, 'Do not follow image symlinks or special nodes'
  listing=self.run('ls -p '+path)
  names=[]
  for line in listing.splitlines():
   fields=line.split('/')
   if len(fields)<7 or not fields[1].isdigit():continue
   name=fields[5]
   if name in ['.','..']:continue
   assert re.fullmatch(r'[A-Za-z0-9_.-]+',name),name
   names.append(name)
  for name in names:self.remove_camera_tree(path+'/'+name,removed)
  self.run('rmdir '+path,True)

assert json.loads((O/'system-clone-result.json').read_text())['state']=='PRIVATE_SYSTEM_A_COPY_SOURCE_SHA_PASS'
compression=json.loads((O.parent/'cold-start-camera-20261025/zui-v7-compression-result.json').read_text())
archive=R/'ZuiCamera-v7.apk.xz';assert sha(archive)==compression['compressed_sha256']
assert sha(O/'install-camera-once.sh')
sy=Editor('system_a');se=Editor('system_ext_a')
# Only the old standalone camera application and its obsolete companions leave.
removed=[];sy.remove_camera_tree('/my_product/app/Camera',removed)
assert removed and any(r['path'].endswith('/Camera.apk') for r in removed)
sy.mkdir('/system/app/ZuiCameraSeed');sy.mkdir('/system/etc/r94-camera-v7')
rows=[]
seed=O.parent/'cold-start-camera-20261025/system-camera-seed/ZuiCameraSeed.apk'
assert sha(seed)=='3019d0e8d7815a5e0a5b60dafed7803172954e42883e5ae17c109401e020d511'
rows.append(sy.put('/system/app/ZuiCameraSeed/ZuiCameraSeed.apk',seed,True))
rows.append(sy.put('/system/etc/r94-camera-v7/ZuiCamera.apk.xz',archive,True))
rows.append(sy.put('/system/etc/r94-camera-v7/install-once.sh',O/'install-camera-once.sh',True,'0100755'))
for name in ['apply.sh','SHA256SUMS']:
 rows.append(se.put('/etc/r91-rom/'+name,O/'overlay/system_ext/etc/r91-rom'/name,mode='0100755' if name=='apply.sh' else '0100644'))
assert sy.run('stat /my_product/app/Camera',absent=True) is None
assert sha(se.dump('/overlay/R94NativeUI_bootreg.apk'))=='e61d0cd3350c3dbc94218859bc07c07828b527df6c98110c68a82b46c0bd6712'
assert sha(se.dump('/etc/init/r94-pen-native-v1.rc'))=='870498834e2934b521cb532e8a4a9338acfea00f4e5fc682a5793df0f98405e1'
assert sha(se.dump('/etc/r94-pen-native-v4/bootstrap.sh'))=='9f17191b5458bb29653f9f875d2b1237dc5fe09d52d0a022e9acfb1940b62bcb'
# Native first-boot guard closure, including the unchanged module delivery.
checks=se.dump('/etc/r91-rom/SHA256SUMS').read_text()
for line in checks.splitlines():
 h,n=line.split(None,1);n=n.strip()
 import posixpath
 target=posixpath.normpath('/etc/r91-rom/'+n)
 assert target.startswith('/etc/r91-rom/') or target=='/etc/r94-native/module-delivery/delivery.sh'
 assert sha(se.dump(target))==h,n
for editor in [sy,se]:
 p=subprocess.run(['/usr/sbin/e2fsck','-fn',str(editor.image)],capture_output=True,timeout=240);(O/(editor.name+'-final-fsck.txt')).write_bytes(p.stdout+p.stderr);assert not p.returncode
 print('FINAL_FILESYSTEM_CHECK_PASS '+editor.name,flush=True)
result={'state':'V22B_CAMERA_SYSTEM_BASE_COMPRESSED_EXACT_UPDATE_GUARD_RRO_CACHE_LABELS_FSCK_PASS_HASH_PENDING','new_files_and_replacements':rows,'removed_only_old_camera':removed,'firstboot_guard_and_asset_closure_pass':True,'new_init_service_or_SELinux_rule':False,'source_v7_CAMERA_APK':compression,'original_kernel43_and_vendor_preserved':True,'clean_ROM_firstboot_tested':False}
(O/'camera-image-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'state':result['state'],'old_camera_removed_files':len(removed)}),flush=True)
