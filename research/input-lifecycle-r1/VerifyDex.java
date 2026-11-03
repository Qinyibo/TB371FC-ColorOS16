import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;
import java.util.zip.*;
import com.android.tools.smali.dexlib2.*;
import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.dexlib2.iface.instruction.formats.ArrayPayload;

/** Compare final serialized APK method bodies, including registers and handlers. */
public final class VerifyDex {
    static final String[] VALUES = {"getRegisterA","getRegisterB","getRegisterC","getRegisterD",
        "getRegisterE","getRegisterF","getRegisterG","getRegisterCount","getStartRegister",
        "getNarrowLiteral","getWideLiteral","getCodeOffset","getReference","getReference2",
        "getVerificationError","getInlineIndex","getVtableIndex","getFieldOffset","getElementWidth"};
    static final ClassValue<List<java.lang.reflect.Method>> ACCESSORS = new ClassValue<>() {
        protected List<java.lang.reflect.Method> computeValue(Class<?> kind) {
            var result = new ArrayList<java.lang.reflect.Method>();
            for (String name : VALUES) {
                try { result.add(kind.getMethod(name)); }
                catch (NoSuchMethodException unused) {}
            }
            return result;
        }
    };
    static String instruction(Instruction i) throws Exception {
        var s = new StringBuilder(i.getOpcode().name());
        for (var getter : ACCESSORS.get(i.getClass()))
            s.append('|').append(getter.getName()).append('=').append(getter.invoke(i));
        if (i instanceof SwitchPayload payload)
            for (var item : payload.getSwitchElements()) s.append("|switch=").append(item.getKey()).append(':').append(item.getOffset());
        if (i instanceof ArrayPayload payload) s.append("|array=").append(payload.getArrayElements());
        return s.toString();
    }
    static List<String> body(MethodImplementation body) throws Exception {
        if (body == null) return List.of("abstract");
        var out = new ArrayList<String>();
        out.add("registers="+body.getRegisterCount());
        for (var i : body.getInstructions()) out.add(instruction(i));
        for (var t : body.getTryBlocks()) {
            var line = new StringBuilder("try=").append(t.getStartCodeAddress()).append(':').append(t.getCodeUnitCount());
            for (var h : t.getExceptionHandlers()) line.append('|').append(h.getExceptionType()).append(':').append(h.getHandlerCodeAddress());
            out.add(line.toString());
        }
        return out;
    }
    static Map<String,com.android.tools.smali.dexlib2.iface.Method> methods(Path apk, String dexName) throws Exception {
        var result = new TreeMap<String,com.android.tools.smali.dexlib2.iface.Method>();
        try (var zip = new ZipFile(apk.toFile())) {
            var dex = new DexBackedDexFile(Opcodes.forApi(36), zip.getInputStream(zip.getEntry(dexName)).readAllBytes());
            for (var c : dex.getClasses()) for (var m : c.getMethods()) result.put(m.toString(),m);
        }
        return result;
    }
    public static void main(String[] args) throws Exception {
        var before = methods(Path.of(args[0]),args[2]);
        var after = methods(Path.of(args[1]),args[2]);
        if (!before.keySet().equals(after.keySet())) throw new AssertionError("Method set changed");
        int changed=0;
        for (String key : before.keySet()) {
            var a=before.get(key);var b=after.get(key);
            if (a.getAccessFlags()!=b.getAccessFlags()) throw new AssertionError("Flags changed: "+key);
            var old=body(a.getImplementation());var next=body(b.getImplementation());
            if (old.equals(next)) continue;
            changed++;
            if (!key.equals(InputLifecyclePatch.OWNER+"->resetState()V") || old.size()!=next.size())
                throw new AssertionError("Unexpected change: "+key);
            int instructions=0;
            for(int i=0;i<old.size();i++) if(!old.get(i).equals(next.get(i))) {
                instructions++;
                if(!old.get(i).equals("RETURN_VOID") || !next.get(i).startsWith("GOTO|getCodeOffset="))
                    throw new AssertionError("Unexpected instruction change: "+old.get(i)+" -> "+next.get(i));
            }
            if(instructions!=1) throw new AssertionError("Changed instructions="+instructions);
        }
        if(changed!=1) throw new AssertionError("Changed methods="+changed);
        System.out.println("FINAL_APK_METHODS_COMPARED="+before.size()+" CHANGED_METHODS=1 CHANGED_INSTRUCTIONS=1");
    }
}
