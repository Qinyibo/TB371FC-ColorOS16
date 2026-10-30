from pathlib import Path
import re
p=Path('work/bili-native-middle-width');f=p/'smali/com/android/server/wm/CompactWindowBoundsCalculator.smali'
backup=p/'original-calculator.smali'
if not backup.exists():backup.write_bytes(f.read_bytes())
s=backup.read_text(encoding='utf-8')
pat=r'(?ms)^\.method public static calculateBoundsInPosition\(Lcom/android/server/wm/Task;I\)Landroid/graphics/Rect;\n.*?^\.end method'
def patch(m):
 text=m[0];needle='    int-to-float v5, v2\n';assert text.count(needle)==1
 extra='''
    const/high16 v2, -0x40800000
    cmpl-float v2, v5, v2
    if-nez v2, :bili_middle_native_end
    invoke-virtual {p0}, Lcom/android/server/wm/Task;->getBasePackageName()Ljava/lang/String;
    move-result-object v2
    const-string v3, "tv.danmaku.bili"
    invoke-virtual {v3, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :bili_middle_native_end
    const v5, 0x3fcccccd    # 1.6f; centered page width=(height/1.6)-1
    :bili_middle_native_end
'''
 return text.replace(needle,needle+extra)
s,n=re.subn(pat,patch,s);assert n==1
f.write_text(s,encoding='utf-8');(p/'patched-calculator.smali').write_text(s,encoding='utf-8')
print('One native method changed: Bili half-screen middle only; left/right/fullscreen paths unchanged')
