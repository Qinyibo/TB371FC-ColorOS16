import java.nio.file.*;
import java.io.*;
import java.util.regex.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.baksmali.*;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;
public final class ExportWakeContext {
 public static void main(String[] args)throws Exception{
 var out=Paths.get(args[1]);Files.createDirectories(out);
 var regex=Pattern.compile("(?i)(Keyguard|ScreenOn|ScreenOff|ScreenLifecycle|Wakefulness|WakeLock|PowerBlock|PowerManagerService|DisplayPowerController|DisplayPowerState|PhoneWindowManager|RuntimeInit|ApplicationExitInfo|ApplicationThread|KillApplication|SystemExitRestarter|Restarter|Watchdog|ExceptionHandler|CrashHandler|CentralSurfaces|GestureAnimation|MultiGesture|InputMonitor|InputConsumer|WindowAnimationManager|ZoomWindowManager|OplusActivityTaskManager|IOplusActivityTaskManager|OplusActivityManager|ScreenDraw|Screen.*Timeout|Timeout.*Screen)");
 var container=DexFileFactory.loadDexContainer(new File(args[0]),Opcodes.forApi(35));var opt=new BaksmaliOptions();opt.apiLevel=35;int count=0;
 for(String entry:container.getDexEntryNames())for(ClassDef def:container.getEntry(entry).getDexFile().getClasses()){
 if(!regex.matcher(def.getType()).find())continue;
 var path=out.resolve(def.getType().substring(1,def.getType().length()-1)+".smali");Files.createDirectories(path.getParent());
 try(var w=new BaksmaliWriter(Files.newBufferedWriter(path))){new ClassDefinition(opt,def).writeTo(w);}count++;
 }System.out.println("COMPLETE_CONTEXT_CLASSES="+count);
 }
}
