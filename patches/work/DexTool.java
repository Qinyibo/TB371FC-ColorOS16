import java.io.*;
import java.nio.file.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.baksmali.*;
public class DexTool {
 public static void main(String[] a) throws Exception {
  if (a[0].equals("dis")) {
   var dex=new DexBackedDexFile(Opcodes.forApi(36),Files.readAllBytes(Path.of(a[1])));
   var opt=new BaksmaliOptions();opt.apiLevel=36;
   if(!Baksmali.disassembleDexFile(dex,new File(a[2]),4,opt))throw new RuntimeException("disassemble failed");
  } else {
   brut.androlib.src.SmaliBuilder.build(new brut.directory.ExtFile(a[1]),new File(a[2]),36);
  }
 }
}
