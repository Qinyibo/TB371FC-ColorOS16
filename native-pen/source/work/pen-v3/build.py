from pathlib import Path
import subprocess,zipfile,re,hashlib,json,sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
W=Path(__file__).resolve().parent;O=W.parent.parent/'inputs/pen-native-v1'
J=Path('C:/Program Files/Java/jdk-21/bin');S=Path('C:/android-sdk');B=W/'build';B.mkdir(exist_ok=True)
def run(a,name):
 p=subprocess.run(list(map(str,a)),capture_output=True,timeout=120);out=(p.stdout+p.stderr).decode('utf-8','replace');(B/(name+'.log')).write_text(out,encoding='utf-8')
 if p.returncode:raise RuntimeError(name+'\n'+out[-3000:])
 return out
patch=(O/'dex-tools/PenDexPatch.java').read_text(encoding='utf-8').replace('PenDexPatch','PenDexPatchV3')
needle='''        if(kind==null) return method;'''
special='''        if(mode.equals("ipe") && c.equals("Lcom/oplus/ipemanager/btadsorb/CoreService;")) {
            String action=sig.equals("onCreate()V")?"created":sig.equals("onDestroy()V")?"destroyed":sig.equals("onStartCommand(Landroid/content/Intent;II)I")?"started":null;
            if(action!=null) {
                MethodImplementation original=method.getImplementation();
                MutableMethodImplementation b=new MutableMethodImplementation(original);
                int start=original.getRegisterCount()-parameterWords(method);
                ImmutableMethodReference target=action.equals("started")?ref("Lorg/tb371fc/pen/NativePenLifecycle;",action,"V","Ljava/lang/Object;","Landroid/content/Intent;"):ref("Lorg/tb371fc/pen/NativePenLifecycle;",action,"V","Ljava/lang/Object;");
                if(action.equals("created")) {
                    for(int i=b.getInstructions().size()-1;i>=0;i--)if(b.getInstructions().get(i).getOpcode()==Opcode.RETURN_VOID)b.addInstruction(i,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,start,1,target));
                }else b.addInstruction(0,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,start,action.equals("started")?2:1,target));
                edited++;System.out.println("EDIT "+c+" "+sig+" "+action);
                return new ImmutableMethod(c,method.getName(),method.getParameters(),method.getReturnType(),method.getAccessFlags(),method.getAnnotations(),method.getHiddenApiRestrictions(),b);
            }
        }
        if(mode.equals("ipe") && c.equals("Lcom/oplus/ipemanager/btadsorb/ble/e;")) {
            if(sig.equals("onCharacteristicRead(Landroid/bluetooth/BluetoothGatt;Landroid/bluetooth/BluetoothGattCharacteristic;[BI)V"))kind="read33";
            if(sig.equals("onCharacteristicRead(Landroid/bluetooth/BluetoothGatt;Landroid/bluetooth/BluetoothGattCharacteristic;I)V"))kind="readlegacy";
            if(sig.equals("onCharacteristicChanged(Landroid/bluetooth/BluetoothGatt;Landroid/bluetooth/BluetoothGattCharacteristic;)V"))kind="changedlegacy";
            if(sig.equals("onServicesDiscovered(Landroid/bluetooth/BluetoothGatt;I)V"))kind="serviceresult";
            if(sig.equals("onDescriptorWrite(Landroid/bluetooth/BluetoothGatt;Landroid/bluetooth/BluetoothGattDescriptor;I)V")) {
                MethodImplementationBuilder b=new MethodImplementationBuilder(4);
                b.addInstruction(new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,0,4,ref(GATT,"descriptorDispatch","V","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattDescriptor;","I")));
                b.addInstruction(new BuilderInstruction10x(Opcode.RETURN_VOID));edited++;System.out.println("EDIT "+c+" "+sig+" descriptorDispatch");
                return new ImmutableMethod(c,method.getName(),method.getParameters(),method.getReturnType(),method.getAccessFlags(),method.getAnnotations(),method.getHiddenApiRestrictions(),b.getMethodImplementation());
            }
        }
        if(kind==null) return method;'''
assert needle in patch;patch=patch.replace(needle,special)
needle='''            case "name": target='''
cases='''            case "read33": target=ref(GATT,"readValue","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","[B","I");break;
            case "readlegacy": target=ref(GATT,"readLegacy","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","I");break;
            case "changedlegacy": target=ref(GATT,"changed","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;");break;
            case "serviceresult": target=ref(GATT,"serviceResult","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","I");break;
            case "name": target='''
patch=patch.replace(needle,cases)
needle='''            classes.add(new ImmutableClassDef'''
extra='''            if(args[2].equals("ipe") && c.getType().equals("Lcom/oplus/ipemanager/btadsorb/ble/e;")) {
                MethodImplementationBuilder b=new MethodImplementationBuilder(5);
                b.addInstruction(new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,1,4,ref(GATT,"changedValue","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","[B")));
                b.addInstruction(new BuilderInstruction11x(Opcode.MOVE_RESULT,0));
                b.addInstruction(new BuilderInstruction21t(Opcode.IF_EQZ,0,b.getLabel("fallback")));
                b.addInstruction(new BuilderInstruction10x(Opcode.RETURN_VOID));b.addLabel("fallback");
                b.addInstruction(new BuilderInstruction3rc(Opcode.INVOKE_SUPER_RANGE,1,4,ref("Landroid/bluetooth/BluetoothGattCallback;","onCharacteristicChanged","V","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","[B")));
                b.addInstruction(new BuilderInstruction10x(Opcode.RETURN_VOID));
                java.util.List<ImmutableMethodParameter> parameters=Arrays.asList(new ImmutableMethodParameter("Landroid/bluetooth/BluetoothGatt;",null,"gatt"),new ImmutableMethodParameter("Landroid/bluetooth/BluetoothGattCharacteristic;",null,"characteristic"),new ImmutableMethodParameter("[B",null,"value"));
                methods.add(new ImmutableMethod(c.getType(),"onCharacteristicChanged",parameters,"V",17,null,null,b.getMethodImplementation()));edited++;System.out.println("ADD value-snapshot notification callback");
            }
            classes.add(new ImmutableClassDef'''
patch=patch.replace(needle,extra)
(W/'PenDexPatchV3.java').write_text(patch,encoding='utf-8')
libs=[p for p in (S/'cmdline-tools/latest/lib').rglob('*.jar') if any(k in str(p) for k in ['smali','guava','failureaccess'])];cp=';'.join(map(str,libs))
P=B/'patcher';P.mkdir(exist_ok=True);run([J/'javac.exe','-cp',cp,'-d',P,W/'PenDexPatchV3.java'],'patcher')
C=B/'classes';C.mkdir(exist_ok=True);src=list((W/'src').rglob('*.java'));run([J/'javac.exe','--release','8','-cp',S/'platforms/android-36/android.jar','-d',C,*src],'javac')
jar=B/'classes.jar'
with zipfile.ZipFile(jar,'w')as z:
 for p in C.rglob('*.class'):z.write(p,p.relative_to(C).as_posix())
D=B/'dex';D.mkdir(exist_ok=True);run([S/'build-tools/36.0.0/d8.bat','--min-api','35','--lib',S/'platforms/android-36/android.jar','--output',D,jar],'d8')
rows={}
for mode,pkg,expected in [('ipe','com.oplus.ipemanager',16),('ws','com.oplus.wirelesssettings',1)]:
 source=O/'runtime-contract-v1'/(pkg+'.apk');replacements={};count=0;T=B/mode;T.mkdir(exist_ok=True)
 with zipfile.ZipFile(source)as z:
  names=[n for n in z.namelist()if re.fullmatch(r'classes\d*\.dex',n)]
  for n in names:
   (T/n).write_bytes(z.read(n));out=T/(n+'.patched');log=run([J/'java.exe','-cp',str(P)+';'+cp,'PenDexPatchV3',T/n,out,mode],mode+'-'+n)
   m=re.search(r'PATCHED (\d+) methods',log)
   if m:count+=int(m[1]);replacements[n]=out.read_bytes()
  assert count==expected,(mode,count,expected)
  extra='classes'+str(max(1 if n=='classes.dex'else int(re.search(r'\d+',n)[0])for n in names)+1)+'.dex'
  unaligned=T/'unaligned.apk'
  with zipfile.ZipFile(unaligned,'w')as dest:
   for e in z.infolist():dest.writestr(e,replacements.get(e.filename,z.read(e.filename)))
   dest.writestr(extra,(D/'classes.dex').read_bytes())
  target=T/('IPeManager.apk'if mode=='ipe'else 'WirelessSettings.apk')
  run([S/'build-tools/36.0.0/zipalign.exe','-P','16','-f','4',unaligned,target],mode+'-align')
  run([S/'build-tools/36.0.0/zipalign.exe','-c','-P','16','4',target],mode+'-alignment-check')
  rows[mode]={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'patched_or_added_methods':count,'target':str(target)}
(B/'result.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
