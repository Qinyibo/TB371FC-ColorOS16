import java.lang.reflect.*;

public final class ChargerCompatTest {
    static final class Fake implements InvocationHandler {
        int version, calls, queries;
        boolean getterFails, versionFails;
        String value = "genuine-value";
        Fake(int version) { this.version = version; }
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            if (method.getName().equals("getInterfaceVersion")) {
                queries++;
                if (versionFails) throw remote("temporary version failure");
                return version;
            }
            if (method.getName().equals("getChgConfig")) {
                calls++;
                if (!args[0].equals(31) || !args[1].equals("30") || !args[2].equals(0)) throw new AssertionError("arguments changed");
                if (version <= 3 || getterFails) throw remote("unimplemented or transient getter");
                return value;
            }
            throw new AssertionError("Unexpected method " + method);
        }
        static Throwable remote(String text) throws Exception {
            return (Throwable)Class.forName("android.os.RemoteException").getConstructor(String.class).newInstance(text);
        }
    }
    static Object allocate(Class<?> type) throws Exception {
        Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
        Field field = unsafeClass.getDeclaredField("theUnsafe");
        field.setAccessible(true);
        return unsafeClass.getMethod("allocateInstance", Class.class).invoke(field.get(null), type);
    }
    public static void main(String[] args) throws Exception {
        Class<?> owner = Class.forName("com.android.server.OplusBatteryServiceFeature");
        Class<?> api = Class.forName("vendor.oplus.hardware.charger.ICharger");
        Object feature = allocate(owner); // Bypass constructor: never connect to a real charger.
        Field service = owner.getDeclaredField("mIChargerService"); service.setAccessible(true);
        Method get = owner.getMethod("getChgConfig", int.class, String.class, int.class);
        int failures = 0;
        for (int n = 0; n < 7; n++) {
            Fake fake = new Fake(n == 0 ? 1 : n == 1 || n == 6 ? 3 : n == 2 ? 4 : 9);
            fake.versionFails = n == 3;
            fake.getterFails = n == 4;
            if (n == 5) fake.value = null;
            service.set(feature, Proxy.newProxyInstance(api.getClassLoader(), new Class<?>[]{api}, fake));
            String expected = fake.version <= 3 || fake.versionFails || fake.getterFails ? "-1" : fake.value;
            for (int repeat = 0; repeat < 2; repeat++) {
                Object result = get.invoke(feature, 31, "30", 0);
                if (expected == null ? result != null : !expected.equals(result)) failures++;
            }
            int expectedCalls = fake.version <= 3 || fake.versionFails ? 0 : 2;
            boolean pass = fake.calls == expectedCalls;
            if (!pass) failures++;
            System.out.println("case=" + n + " version=" + fake.version + " queries=" + fake.queries + " getter_calls=" + fake.calls + " pass=" + pass);
        }
        System.out.println("REAL_METHOD_ART_TEST failures=" + failures + " constructor_bypassed=true real_charger_access=false");
        if (failures != 0) System.exit(1);
    }
}
