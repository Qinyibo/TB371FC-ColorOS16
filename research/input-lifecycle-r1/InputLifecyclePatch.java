import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
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

/** Preserve unconditional gesture cleanup when its timeout is no longer queued. */
public final class InputLifecyclePatch {
    static final String OWNER = "Lcom/oplus/quickstep/gesture/helper/OplusInputInterceptHelper;";

    static boolean calls(Instruction ins, String owner, String name) {
        return ins instanceof ReferenceInstruction ri && ri.getReference() instanceof MethodReference mr
                && mr.getDefiningClass().equals(owner) && mr.getName().equals(name);
    }

    static Method patch(Method source) {
        if (!source.getName().equals("resetState") || !source.getParameterTypes().isEmpty()
                || !source.getReturnType().equals("V")) return source;
        var body = new MutableMethodImplementation(source.getImplementation());
        var ins = body.getInstructions();
        int query = -1, remove = -1, cleanup = -1;
        for (int i = 0; i < ins.size(); i++) {
            if (calls(ins.get(i), "Landroid/os/Handler;", "hasCallbacks")) query = i;
            if (calls(ins.get(i), "Landroid/os/Handler;", "removeCallbacks")) remove = i;
            if (ins.get(i).getOpcode() == Opcode.IPUT_OBJECT
                    && ins.get(i) instanceof ReferenceInstruction ri
                    && ri.getReference() instanceof FieldReference fr
                    && fr.getDefiningClass().equals(OWNER) && fr.getName().equals("velocityTracker")) cleanup = i;
        }
        if (query < 0 || remove <= query || cleanup <= remove)
            throw new IllegalStateException("Unexpected cleanup layout");
        var returns = new ArrayList<Integer>();
        for (int i = query + 1; i < remove; i++)
            if (ins.get(i).getOpcode() == Opcode.RETURN_VOID) returns.add(i);
        if (returns.size() != 1 || ins.get(returns.get(0)-1).getOpcode() != Opcode.IF_NEZ)
            throw new IllegalStateException("Expected one timeout-absent early return");
        // Only skip removing the absent callback. Listener, borrowed tracker,
        // handler and thresholds must still complete their existing cleanup.
        var target = body.newLabelForIndex(cleanup);
        body.replaceInstruction(returns.get(0), new BuilderInstruction10t(Opcode.GOTO, target));
        System.out.println("EDIT resetState return-void -> goto existing cleanup");
        return new ImmutableMethod(source.getDefiningClass(), source.getName(), source.getParameters(),
                source.getReturnType(), source.getAccessFlags(), source.getAnnotations(),
                source.getHiddenApiRestrictions(), body);
    }

    static ClassDef focused(ClassDef owner, Iterable<? extends Method> methods) {
        var selected = new ArrayList<Method>();
        for (var method : methods)
            if (Set.of("resetState", "resetThreshold", "<clinit>").contains(method.getName())) selected.add(method);
        // Isolation-only constructor; the methods under test and static setup
        // above remain the actual production bytecode, not hand translations.
        var ctor = new MutableMethodImplementation(1);
        ctor.addInstruction(new BuilderInstruction35c(Opcode.INVOKE_DIRECT, 1, 0, 0, 0, 0, 0,
                new ImmutableMethodReference("Ljava/lang/Object;", "<init>", List.of(), "V")));
        ctor.addInstruction(new BuilderInstruction10x(Opcode.RETURN_VOID));
        selected.add(new ImmutableMethod(OWNER, "<init>", List.of(), "V",
                AccessFlags.PUBLIC.getValue() | AccessFlags.CONSTRUCTOR.getValue(), Set.of(), Set.of(), ctor));
        return new ImmutableClassDef(OWNER, 1, "Ljava/lang/Object;", List.of(), owner.getSourceFile(),
                Set.of(), owner.getFields(), selected);
    }

    public static void main(String[] args) throws Exception {
        Path output = Path.of(args[1]);
        int edits = 0;
        try (var zip = new ZipFile(args[0])) {
            for (var entry : Collections.list(zip.entries())) {
                if (!entry.getName().matches("classes[0-9]*\\.dex")) continue;
                var dex = new DexBackedDexFile(Opcodes.forApi(36), zip.getInputStream(entry).readAllBytes());
                var classes = new ArrayList<ClassDef>();
                boolean changed = false;
                for (var c : dex.getClasses()) {
                    if (!c.getType().equals(OWNER)) { classes.add(c); continue; }
                    var methods = new ArrayList<Method>();
                    for (var m : c.getMethods()) {
                        var next = patch(m);
                        if (next != m) { edits++; changed = true; }
                        methods.add(next);
                    }
                    classes.add(new ImmutableClassDef(c.getType(), c.getAccessFlags(), c.getSuperclass(),
                            c.getInterfaces(), c.getSourceFile(), c.getAnnotations(), c.getFields(), methods));
                    // These methods only use legacy opcodes. DEX035 is for the
                    // isolated host translator; production retains its API.
                    DexPool.writeTo(output.resolve("before-focused.dex").toString(),
                            new ImmutableDexFile(Opcodes.forApi(23), List.of(focused(c, c.getMethods()))));
                    DexPool.writeTo(output.resolve("candidate-focused.dex").toString(),
                            new ImmutableDexFile(Opcodes.forApi(23), List.of(focused(c, methods))));
                }
                if (changed) {
                    DexPool.writeTo(output.resolve("candidate.dex").toString(),
                            new ImmutableDexFile(dex.getOpcodes(), classes));
                    Files.writeString(output.resolve("dex-name.txt"), entry.getName());
                }
            }
        }
        if (edits != 1) throw new IllegalStateException("Changed methods=" + edits);
    }
}
