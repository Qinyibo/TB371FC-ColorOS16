import java.lang.reflect.*;
import java.util.*;
import android.os.Handler;
import android.view.MotionEvent;
import android.view.VelocityTracker;
import com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper$IGestureStateChangeListener;
import com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper$State;

/** Exercise extracted production methods, with only their OS environment stubbed. */
public final class LifecycleContractTest {
    static int checks, failures;
    static Class<?> type;

    static Object get(Object owner, String name) throws Exception {
        Field f = type.getDeclaredField(name); f.setAccessible(true); return f.get(owner);
    }
    static void set(Object owner, String name, Object value) throws Exception {
        Field f = type.getDeclaredField(name); f.setAccessible(true); f.set(owner, value);
    }
    static void check(boolean good, String name) {
        checks++;
        if (!good) { failures++; System.out.println("FAIL " + name); }
    }
    static void fixture(String timerState, boolean cui) throws Exception {
        Object owner = type.getConstructor().newInstance();
        Handler handler = timerState.equals("no-handler") ? null : new Handler(timerState);
        MotionEvent down = new MotionEvent(), up = new MotionEvent(), pointer = new MotionEvent();
        var pointers = new ArrayList<MotionEvent>(); pointers.add(pointer);
        var velocity = new VelocityTracker();
        var listener = new OplusInputInterceptHelper$IGestureStateChangeListener() {};
        var timeout = (Runnable) () -> {};
        set(owner, "firstMoveTime", 50L);
        set(owner, "downEvent", down); set(owner, "upEvent", up); set(owner, "pointerEvent", pointers);
        set(owner, "passedMinimumVelocitySlop", true); set(owner, "hasInjectEvent", true);
        set(owner, "needInject", true); set(owner, "gestureState", OplusInputInterceptHelper$State.SWIPE_FAIL);
        set(owner, "handler", handler); set(owner, "timeoutRunnable", timeout);
        set(owner, "velocityTracker", velocity); set(owner, "listener", listener);
        set(owner, "mIsCUICase", cui);
        // Actual game-mode values from production adjustThreshold. A later
        // ordinary session must not retain these after cleanup.
        set(owner, "mSwipeUpTimeoutMs", 100L); set(owner, "mSwipeUpNoMoveTimeoutMs", 150L);
        set(owner, "mVelocityThreshold", 500);
        String id = timerState + "/cui=" + cui;
        type.getMethod("resetState").invoke(owner);
        check(get(owner,"downEvent")==null && get(owner,"upEvent")==null && pointers.isEmpty(), id+" buffered motion released");
        check(down.recycles==1 && up.recycles==1 && pointer.recycles==1, id+" recycle exactly once");
        check(get(owner,"firstMoveTime").equals(-1L), id+" movement timestamp reset");
        check(get(owner,"passedMinimumVelocitySlop").equals(false) && get(owner,"hasInjectEvent").equals(false)
                && get(owner,"needInject").equals(false), id+" injection flags reset");
        check(get(owner,"gestureState")==OplusInputInterceptHelper$State.SWIPE_DETECTING, id+" state reset");
        check(get(owner,"handler")==null, id+" old handler released");
        check(get(owner,"listener")==null, id+" old callback owner released");
        check(get(owner,"velocityTracker")==null && !velocity.recycled, id+" borrowed tracker released without recycling owner resource");
        check(get(owner,"mSwipeUpTimeoutMs").equals(cui?800L:400L)
                && get(owner,"mSwipeUpNoMoveTimeoutMs").equals(cui?800L:600L)
                && get(owner,"mVelocityThreshold").equals(200), id+" ordinary thresholds restored");
        check(handler==null || handler.removed==(timerState.equals("queued")?1:0), id+" only queued callback removed");
        type.getMethod("resetState").invoke(owner);
        check(down.recycles==1 && up.recycles==1 && pointer.recycles==1, id+" repeated cleanup idempotent");
        check(get(owner,"handler")==null && get(owner,"listener")==null && get(owner,"velocityTracker")==null,
                id+" repeated cleanup leaves no stale owner");
    }
    public static void main(String[] args) throws Exception {
        type = Class.forName("com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper");
        for (String timer : new String[]{"queued", "executed", "cancelled", "never-queued", "no-handler"})
            for (boolean cui : new boolean[]{false,true}) fixture(timer,cui);
        System.out.println("CHECKS="+checks+" FAILURES="+failures);
        if (failures!=0) System.exit(1);
    }
}
