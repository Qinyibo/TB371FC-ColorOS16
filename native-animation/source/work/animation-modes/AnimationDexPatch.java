import java.nio.file.*;
import java.util.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.builder.*;
import com.android.tools.smali.dexlib2.builder.instruction.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.dexlib2.iface.reference.*;
import com.android.tools.smali.dexlib2.immutable.*;
import com.android.tools.smali.dexlib2.immutable.reference.*;
import com.android.tools.smali.dexlib2.writer.pool.DexPool;

public final class AnimationDexPatch {
 static int count;
 static final String HELPER="Lorg/tb371fc/animation/LauncherCompat;";
 static ImmutableMethodReference ref(String cls,String name,String ret,String... params){return new ImmutableMethodReference(cls,name,Arrays.asList(params),ret);}
 static Method patch(Method m,String mode) {
  if(m.getImplementation()==null)return m;
  String c=m.getDefiningClass(),name=m.getName();
  var b=new MutableMethodImplementation(m.getImplementation());int changed=0;
  if(mode.equals("settings")&&c.equals("Lcom/oplus/settings/feature/display/DisplaySettingsFragment;")&&name.equals("onCreate")&&m.getParameterTypes().size()==1) {
   int self=b.getRegisterCount()-2;
   for(int i=b.getInstructions().size()-1;i>=0;i--)if(b.getInstructions().get(i).getOpcode()==Opcode.RETURN_VOID){
    b.addInstruction(i,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,self,1,ref("Lorg/tb371fc/animation/AnimationSettings;","attach","V","Ljava/lang/Object;")));changed++;
   }
  }
  if(mode.equals("launcher")&&c.endsWith("/OplusStackRecentsConfig;")&&name.equals("isAnimLevelSupportedStack")) {
   b=new MutableMethodImplementation(1);
   b.addInstruction(new BuilderInstruction35c(Opcode.INVOKE_STATIC,0,0,0,0,0,0,ref(HELPER,"supportsStack","Z")));
   b.addInstruction(new BuilderInstruction11x(Opcode.MOVE_RESULT,0));b.addInstruction(new BuilderInstruction11x(Opcode.RETURN,0));changed++;
  } else if(mode.equals("launcher")) {
   if(c.equals("Lcom/android/quickstep/touch/SwipeToRecentMotionPauseDetector;")&&name.equals("addPosition")&&m.getParameterTypes().size()==2){
    int self=b.getRegisterCount()-3,event=self+1;
    // The vendor method reuses p1 for Float before returning: consume the
    // MotionEvent at entry, before its original register type is overwritten.
    b.addInstruction(0,new BuilderInstruction22c(Opcode.IGET,0,self,new ImmutableFieldReference(c,"mScreenHeight","I")));
    b.addInstruction(1,new BuilderInstruction35c(Opcode.INVOKE_VIRTUAL,3,self,event,0,0,0,ref("Lcom/android/quickstep/util/MotionPauseDetector;","r94ArmDesktopPause","V","Landroid/view/MotionEvent;","I")));changed++;
   }
   if(c.endsWith("/RecentsLightAnimUtil;")&&name.equals("isLightRecentAnim")){
    for(int i=b.getInstructions().size()-1;i>=0;i--){
     var ins=b.getInstructions().get(i);
     if(ins.getOpcode()==Opcode.RETURN){
      int r=((OneRegisterInstruction)ins).getRegisterA();
      b.addInstruction(i,new BuilderInstruction35c(Opcode.INVOKE_STATIC,1,r,0,0,0,0,ref(HELPER,"lightRecentWithoutStack","Z","Z")));
      b.addInstruction(i+1,new BuilderInstruction11x(Opcode.MOVE_RESULT,r));changed++;
     }
    }
   }
   boolean timings=(c.equals("Lcom/android/quickstep/AbsSwipeUpHandler;")&&Set.of("getTapToNewTaskDuration","handleNormalGestureEnd").contains(name))
     ||(c.equals("Lcom/android/quickstep/TaskViewUtils;")&&Set.of("composeRecentsLaunchAnimator","createRecentsWindowAnimator").contains(name))
     ||(c.endsWith("/SwipeToRecentAnimationHelper;")&&name.equals("goOverviewAnimation"))
     ||(c.endsWith("/AppToOverviewAnimationProvider;")&&name.equals("getRecentsLaunchDuration"))
     ||(c.endsWith("/RecentsLightAnimUtil;")&&name.equals("isDockIconAndClearAllPanelLightAnim"))
     ||(c.endsWith("/OplusRecentsViewImpl;")&&Set.of("onSwipeUpAnimationSuccess","setControlViewInvisibleWithAnimation","setControlViewVisibleWithAnimation").contains(name))
     ||(c.endsWith("/OplusBaseSwipeUpHandler;")&&(name.equals("onWindowAnimationEnd")||name.equals("onWindowAnimationStart$lambda$155")));
   for(int i=0;i<b.getInstructions().size();i++){
    var ins=b.getInstructions().get(i);if(!(ins instanceof ReferenceInstruction ri)||!(ri.getReference() instanceof MethodReference mr))continue;
    if(c.equals("Lcom/android/launcher/statemanager/OplusUiFactoryInjector;")&&name.equals("createTouchControllers")&&mr.getDefiningClass().equals("Lcom/android/common/util/PlatformLevelUtils;")&&mr.getName().equals("isAnimationLevel")){
     int level=((FiveRegisterInstruction)ins).getRegisterC();
     b.replaceInstruction(i,new BuilderInstruction35c(Opcode.INVOKE_STATIC,1,level,0,0,0,0,ref(HELPER,"lightDesktopController","Z","I")));changed++;
    }
    if(c.equals("Lcom/android/launcher3/anim/light/AppLaunchAnimUtil;")&&Set.of("getLightDragLayerAnim","getLightLauncherContentAnimation","getLightWindowAnimation").contains(name)&&mr.getName().equals("setDuration")&&mr.getParameterTypes().equals(List.of("J"))){
     if(!(ins instanceof FiveRegisterInstruction args))throw new IllegalStateException("Unexpected light transition duration call");
     int duration=args.getRegisterD();
     b.addInstruction(i,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,duration,2,ref(HELPER,"lightLaunchDuration","J","J")));
     b.addInstruction(i+1,new BuilderInstruction11x(Opcode.MOVE_RESULT_WIDE,duration));i+=2;changed++;
    }
    if(timings&&mr.getDefiningClass().equals("Lcom/android/common/util/LauncherAnimConfig;")&&mr.getName().equals("isLevelBOrBPlus")){
     b.replaceInstruction(i,new BuilderInstruction35c(Opcode.INVOKE_STATIC,0,0,0,0,0,0,ref(HELPER,"lightRecentsWithoutStack","Z")));changed++;
    }
    if(c.endsWith("/OplusRecentsViewStateControllerImpl;")&&name.equals("setState")&&mr.getDefiningClass().equals("Lcom/android/common/util/AppFeatureUtils;")&&mr.getName().equals("isLightEnterRecentsAnimation")){
     int receiver=((FiveRegisterInstruction)ins).getRegisterC();
     b.replaceInstruction(i,new BuilderInstruction35c(Opcode.INVOKE_STATIC,1,receiver,0,0,0,0,ref(HELPER,"lightEnterRecentsWithoutStack","Z","Lcom/android/common/util/AppFeatureUtils;")));changed++;
    }
    if(c.endsWith("/OplusTaskViewImpl;")&&name.equals("_init_$lambda$7")&&mr.getDefiningClass().equals("Lcom/android/common/util/LauncherAnimConfig;")&&mr.getName().equals("isAdaptiveLowAnimation")){
     b.replaceInstruction(i,new BuilderInstruction35c(Opcode.INVOKE_STATIC,0,0,0,0,0,0,ref(HELPER,"adaptiveLowWithoutStack","Z")));changed++;
    }
   }
   if(c.equals("Lcom/android/quickstep/AbsSwipeUpHandler;")&&name.equals("handleNormalGestureEnd")){
    for(int i=b.getInstructions().size()-1;i>=0;i--){
     var ins=b.getInstructions().get(i);
     if(ins instanceof WideLiteralInstruction lit&&lit.getWideLiteral()==700&&ins instanceof OneRegisterInstruction reg){
      int r=reg.getRegisterA();
      b.addInstruction(i+1,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,r,2,ref(HELPER,"stackTransitionDuration","J","J")));
      b.addInstruction(i+2,new BuilderInstruction11x(Opcode.MOVE_RESULT_WIDE,r));changed++;
     }
    }
   }
   if(c.equals("Lcom/android/quickstep/util/MotionPauseDetector;")&&Set.of("addPosition","checkMotionPaused").contains(name)){
    for(int i=b.getInstructions().size()-1;i>=0;i--){
     var ins=b.getInstructions().get(i);
     if(ins instanceof WideLiteralInstruction lit&&(lit.getWideLiteral()==300||lit.getWideLiteral()==400)&&ins instanceof OneRegisterInstruction reg){
      int r=reg.getRegisterA();
      b.addInstruction(i+1,new BuilderInstruction3rc(Opcode.INVOKE_STATIC_RANGE,r,2,ref(HELPER,"recentsPauseTimeout","J","J")));
      b.addInstruction(i+2,new BuilderInstruction11x(Opcode.MOVE_RESULT_WIDE,r));changed++;
     }
    }
   }
  }
  // Both modes use the high-quality wallpaper backdrop; tier 3 selects that path.
  // Keep all other AssistantScreen animation, card and material gates intact.
  // The tablet-only level-4 veto also closes the Assistant switch at service start.
  if(mode.equals("assistant")&&c.equals("LLz/l;")&&name.equals("d")&&m.getParameterTypes().isEmpty()&&m.getReturnType().equals("Z")){
   b=new MutableMethodImplementation(1);
   b.addInstruction(new BuilderInstruction11n(Opcode.CONST_4,0,0));
   b.addInstruction(new BuilderInstruction11x(Opcode.RETURN,0));changed++;
  }
  if(mode.equals("assistant")&&c.equals("Lro/d;")&&name.equals("invoke")){
   for(int i=0;i<b.getInstructions().size()-1;i++){
    var ins=b.getInstructions().get(i);if(!(ins instanceof ReferenceInstruction ri)||!(ri.getReference() instanceof MethodReference mr))continue;
    if(mr.getDefiningClass().equals("Lqk/i0;")&&mr.getName().equals("c")&&mr.getReturnType().equals("I")){
     var result=b.getInstructions().get(i+1);if(result.getOpcode()!=Opcode.MOVE_RESULT)throw new IllegalStateException("backdrop result");
     int reg=((OneRegisterInstruction)result).getRegisterA();
     b.replaceInstruction(i,new BuilderInstruction11n(Opcode.CONST_4,reg,3));
     b.replaceInstruction(i+1,new BuilderInstruction10x(Opcode.NOP));changed++;
    }
   }
  }
  if(changed==0)return m;
  count+=changed;if(changed>0)System.out.println("EDIT "+c+"->"+name+" changes="+changed);
  return new ImmutableMethod(c,name,m.getParameters(),m.getReturnType(),m.getAccessFlags(),m.getAnnotations(),m.getHiddenApiRestrictions(),b);
 }
 public static void main(String[] args)throws Exception{
  var dex=new DexBackedDexFile(Opcodes.forApi(36),Files.readAllBytes(Path.of(args[0])));var classes=new ArrayList<ClassDef>();var moved=new ArrayList<ClassDef>();
  for(var c:dex.getClasses()){
   int before=count;
   var methods=new ArrayList<Method>();for(var m:c.getMethods())methods.add(patch(m,args[2]));
   if(args[2].equals("launcher")&&c.getType().equals("Lcom/android/quickstep/util/MotionPauseDetector;")){
    var impl=new MutableMethodImplementation(4);
    impl.addInstruction(new BuilderInstruction22c(Opcode.IGET_OBJECT,0,1,new ImmutableFieldReference(c.getType(),"mForcePauseTimeout","Lcom/android/launcher3/Alarm;")));
    impl.addInstruction(new BuilderInstruction35c(Opcode.INVOKE_STATIC,3,0,2,3,0,0,ref(HELPER,"desktopPause","V","Lcom/android/launcher3/Alarm;","Landroid/view/MotionEvent;","I")));
    impl.addInstruction(new BuilderInstruction10x(Opcode.RETURN_VOID));
    methods.add(new ImmutableMethod(c.getType(),"r94ArmDesktopPause",List.of(new ImmutableMethodParameter("Landroid/view/MotionEvent;",Set.of(),null),new ImmutableMethodParameter("I",Set.of(),null)),"V",1,Set.of(),Set.of(),impl));
    count++;System.out.println("EDIT "+c.getType()+"->r94ArmDesktopPause changes=1");
   }
   var next=new ImmutableClassDef(c.getType(),c.getAccessFlags(),c.getSuperclass(),c.getInterfaces(),c.getSourceFile(),c.getAnnotations(),c.getFields(),methods);
   // Vendor dex files are at the 65536 method-reference limit. Move changed
   // classes into a new dex instead of overflowing or deleting vendor code.
   if(count>before&&!args[2].equals("assistant"))moved.add(next);else classes.add(next);
  }
  if(count>0)DexPool.writeTo(args[1],new ImmutableDexFile(dex.getOpcodes(),classes));
  if(!moved.isEmpty())DexPool.writeTo(args[1]+".moved",new ImmutableDexFile(dex.getOpcodes(),moved));
  System.out.println("PATCHED "+count);
 }
}
