from pathlib import Path
import sys,time,xml.etree.ElementTree as E,re,json,subprocess
sys.stdout.reconfigure(encoding='utf-8');sys.path.insert(0,'work');import async_trial as t
O=Path(__file__).resolve().parent
def xml():
 t.shell('uiautomator dump /data/local/tmp/v23-bili-ui.xml >/dev/null')
 return E.fromstring(t.shell('cat /data/local/tmp/v23-bili-ui.xml'))
def config(s,component):
 m=re.search(r'Hist\s+#\d+: ActivityRecord\{[^\n]*'+re.escape(component)+r'[^\n]*',s);assert m,component
 text=re.search(r'CurrentConfiguration=([^\n]+)',s[m.start():m.start()+10000])[1]
 return [int(n) for n in re.findall(r'-?\d+',re.search(r'mBounds=Rect\(([^)]*)\)',text)[1].replace(' - ',','))]
try:
 t.shell('input keyevent KEYCODE_WAKEUP; wm dismiss-keyguard; wm user-rotation lock 1; svc power stayon usb')
 if '--current' not in sys.argv:t.shell('am force-stop tv.danmaku.bili; am start -W -n tv.danmaku.bili/.MainActivityV2')
 time.sleep(2)
 s=t.shell('dumpsys activity activities');home=config(s,'tv.danmaku.bili/.MainActivityV2');assert home[2]-home[0]==1149,home
 nodes=xml();search=next((n for n in nodes.iter('node') if n.attrib.get('resource-id') in ['tv.danmaku.bili:id/expand_search','tv.danmaku.bili:id/search_text']),None)
 if search is None:
  print('BILI_HOME_WIDTH_PASS_SEARCH_UI_NOT_READY',home);sys.exit(2)
 b=[int(v) for v in re.findall(r'\d+',search.attrib['bounds'])];t.shell('input tap '+str((b[0]+b[2])//2)+' '+str((b[1]+b[3])//2));time.sleep(3)
 s=t.shell('dumpsys activity activities');left=config(s,'tv.danmaku.bili/.MainActivityV2');assert left[0]==0 and 1024<=left[2]-left[0]<=1026,left
 assert 'com.bilibili.search2.main.BiliMainSearchActivity' in s
 with (O/'bili-native-dual.png').open('wb') as out:subprocess.run(t.ADB+['exec-out','screencap','-p'],stdout=out,check=True)
 r={'status':'NATIVE_BILI_HOME_WIDTH_AND_SEARCH_DUAL_PANES_PASS','home_bounds':home,'left_pane_bounds':left,'new_rules_module_required':False}
 (O/'bili-dual-result.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
finally:t.shell('input keyevent KEYCODE_HOME; wm user-rotation free; settings put global stay_on_while_plugged_in 0')
