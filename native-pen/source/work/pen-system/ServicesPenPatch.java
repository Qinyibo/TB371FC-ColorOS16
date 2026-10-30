import java.io.File;import java.util.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.immutable.*;
import com.android.tools.smali.dexlib2.immutable.reference.*;
import com.android.tools.smali.dexlib2.builder.*;
import com.android.tools.smali.dexlib2.builder.instruction.*;
public final class ServicesPenPatch {
 static int changed;
 static Method patch(Method m){
  if(!m.getDefiningClass().equals("Lcom/android/server/policy/PhoneWindowManager;"))return m;
  String name=m.getName();boolean ready=name.equals("systemReady")&&m.getParameterTypes().isEmpty()&&m.getReturnType().equals("V");
  boolean key=name.equals("interceptKeyBeforeQueueing")&&m.getParameterTypes().toString().equals("[Landroid/view/KeyEvent;, I]")&&m.getReturnType().equals("I");
  if(!ready&&!key)return m;MethodImplementation old=m.getImplementation();int regs=old.getRegisterCount(),start=regs-(ready?1:3);
  MutableMethodImplementation b=new MutableMethodImplementation(old);
  if(ready){ImmutableMethodReference ref=new ImmutableMethodReference("Lorg/tb371fc/pen/system/NativePenSystem;","start",Arrays.asList("Ljava/lang/Object;"),"V");
   for(int i=b.getInstructions().size()-1;i>=0;i--)if(b.getInstructions().get(i).getOpcode()==Opcode.RETURN_VOID)b.addInstruction(i,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,start,1,ref));
  }else{if(start<1)throw new IllegalStateException("No scratch register");
   ImmutableMethodReference ref=new ImmutableMethodReference("Lorg/tb371fc/pen/system/NativePenSystem;","key",Arrays.asList("Ljava/lang/Object;","Landroid/view/KeyEvent;"),"Z");
   b.addInstruction(0,new BuilderInstruction11x(Opcode.RETURN,0));b.addInstruction(0,new BuilderInstruction11n(Opcode.CONST_4,0,0));b.addInstruction(0,new BuilderInstruction10x(Opcode.NOP));
   b.addInstruction(0,new BuilderInstruction11x(Opcode.MOVE_RESULT,0));b.addInstruction(0,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,start,2,ref));
   Label original=b.newLabelForIndex(5);b.replaceInstruction(2,new BuilderInstruction21t(Opcode.IF_EQZ,0,original));
  }
  changed++;System.out.println("EDIT "+m.getDefiningClass()+" "+name);
  return new ImmutableMethod(m.getDefiningClass(),m.getName(),m.getParameters(),m.getReturnType(),m.getAccessFlags(),m.getAnnotations(),m.getHiddenApiRestrictions(),b);
 }
 public static void main(String[] args)throws Exception{
  DexBackedDexFile dex=DexFileFactory.loadDexFile(new File(args[0]),Opcodes.forApi(36));List<ClassDef> classes=new ArrayList<>();
  for(ClassDef c:dex.getClasses()){List<Method> methods=new ArrayList<>();for(Method m:c.getMethods())methods.add(patch(m));classes.add(new ImmutableClassDef(c.getType(),c.getAccessFlags(),c.getSuperclass(),c.getInterfaces(),c.getSourceFile(),c.getAnnotations(),c.getFields(),methods));}
  if(changed>0)DexFileFactory.writeDexFile(args[1],new ImmutableDexFile(dex.getOpcodes(),classes));System.out.println("PATCHED "+changed);
 }
}
