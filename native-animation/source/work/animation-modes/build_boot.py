"""Remove the level-4 Assistant veto before the late ROM overlay is loaded."""
from pathlib import Path
import hashlib,struct,zlib,zipfile,json,sys
from loguru import logger
logger.remove()
from androguard.core.dex import DEX
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W.parent))
from apk_dex_replace import replace_dex
source=W/'inputs/AssistantScreen-stock.apk';raw=source.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='c8e7396f691b146d630764e3037e7a41f92170c725e1661272406c41c7c6a628'
with zipfile.ZipFile(source)as z:
 original=z.read('classes5.dex');dex=DEX(original)
 method=next(m for c in dex.get_classes()if c.get_name()=='LLz/l;'for m in c.get_methods()if m.get_name()=='d'and m.get_descriptor()=='()Z')
 code=method.get_code();assert code.get_tries_size()==0
 start=method.get_code_off()+16;size=code.get_length()*2
 assert size==50,size
 data=bytearray(original)
 data[start:start+size]=bytes.fromhex('12000f00')+bytes(size-4)
 data[12:32]=hashlib.sha1(data[32:]).digest()
 struct.pack_into('<I',data,8,zlib.adler32(data[12:])&0xffffffff)
 result=replace_dex(raw,'classes5.dex',bytes(data))
 assert len(result)==len(raw)
 output=W/'build/assistant-boot/AssistantScreen.apk';output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(result)
 with zipfile.ZipFile(output)as dest:
  assert dest.testzip()is None
  assert [n for n in z.namelist()if z.read(n)!=dest.read(n)]==['classes5.dex']
spans=[]
for i,(old,new)in enumerate(zip(raw,result)):
 if old==new:continue
 if spans and spans[-1]['offset']+len(bytes.fromhex(spans[-1]['new']))==i:
  spans[-1]['old']+=f'{old:02x}';spans[-1]['new']+=f'{new:02x}'
 else:spans.append({'offset':i,'old':f'{old:02x}','new':f'{new:02x}'})
info={'source_sha256':hashlib.sha256(raw).hexdigest(),'target_sha256':hashlib.sha256(result).hexdigest(),'size':len(result),'target':'/my_stock/app/AssistantScreen/AssistantScreen.apk','method':'LLz/l;->d()Z','spans':spans}
(W/'build/assistant-boot-patch.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
print('ASSISTANT_BOOT_PATCH',info['target_sha256'],'changed_bytes',sum(len(bytes.fromhex(s['new']))for s in spans),flush=True)
