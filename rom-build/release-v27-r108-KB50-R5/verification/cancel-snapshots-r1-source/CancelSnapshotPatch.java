import java.nio.file.*;import java.util.*;import java.util.zip.*;
import com.android.tools.smali.dexlib2.*;import com.android.tools.smali.dexlib2.builder.*;import com.android.tools.smali.dexlib2.builder.instruction.*;import com.android.tools.smali.dexlib2.dexbacked.*;import com.android.tools.smali.dexlib2.iface.*;import com.android.tools.smali.dexlib2.iface.instruction.*;import com.android.tools.smali.dexlib2.iface.reference.*;import com.android.tools.smali.dexlib2.immutable.*;import com.android.tools.smali.dexlib2.immutable.reference.*;import com.android.tools.smali.dexlib2.writer.pool.DexPool;
public class CancelSnapshotPatch {
 static final String OWNER="Lcom/android/wm/shell/recents/RecentsTransitionHandler$RecentsController;",STATE="Lcom/android/wm/shell/recents/RecentsTransitionHandler$TaskState;";
 static boolean call(Instruction i,String owner,String name){return i instanceof ReferenceInstruction r && r.getReference() instanceof MethodReference m && m.getDefiningClass().equals(owner)&&m.getName().equals(name);}
 static boolean field(Instruction i,String owner,String name){return i instanceof ReferenceInstruction r&&r.getReference() instanceof FieldReference f&&f.getDefiningClass().equals(owner)&&f.getName().equals(name);}
 static ClassDef focused(ClassDef c,Method m){return new ImmutableClassDef(c.getType(),1,"Ljava/lang/Object;",List.of(),null,Set.of(),List.of(new ImmutableField(OWNER,"mPausingTasks","Ljava/util/ArrayList;",1,null,Set.of(),Set.of()),new ImmutableField(OWNER,"mInstanceId","I",1,null,Set.of(),Set.of())),List.of(m));}
 public static void main(String[] a)throws Exception{
  Path out=Path.of(a[1]);int modified=0;
  try(ZipFile z=new ZipFile(a[0])) {for(var e:Collections.list(z.entries())){if(!e.getName().matches("classes[0-9]*\\.dex"))continue;var src=new DexBackedDexFile(Opcodes.forApi(36),z.getInputStream(e).readAllBytes());var classes=new ArrayList<ClassDef>();boolean found=false;
   for(var c:src.getClasses()){ClassDef result=c;if(c.getType().equals(OWNER)){found=true;var methods=new ArrayList<Method>();for(var m:c.getMethods()){
    if(!m.getName().equals("getSnapshotsForPausingTasks")){methods.add(m);continue;}
    var b=new MutableMethodImplementation(m.getImplementation());var ins=b.getInstructions();int get=-1,store=-1;
    if(b.getRegisterCount()!=13)throw new IllegalStateException("registers");
    for(int i=0;i<ins.size();i++){
     if(call(ins.get(i),"Ljava/util/ArrayList;","get")){if(get!=-1)throw new IllegalStateException("multiple get");get=i;}
     if(field(ins.get(i),"Landroid/app/ActivityManager$RunningTaskInfo;","taskId") && ins.get(i+1).getOpcode()==Opcode.INVOKE_INTERFACE && call(ins.get(i+1),"Landroid/app/IActivityTaskManager;","takeTaskSnapshot"))store=i+1;
     if(ins.get(i).getOpcode()==Opcode.APUT)throw new IllegalStateException("taskIds already assigned");
    }
    if(get<0||store<0)throw new IllegalStateException("layout");var g=(FiveRegisterInstruction)ins.get(get);
    if(g.getRegisterCount()!=2||g.getRegisterC()!=5||g.getRegisterD()!=3)throw new IllegalStateException("get registers");
    var ref=(MethodReference)((ReferenceInstruction)ins.get(get)).getReference();
    b.replaceInstruction(get,new BuilderInstruction35c(Opcode.INVOKE_VIRTUAL,2,5,4,0,0,0,ref));
    b.addInstruction(store,new BuilderInstruction23x(Opcode.APUT,5,0,4));
    var candidate=new ImmutableMethod(OWNER,m.getName(),m.getParameters(),m.getReturnType(),m.getAccessFlags(),m.getAnnotations(),m.getHiddenApiRestrictions(),b);methods.add(candidate);modified++;
    DexPool.writeTo(out.resolve("old-focused.dex").toString(),new ImmutableDexFile(src.getOpcodes(),List.of(focused(c,m))));
    DexPool.writeTo(out.resolve("candidate-focused.dex").toString(),new ImmutableDexFile(src.getOpcodes(),List.of(focused(c,candidate))));
   }result=new ImmutableClassDef(c.getType(),c.getAccessFlags(),c.getSuperclass(),c.getInterfaces(),c.getSourceFile(),c.getAnnotations(),c.getFields(),methods);}classes.add(result);}
   if(found){Files.write(out.resolve("before.dex"),z.getInputStream(e).readAllBytes());DexPool.writeTo(out.resolve("candidate.dex").toString(),new ImmutableDexFile(src.getOpcodes(),classes));Files.writeString(out.resolve("dex-name.txt"),e.getName());System.out.println("PATCHED "+e.getName()+" one method; task index and task ID only");}
  }}if(modified!=1)throw new IllegalStateException("modified="+modified);
 }
}
