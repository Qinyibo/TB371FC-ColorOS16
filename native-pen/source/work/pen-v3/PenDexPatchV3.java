import java.io.File;
import java.util.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.immutable.*;
import com.android.tools.smali.dexlib2.immutable.reference.*;
import com.android.tools.smali.dexlib2.builder.*;
import com.android.tools.smali.dexlib2.builder.instruction.*;

/** Narrow DEX edit preserving annotations, code, debug locations and exception labels. */
public final class PenDexPatchV3 {
    static final String SESSION="Lorg/tb371fc/pen/PenSession;";
    static final String GATT="Lorg/tb371fc/pen/NativeGatt;";
    static int edited;
    static String signature(Method m) { return m.getName()+"("+String.join("",m.getParameterTypes())+")"+m.getReturnType(); }
    static int parameterWords(Method m) {
        int n=(m.getAccessFlags()&8)!=0?0:1;
        for(CharSequence p:m.getParameterTypes()) n+=p.toString().equals("J")||p.toString().equals("D")?2:1;
        return n;
    }
    static ImmutableMethodReference ref(String type,String name,String result,String... args) {
        return new ImmutableMethodReference(type,name,Arrays.asList(args),result);
    }
    static Method patch(Method method,String mode) {
        String c=method.getDefiningClass(),sig=signature(method),kind=null;
        if(mode.equals("ipe") && c.equals("Lcom/oplus/ipemanager/btadsorb/util/p;") && sig.equals("M(Landroid/content/Context;Ljava/lang/String;)Z")) kind="name";
        if(mode.equals("ws") && c.equals("LF2/y;") && sig.equals("q(Ljava/lang/String;)Z")) kind="name";
        if(mode.equals("ipe") && c.equals("Lcom/oplus/ipemanager/btadsorb/ble/e0;")) {
            if(sig.equals("k(Landroid/bluetooth/BluetoothGatt;)V")) kind="services";
            if(sig.equals("i()V")) kind="connected";
            if(sig.equals("h(I)V")) kind="descriptor";
            if(sig.equals("j()V")) kind="disconnect";
            if(sig.equals("e(Landroid/bluetooth/BluetoothGattCharacteristic;)V")) kind="notify";
            if(sig.equals("f(Landroid/bluetooth/BluetoothGattCharacteristic;I)V")) kind="read";
        }
        if(mode.equals("ipe") && c.equals("Lcom/oplus/ipemanager/btadsorb/CoreService;")) {
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
        if(kind==null) return method;
        MethodImplementation original=method.getImplementation();
        if(original==null) throw new IllegalStateException("No implementation: "+sig);
        int registers=original.getRegisterCount(),params=parameterWords(method),start=registers-params;
        if(start<1) throw new IllegalStateException("No v0 scratch: "+sig);
        MutableMethodImplementation b=new MutableMethodImplementation(original);
        List<BuilderInstruction> prefix=new ArrayList<>();
        ImmutableMethodReference target;
        int words=params;
        switch(kind) {
            case "read33": target=ref(GATT,"readValue","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","[B","I");break;
            case "readlegacy": target=ref(GATT,"readLegacy","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;","I");break;
            case "changedlegacy": target=ref(GATT,"changed","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","Landroid/bluetooth/BluetoothGattCharacteristic;");break;
            case "serviceresult": target=ref(GATT,"serviceResult","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;","I");break;
            case "name": target=ref(SESSION,"officialName","Z","Ljava/lang/String;"); start=registers-1; words=1; break;
            case "connected": target=ref(GATT,"connected","Z","Ljava/lang/Object;"); break;
            case "services": target=ref(GATT,"services","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGatt;"); break;
            case "descriptor": target=ref(GATT,"descriptor","Z","Ljava/lang/Object;","I"); break;
            case "disconnect": target=ref(GATT,"disconnected","V","Ljava/lang/Object;"); break;
            case "read": target=ref(GATT,"characteristic","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGattCharacteristic;","I"); break;
            case "notify": target=ref(GATT,"notification","Z","Ljava/lang/Object;","Landroid/bluetooth/BluetoothGattCharacteristic;"); break;
            default: throw new AssertionError(kind);
        }
        prefix.add(new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,start,words,target));
        if(!kind.equals("disconnect")) {
            prefix.add(new BuilderInstruction11x(Opcode.MOVE_RESULT,0));
            prefix.add(null);
            prefix.add(kind.equals("name")?new BuilderInstruction11x(Opcode.RETURN,0):new BuilderInstruction10x(Opcode.RETURN_VOID));
        }
        for(int i=prefix.size()-1;i>=0;i--) {
            b.addInstruction(0,prefix.get(i)==null?new BuilderInstruction10x(Opcode.NOP):prefix.get(i));
        }
        if(!kind.equals("disconnect")) {
            Label originalEntry=b.newLabelForIndex(prefix.size());
            b.replaceInstruction(2,new BuilderInstruction21t(Opcode.IF_EQZ,0,originalEntry));
        }
        edited++; System.out.println("EDIT "+c+" "+sig+" "+kind);
        return new ImmutableMethod(c,method.getName(),method.getParameters(),method.getReturnType(),method.getAccessFlags(),method.getAnnotations(),method.getHiddenApiRestrictions(),b);
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=3) throw new IllegalArgumentException("input.dex output.dex ipe|ws");
        DexBackedDexFile dex=DexFileFactory.loadDexFile(new File(args[0]),Opcodes.forApi(35));
        ArrayList<ClassDef> classes=new ArrayList<>();
        for(ClassDef c:dex.getClasses()) {
            ArrayList<Method> methods=new ArrayList<>();
            for(Method m:c.getMethods()) methods.add(patch(m,args[2]));
            if(args[2].equals("ipe") && c.getType().equals("Lcom/oplus/ipemanager/btadsorb/ble/e;")) {
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
            classes.add(new ImmutableClassDef(c.getType(),c.getAccessFlags(),c.getSuperclass(),c.getInterfaces(),c.getSourceFile(),c.getAnnotations(),c.getFields(),methods));
        }
        if(edited==0) { System.out.println("UNCHANGED"); return; }
        DexFileFactory.writeDexFile(args[1],new ImmutableDexFile(dex.getOpcodes(),classes));
        System.out.println("PATCHED "+edited+" methods");
    }
}
