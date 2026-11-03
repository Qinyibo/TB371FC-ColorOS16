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

public final class ChargerCompatPatch {
    static final String OWNER = "Lcom/android/server/OplusBatteryServiceFeature;";
    static final String CHARGER = "Lvendor/oplus/hardware/charger/ICharger;";
    public static void main(String[] args) throws Exception {
        var source = new DexBackedDexFile(Opcodes.forApi(36), Files.readAllBytes(Path.of(args[0])));
        var classes = new ArrayList<ClassDef>();
        var focused = new ArrayList<ClassDef>();
        var originalFocused = new ArrayList<ClassDef>();
        int changed = 0;
        for (var c : source.getClasses()) {
            ClassDef output = c;
            if (c.getType().equals(OWNER)) {
                var methods = new ArrayList<Method>();
                for (var m : c.getMethods()) {
                    if (!m.getName().equals("getChgConfig")) { methods.add(m); continue; }
                    if (!m.getParameterTypes().toString().equals("[I, Ljava/lang/String;, I]") || !m.getReturnType().equals("Ljava/lang/String;")) throw new IllegalStateException("signature");
                    var b = new MutableMethodImplementation(m.getImplementation());
                    if (b.getRegisterCount() != 9) throw new IllegalStateException("registers");
                    int call = -1, end = -1;
                    for (int i = 0; i < b.getInstructions().size(); i++) {
                        var ins = b.getInstructions().get(i);
                        if (ins.getOpcode() == Opcode.INVOKE_INTERFACE && ins instanceof ReferenceInstruction ri && ri.getReference() instanceof MethodReference r && r.getDefiningClass().equals(CHARGER) && r.getName().equals("getChgConfig")) call = i;
                        if (ins.getOpcode() == Opcode.RETURN_OBJECT && ((OneRegisterInstruction)ins).getRegisterA() == 0) end = i;
                    }
                    if (call < 0 || end < call) throw new IllegalStateException("baseline layout");
                    var prior = b.getInstructions().get(call - 1);
                    if (prior.getOpcode() != Opcode.IGET_OBJECT || ((TwoRegisterInstruction)prior).getRegisterA() != 1) throw new IllegalStateException("service register");
                    var returnUnknown = b.newLabelForIndex(end);
                    // V3's frozen dispatch covers transactions 1..126; this
                    // getter is transaction128. Keep the existing unknown
                    // sentinel instead of sending a known-unsupported request.
                    b.addInstruction(call++, new BuilderInstruction35c(Opcode.INVOKE_INTERFACE, 1, 1, 0, 0, 0, 0,
                        new ImmutableMethodReference(CHARGER, "getInterfaceVersion", List.of(), "I")));
                    b.addInstruction(call++, new BuilderInstruction11x(Opcode.MOVE_RESULT, 3));
                    b.addInstruction(call++, new BuilderInstruction11n(Opcode.CONST_4, 4, 3));
                    b.addInstruction(call, new BuilderInstruction22t(Opcode.IF_LE, 3, 4, returnUnknown));
                    methods.add(new ImmutableMethod(c.getType(), m.getName(), m.getParameters(), m.getReturnType(), m.getAccessFlags(), m.getAnnotations(), m.getHiddenApiRestrictions(), b));
                    changed++;
                }
                output = new ImmutableClassDef(c.getType(), c.getAccessFlags(), c.getSuperclass(), c.getInterfaces(), c.getSourceFile(), c.getAnnotations(), c.getFields(), methods);
            }
            classes.add(output);
            if (c.getType().startsWith("Lcom/android/server/OplusBatteryServiceFeature") || c.getType().startsWith("Lcom/android/server/IOplusBatteryServiceFeature")) {
                focused.add(output); originalFocused.add(c);
            }
        }
        if (changed != 1) throw new IllegalStateException("changed=" + changed);
        DexPool.writeTo(args[1], new ImmutableDexFile(source.getOpcodes(), classes));
        DexPool.writeTo(args[2], new ImmutableDexFile(source.getOpcodes(), focused));
        DexPool.writeTo(args[3], new ImmutableDexFile(source.getOpcodes(), originalFocused));
        System.out.println("PATCHED_ONE_METHOD focused_classes=" + focused.size());
    }
}
