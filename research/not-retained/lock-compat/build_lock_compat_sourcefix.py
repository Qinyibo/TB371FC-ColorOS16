import hashlib,json,struct,zlib,zipfile
from pathlib import Path
from collections import deque
from loguru import logger
logger.remove()
from androguard.core.dex import DEX
from androguard.core.analysis.analysis import MethodAnalysis

BASE=Path(r'D:\TB371FC-work\codex-20261028')
src=BASE/'oplus-services-live-20261029.jar'
dst=BASE/'oplus-services-lock-compat-sourcefix.jar'
EXT='Lcom/android/server/ThreadPriorityBoosterExtImpl;'
TRANS='Lcom/android/server/wm/ContinuousTransitionStateManager;'
boost='Lcom/android/server/wm/WindowManagerService;->boostPriorityForLockedSection()V'
reset='Lcom/android/server/wm/WindowManagerService;->resetPriorityAfterLockedSection()V'
changes=[];proof=[];replacement={}

def returns(dex,method):
    ma=MethodAnalysis(dex,method)
    blocks=list(ma.get_basic_blocks().gets())
    todo=deque([(blocks[0],0)]);seen=set();out=set()
    while todo:
        block,n=todo.popleft()
        if (block.start,n) in seen:continue
        seen.add((block.start,n));assert -8<=n<=8,'unbounded priority depth'
        instructions=list(block.get_instructions())
        for i in instructions:
            if boost in i.get_output():n+=1
            if reset in i.get_output():n-=1
        if instructions and instructions[-1].get_name().startswith('return'):out.add(n)
        for edge in block.childs:todo.append((edge[2],n))
    return sorted(out)

with zipfile.ZipFile(src) as z:
    for entry in ['classes.dex','classes2.dex']:
        original=z.read(entry);data=bytearray(original);dex=DEX(original)
        targets=[(EXT,'setLockOwnerThreadBoost')] if entry=='classes.dex' else [(TRANS,'notifyTransitionMergedInner'),(TRANS,'notifyTransitionRemoveTaskInner')]
        for cls,name in targets:
            c=dex.get_class(cls);assert c,cls
            methods=[m for m in c.get_methods() if m.get_name()==name];assert len(methods)==1
            m=methods[0];instructions=[];pos=m.get_code_off()+16
            for i in m.get_instructions():
                raw=i.get_raw();assert bytes(data[pos:pos+len(raw)])==raw
                instructions.append((pos,i));pos+=len(raw)
            patches=[]
            if cls==EXT:
                off,i=instructions[-2]
                assert i.get_name()=='const/4' and i.get_output()=='v0, 1'
                assert instructions[-1][1].get_name()=='return'
                assert i.get_raw()==b'\x12\x10'
                patches=[(off,b'\x12\x00','report unavailable vendor boost so Android fallback runs')]
                before=None
            else:
                before=returns(dex,m);assert before==[0,1],before
                boosts=[(off,i) for off,i in instructions if boost in i.get_output()]
                assert len(boosts)==2
                pairs=[(off,i) for k,(off,i) in enumerate(instructions) if k and reset in i.get_output() and reset in instructions[k-1][1].get_output()]
                assert len(pairs)==1
                for off,i in [boosts[0],pairs[0]]:
                    assert i.get_length()==6
                    patches.append((off,b'\x00'*6,'remove unmatched outer priority region'))
            for off,new,why in patches:
                old=bytes(data[off:off+len(new)]);data[off:off+len(new)]=new
                changes.append({'dex':entry,'class':cls,'method':name,'offset':off,'old':old.hex(),'new':new.hex(),'reason':why})
            proof.append({'dex':entry,'class':cls,'method':name,'before_normal_return_depths':before,'original_tries':m.get_code().get_tries_size()})
        data[12:32]=hashlib.sha1(data[32:]).digest()
        struct.pack_into('<I',data,8,zlib.adler32(data[12:])&0xffffffff)
        newdex=DEX(bytes(data))
        for p in [p for p in proof if p['dex']==entry]:
            nm=next(m for m in newdex.get_class(p['class']).get_methods() if m.get_name()==p['method'])
            assert nm.get_code().get_tries_size()==p['original_tries']
            if p['class']==TRANS:
                p['after_normal_return_depths']=returns(newdex,nm)
                assert p['after_normal_return_depths']==[0]
            else:
                out=list(nm.get_instructions());assert out[-2].get_output()=='v0, 0'
                p['fallback_return']=False
        replacement[entry]=bytes(data)
    with zipfile.ZipFile(dst,'w') as out:
        for info in z.infolist():out.writestr(info,replacement.get(info.filename,z.read(info.filename)))
with zipfile.ZipFile(src) as old,zipfile.ZipFile(dst) as new:
    assert old.namelist()==new.namelist()
    modified=[n for n in old.namelist() if old.read(n)!=new.read(n)]
    assert modified==list(replacement),modified
manifest={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'fixed_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'changes':changes,'proof':proof,'modified_entries':modified,'device_deployed':False}
(BASE/'lock-compat-sourcefix-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8',newline='\n')
for p in proof:print(json.dumps(p))
print('Prepared source JAR:',dst,'patch sites:',len(changes),'not deployed')
