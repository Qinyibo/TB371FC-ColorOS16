"""Merge the retained app rules into matching OEM XML inputs; no device writes."""
from pathlib import Path
import argparse,json,re,html,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('xml',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
rules=json.loads(Path(__file__).with_name('native-window-rules.json').read_text(encoding='utf-8'))
key=a.xml.stem;assert key in rules,key
s=a.xml.read_text(encoding='utf-8');before=ET.fromstring(s);plan=rules[key]
for pkg,body in plan['apps'].items():
 pattern=r'<[a-zA-Z]+\b[^>]*\bpackage_name="'+re.escape(pkg)+r'"[^>]*>'
 value=html.escape(json.dumps(body,ensure_ascii=False,separators=(',',':')).replace('"','^'),quote=True)
 def edit(m):
  t,n=re.subn(r'custom_config_body="[^"]*"',lambda _: 'custom_config_body="'+value+'"',m[0]);assert n==1
  return t
 s,n=re.subn(pattern,edit,s);assert n==1,(key,pkg,n)
old=int(before.findtext('version'));version=max(int(plan['version']),old+1)
s,n=re.subn(r'(<version>)\d+(</version>)',lambda m:m[1]+str(version)+m[2],s);assert n==1
after=ET.fromstring(s);assert len(before)==len(after)
for x,y in zip(before,after):
 if ET.tostring(x)!=ET.tostring(y):assert x.tag=='version' or x.attrib.get('package_name') in plan['apps']
assert a.output.resolve()!=a.xml.resolve(),'Use a separate output path'
a.output.write_text(s,encoding='utf-8',newline='\n');print(a.output)
