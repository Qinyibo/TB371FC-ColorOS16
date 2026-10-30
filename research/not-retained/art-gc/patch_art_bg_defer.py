import pathlib,hashlib,struct,json,io
from elftools.elf.elffile import ELFFile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
p=pathlib.Path('work/art-bg-defer');original=(p/'libart-original.so').read_bytes();old_hash=hashlib.sha256(original).hexdigest()
assert old_hash=='16c6d07f5baaff155478664adbcd773386cfd9aff4bdd856652406c749e9c187'
elf=ELFFile(io.BytesIO(original));symbols=elf.get_section_by_name('.symtab')
name='_ZN3art2gc4Heap26RequestCollectorTransitionENS0_13CollectorTypeEm'
symbol=next(s for s in symbols.iter_symbols() if s.name==name)
assert symbol['st_value']==0x737fc4 and symbol['st_size']==316
index,segment=next((i,s) for i,s in enumerate(elf.iter_segments()) if s['p_type']=='PT_LOAD' and s['p_flags']==5)
assert segment['p_offset']==segment['p_vaddr']==0x400000
assert segment['p_filesz']==segment['p_memsz']==0x95e030
hook=0x738058;resume=hook+4;cave=0xd5f000;delay=1<<32
assert original[hook:resume]==bytes.fromhex('f50300aa')
# RequestCollectorTransition first stores desired type, then returns immediately
# for the current foreground collector. Only an actual queued transition reaches
# this NanoTime result. Keep that cancellation/foreground path byte-identical.
assert original[0x73800c:0x73801c]==bytes.fromhex('68b240b961be00b93f00086b81010054')
assert original[cave:cave+12]==bytes(12)
assert segment['p_vaddr']+segment['p_memsz']<=cave
next_load=min(s['p_vaddr'] for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_vaddr']>segment['p_vaddr'])
assert cave+12<next_load
assert not any(s['sh_flags']&2 and s['sh_addr']<cave+12 and s['sh_addr']+s['sh_size']>cave for s in elf.iter_sections())
def branch(src,dst):
 delta=dst-src;assert delta%4==0 and -(1<<27)<=delta<(1<<27)
 return struct.pack('<I',0x14000000|((delta//4)&0x3ffffff))
# x21 = NanoTime() + 2^32ns. MOVZ/ADD preserve flags and all other registers.
stub=struct.pack('<II',0xd2800000|(2<<21)|(1<<5)|21,0x8b000000|(21<<16)|21)+branch(cave+8,resume)
patched=bytearray(original);patched[hook:resume]=branch(hook,cave);patched[cave:cave+12]=stub
new_size=cave+len(stub)-segment['p_vaddr'];ph=elf.header['e_phoff']+index*elf.header['e_phentsize']
struct.pack_into('<QQ',patched,ph+32,new_size,new_size)
check=ELFFile(io.BytesIO(patched));assert check.num_segments()==elf.num_segments()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
decoded=[(hex(i.address),i.mnemonic,i.op_str) for i in md.disasm(stub,cave)]
assert decoded==[(hex(cave),'mov','x21, #0x100000000'),(hex(cave+4),'add','x21, x0, x21'),(hex(cave+8),'b',hex(resume).replace('0x','#0x'))],decoded
changes=[i for i,(a,b) in enumerate(zip(original,patched)) if a!=b]
allowed=set(range(hook,resume))|set(range(cave,cave+12))|set(range(ph+32,ph+48))
assert set(changes)<=allowed and len(patched)==len(original)
text=elf.get_section_by_name('.text');start=text['sh_offset'];end=start+text['sh_size']
assert [i for i in changes if start<=i<end]==[i for i in range(hook,resume) if original[i]!=patched[i]]
(p/'libart-bg-defer.so').write_bytes(patched)
v={'status':'OFFLINE_NATIVE_BG_GC_DEFER_VERIFIED','base_sha256':old_hash,'candidate_sha256':hashlib.sha256(patched).hexdigest(),'target_symbol':name,'hook_address':hex(hook),'stub_address':hex(cave),'delay_ns':delay,'delay_ms':delay/1e6,'changed_byte_offsets':changes,'executable_segment_extended_into_verified_unused_padding':True,'file_size_unchanged':True,'normal_gc_unchanged':True,'heap_limits_unchanged':True,'foreground_transition_unchanged':True,'currently_active':False,'stub':decoded}
(p/'validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
