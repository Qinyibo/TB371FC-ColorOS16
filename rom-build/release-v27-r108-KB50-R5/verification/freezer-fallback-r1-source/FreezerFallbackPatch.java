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

public final class FreezerFallbackPatch {
    static final String OWNER = "Lcom/android/server/am/CachedAppOptimizerExtImpl;";
    static final String HANS = "Lcom/android/server/am/OplusHansManager;";
    static boolean calls(Instruction i, String name) {
        return i instanceof ReferenceInstruction r && r.getReference() instanceof MethodReference m
            && m.getDefiningClass().equals(HANS) && m.getName().equals(name);
    }
    public static void main(String[] args) throws Exception {
        var source = new DexBackedDexFile(Opcodes.forApi(36), Files.readAllBytes(Path.of(args[0])));
        var classes = new ArrayList<ClassDef>();
        var focused = new ArrayList<ClassDef>();
        var original = new ArrayList<ClassDef>();
        int changed = 0;
        for (var c : source.getClasses()) {
            ClassDef output = c;
            if (c.getType().equals(OWNER)) {
                var methods = new ArrayList<Method>();
                for (var m : c.getMethods()) {
                    if (!m.getName().equals("checkFreezeProc")) { methods.add(m); continue; }
                    if (!m.getParameterTypes().toString().equals("[Lcom/android/server/am/ProcessRecord;]")
                        || !m.getReturnType().equals("Z")) throw new IllegalStateException("signature");
                    var b = new MutableMethodImplementation(m.getImplementation());
                    var ins = b.getInstructions();
                    if (b.getRegisterCount() != 9 || ins.size() < 8
                        || !calls(ins.get(0), "getInstance")
                        || ins.get(1).getOpcode() != Opcode.MOVE_RESULT_OBJECT
                        || !calls(ins.get(2), "isPermissionDisable")
                        || ins.get(3).getOpcode() != Opcode.MOVE_RESULT
                        || ins.get(4).getOpcode() != Opcode.CONST_4
                        || ((OneRegisterInstruction)ins.get(4)).getRegisterA() != 1
                        || ins.get(5).getOpcode() != Opcode.CONST_4
                        || ((OneRegisterInstruction)ins.get(5)).getRegisterA() != 2
                        || ins.get(6).getOpcode() != Opcode.IF_EQZ)
                        throw new IllegalStateException("unexpected baseline layout");
                    var permissionQuery = b.newLabelForIndex(2);
                    var initializeBranch = b.newLabelForIndex(4);
                    // Reuse the existing AOSP-only/permission-disabled branch,
                    // including its quota exemption. Do not change global
                    // permission policy, freeze eligibility, or thaw ownership.
                    int at = 2;
                    b.addInstruction(at++, new BuilderInstruction35c(Opcode.INVOKE_VIRTUAL, 1, 0, 0, 0, 0, 0,
                        new ImmutableMethodReference(HANS, "isReady", List.of(), "Z")));
                    b.addInstruction(at++, new BuilderInstruction11x(Opcode.MOVE_RESULT, 3));
                    b.addInstruction(at++, new BuilderInstruction21t(Opcode.IF_NEZ, 3, permissionQuery));
                    b.addInstruction(at++, new BuilderInstruction11n(Opcode.CONST_4, 0, 1));
                    b.addInstruction(at, new BuilderInstruction10t(Opcode.GOTO, initializeBranch));
                    methods.add(new ImmutableMethod(c.getType(), m.getName(), m.getParameters(), m.getReturnType(),
                        m.getAccessFlags(), m.getAnnotations(), m.getHiddenApiRestrictions(), b));
                    changed++;
                }
                output = new ImmutableClassDef(c.getType(), c.getAccessFlags(), c.getSuperclass(), c.getInterfaces(),
                    c.getSourceFile(), c.getAnnotations(), c.getFields(), methods);
                focused.add(output);
                original.add(c);
            }
            classes.add(output);
        }
        if (changed != 1) throw new IllegalStateException("changed=" + changed);
        DexPool.writeTo(args[1], new ImmutableDexFile(source.getOpcodes(), classes));
        DexPool.writeTo(args[2], new ImmutableDexFile(source.getOpcodes(), focused));
        DexPool.writeTo(args[3], new ImmutableDexFile(source.getOpcodes(), original));
        System.out.println("PATCHED_ONE_METHOD checkFreezeProc; existing quota and thaw paths retained");
    }
}
