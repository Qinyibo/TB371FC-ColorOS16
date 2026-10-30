import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

/** Use the existing per-package PMS install policy. Does not alter APK signatures. */
public final class R93PatchGuard {
  static final String KEY = "persist.sys.custom_disallow_install_list";
  static final String PROBE = "com.tb371fc.r92.protectionprobe";
  static final String[] FIXED = {"com.android.launcher", "com.coloros.assistantscreen", "com.oplus.ota", "com.heytap.market"};
  public static void main(String[] args) throws Exception {
    Class<?> os = Class.forName("android.system.Os");
    int uid = (Integer) os.getMethod("getuid").invoke(null);
    if (uid == 0) {
      os.getMethod("setgid", int.class).invoke(null, 1000);
      os.getMethod("setuid", int.class).invoke(null, 1000);
    }
    if ((Integer) os.getMethod("getuid").invoke(null) != 1000)
      throw new IllegalStateException("system UID required");
    Class<?> c = Class.forName("android.os.oplusdevicepolicy.OplusDevicepolicyManager");
    Object manager = c.getMethod("getInstance").invoke(null);
    Method get = c.getMethod("getList", String.class, int.class);
    Object before = get.invoke(manager, KEY, 0);
    System.out.println("before=" + before);
    if (args.length == 0 || args[0].equals("read")) return;
    LinkedHashSet<String> merged = new LinkedHashSet<String>();
    if (before != null) merged.addAll((List<String>) before);
    for (String p : FIXED) merged.add(p);
    if (args[0].equals("with-probe")) merged.add(PROBE);
    else if (args[0].equals("apply")) merged.remove(PROBE);
    else throw new IllegalArgumentException("read/apply/with-probe");
    Object ok = c.getMethod("setList", String.class, List.class, int.class)
      .invoke(manager, KEY, new ArrayList<String>(merged), 0);
    if (!Boolean.TRUE.equals(ok)) throw new IllegalStateException("policy write rejected");
    Object after = get.invoke(manager, KEY, 0);
    if (after == null || !new LinkedHashSet<String>((List<String>)after).equals(merged))
      throw new IllegalStateException("policy readback mismatch");
    System.out.println("R93_PROTECTION_OK=" + after);
  }
}
