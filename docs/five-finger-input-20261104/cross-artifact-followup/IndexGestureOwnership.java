import java.nio.file.*;
import java.io.*;
import java.util.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.dexlib2.iface.reference.*;
import com.android.tools.smali.baksmali.*;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;
public final class IndexGestureOwnership {
 static final Set<String> names=Set.of("cleanupGestureAnimation","hasGestureAnimationController","shouldApplyInputConsumer","updateInputConsumerForApp","scheduleFailsafe","createInputConsumer","destroyInputConsumer","setInputConsumerEnabled","enableInputConsumer","disableInputConsumer","registerInputConsumer","unregisterInputConsumer","getInputConsumerEnabled","performFinishAnimation","performFinishAnimationInWms");
 static final Set<String> fields=Set.of("mInputConsumerEnabled","mGestureFullScreenDragStart");
 static String q(String s){return "\""+s.replace("\\","\\\\").replace("\"","\\\"")+"\"";}
 static String sig(Method m){return m.getDefiningClass()+"->"+m.getName()+m.getParameterTypes()+m.getReturnType();}
 public static void main(String[] a)throws Exception{
 var out=Paths.get(a[1]);Files.createDirectories(out);
 var options=new BaksmaliOptions();options.apiLevel=35;
 var container=DexFileFactory.loadDexContainer(new File(a[0]),Opcodes.forApi(35));
 var rows=new ArrayList<String>();var selected=new ArrayList<String>();int classes=0,methods=0;
 for(String entry:container.getDexEntryNames())for(ClassDef c:container.getEntry(entry).getDexFile().getClasses()){
 classes++;boolean export=false;
 for(Method m:c.getMethods()){
 methods++;boolean hit=names.contains(m.getName());
 if(hit)rows.add("{\"kind\":\"definition\",\"dex\":"+q(entry)+",\"class\":"+q(c.getType())+",\"method\":"+q(sig(m))+",\"member\":"+q(m.getName())+"}");
 if(m.getImplementation()!=null){int ix=0;for(Instruction ins:m.getImplementation().getInstructions()){
 if(ins instanceof ReferenceInstruction ri){var ref=ri.getReference();String name=null,owner=null;
 if(ref instanceof MethodReference mr){name=mr.getName();owner=mr.getDefiningClass();if(!names.contains(name))name=null;}
 if(ref instanceof FieldReference fr){name=fr.getName();owner=fr.getDefiningClass();if(!fields.contains(name))name=null;}
 if(name!=null){hit=true;rows.add("{\"kind\":\"reference\",\"dex\":"+q(entry)+",\"class\":"+q(c.getType())+",\"method\":"+q(sig(m))+",\"instruction\":"+ix+",\"opcode\":"+q(ins.getOpcode().name())+",\"owner\":"+q(owner)+",\"member\":"+q(name)+"}");}
 }ix++;
 }}
 if(hit){export=true;selected.add("{\"class\":"+q(c.getType())+",\"method\":"+q(sig(m))+"}");}
 }
 if(export){var path=out.resolve("classes/"+c.getType().substring(1,c.getType().length()-1)+".smali");Files.createDirectories(path.getParent());try(var w=new BaksmaliWriter(Files.newBufferedWriter(path))){new ClassDefinition(options,c).writeTo(w);}}
 }
 Files.writeString(out.resolve("references.json"),"[\n"+String.join(",\n",rows)+"\n]\n");
 Files.writeString(out.resolve("methods.json"),"[\n"+String.join(",\n",selected)+"\n]\n");
 Files.writeString(out.resolve("scope.json"),"{\"classes_scanned\":"+classes+",\"methods_scanned\":"+methods+",\"dex_entries\":"+q(container.getDexEntryNames().toString())+"}\n");
 System.out.println("classes="+classes+" methods="+methods+" reference_rows="+rows.size()+" selected_methods="+selected.size());
 }
}
