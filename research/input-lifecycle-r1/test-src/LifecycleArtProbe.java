import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.view.MotionEvent;
import android.view.VelocityTracker;
import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;

/** Isolated process: real ART/Handler/MotionEvent, no input injection or UI calls. */
public final class LifecycleArtProbe {
    static Class<?> type;
    static int checks, failures;
    static Object get(Object owner,String name)throws Exception {
        Field f=type.getDeclaredField(name);f.setAccessible(true);return f.get(owner);
    }
    static void set(Object owner,String name,Object value)throws Exception {
        Field f=type.getDeclaredField(name);f.setAccessible(true);f.set(owner,value);
    }
    static void check(boolean good,String name) {
        checks++;if(!good){failures++;System.out.println("FAIL "+name);}
    }
    @SuppressWarnings({"unchecked","rawtypes"})
    static void fixture(String mode,Handler handler,Runnable timeout,boolean cui)throws Exception {
        Object owner=type.getConstructor().newInstance();
        long now=SystemClock.uptimeMillis();
        MotionEvent down=MotionEvent.obtain(now,now,0,1,1,0);
        MotionEvent up=MotionEvent.obtain(now,now,1,1,1,0);
        MotionEvent pointer=MotionEvent.obtain(now,now,5,1,1,0);
        var pointers=new ArrayList<MotionEvent>();pointers.add(pointer);
        VelocityTracker tracker=VelocityTracker.obtain();
        Class<?> listenerType=Class.forName("com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper$IGestureStateChangeListener");
        Object listener=Proxy.newProxyInstance(listenerType.getClassLoader(),new Class<?>[]{listenerType},(p,m,a)->null);
        Class<? extends Enum> states=(Class<? extends Enum>)Class.forName("com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper$State");
        set(owner,"downEvent",down);set(owner,"upEvent",up);set(owner,"pointerEvent",pointers);
        set(owner,"firstMoveTime",50L);set(owner,"passedMinimumVelocitySlop",true);
        set(owner,"hasInjectEvent",true);set(owner,"needInject",true);
        set(owner,"gestureState",Enum.valueOf(states,"SWIPE_FAIL"));set(owner,"handler",handler);
        set(owner,"timeoutRunnable",timeout);set(owner,"velocityTracker",tracker);set(owner,"listener",listener);
        set(owner,"mIsCUICase",cui);set(owner,"mSwipeUpTimeoutMs",100L);
        set(owner,"mSwipeUpNoMoveTimeoutMs",150L);set(owner,"mVelocityThreshold",500);
        String id=mode+"/cui="+cui;
        check(handler==null||handler.hasCallbacks(timeout)==mode.equals("queued"),id+" real queue precondition");
        type.getMethod("resetState").invoke(owner);
        check(get(owner,"downEvent")==null&&get(owner,"upEvent")==null&&pointers.isEmpty(),id+" buffered motion released");
        check(get(owner,"firstMoveTime").equals(-1L)&&get(owner,"passedMinimumVelocitySlop").equals(false)
            &&get(owner,"hasInjectEvent").equals(false)&&get(owner,"needInject").equals(false),id+" movement and flags reset");
        check(get(owner,"handler")==null,id+" handler released");
        check(get(owner,"listener")==null,id+" listener released");
        check(get(owner,"velocityTracker")==null,id+" tracker reference released");
        check(get(owner,"gestureState")==Enum.valueOf(states,"SWIPE_DETECTING"),id+" state reset");
        check(get(owner,"mSwipeUpTimeoutMs").equals(cui?800L:400L)
            &&get(owner,"mSwipeUpNoMoveTimeoutMs").equals(cui?800L:600L)
            &&get(owner,"mVelocityThreshold").equals(200),id+" thresholds restored");
        type.getMethod("resetState").invoke(owner);
        check(get(owner,"handler")==null&&get(owner,"listener")==null&&get(owner,"velocityTracker")==null,id+" repeat cleanup");
        check(handler==null||!handler.hasCallbacks(timeout),id+" no queued timeout remains");
        tracker.recycle();
    }
    public static void main(String[] args) {
        try { run(); } catch(Throwable error) {error.printStackTrace(System.out);System.exit(2);}
    }
    static void run()throws Exception {
        type=Class.forName("com.oplus.quickstep.gesture.helper.OplusInputInterceptHelper");
        HandlerThread thread=new HandlerThread("tb371fc-cleanup-contract");thread.start();
        Handler handler=new Handler(thread.getLooper());
        try {
            for(boolean cui:new boolean[]{false,true}) {
                Runnable queued=()->{};handler.postDelayed(queued,60000);
                fixture("queued",handler,queued,cui);
                Runnable cancelled=()->{};handler.postDelayed(cancelled,60000);handler.removeCallbacks(cancelled);
                fixture("cancelled",handler,cancelled,cui);
                fixture("no-handler",null,()->{},cui);
                CountDownLatch finished=new CountDownLatch(1);Throwable[] error=new Throwable[1];Runnable[] executing=new Runnable[1];
                executing[0]=()->{try{fixture("executed",handler,executing[0],cui);}catch(Throwable e){error[0]=e;}finally{finished.countDown();}};
                handler.post(executing[0]);
                if(!finished.await(10,TimeUnit.SECONDS))throw new AssertionError("Isolated queue timeout");
                if(error[0]!=null)throw new AssertionError(error[0]);
            }
        } finally {thread.quitSafely();thread.join(2000);}
        System.out.println("ART_CHECKS="+checks+" FAILURES="+failures);
        if(failures!=0)System.exit(1);
    }
}
