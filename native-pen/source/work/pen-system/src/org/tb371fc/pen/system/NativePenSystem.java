package org.tb371fc.pen.system;
import android.content.*;
import android.os.*;
import android.provider.Settings;
import android.util.Log;
import android.view.*;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

/** Native system_server integration. Observes real input and CTN730; never pilfers input. */
public final class NativePenSystem {
 static final String TAG="TB371FCPenSystem",HARDWARE="org.tb371fc.pen.CTN730_STATE",REQUEST="org.tb371fc.pen.REQUEST_CTN730_STATE";
 static final String CTN="/sys/class/misc/ctn730/",DEVPATH="/devices/virtual/misc/ctn730",PRIV="android.permission.BLUETOOTH_PRIVILEGED";
 static Context context;static Handler handler;static Object monitor,receiver;static UEventObserver observer;
 static boolean started;static String lastMac="";static int lastButtons,lastDevice=-1;static PenGesture gesture;
 static boolean board(){try{return "spinel".equals(Class.forName("android.os.SystemProperties").getMethod("get",String.class).invoke(null,"ro.product.board"));}catch(Throwable e){return false;}}
 public static void start(Object owner){
  if(started||!board())return;
  try{Context c=null;for(Class<?> k=owner.getClass();k!=null&&c==null;k=k.getSuperclass())try{Field f=k.getDeclaredField("mContext");f.setAccessible(true);c=(Context)f.get(owner);}catch(NoSuchFieldException ignored){}
   if(c==null)return;context=c;handler=new Handler(Looper.getMainLooper());started=true;
   mark("tb371fc_pen_system_bridge_ready",0);mark("tb371fc_pen_input_bridge_ready",0);mark("tb371fc_pen_ctn_bridge_ready",0);
   gesture=new PenGesture(new PenGesture.Loop(){public long now(){return SystemClock.uptimeMillis();}public void post(Runnable r,long delay){handler.postDelayed(r,delay);}public void cancel(Runnable r){handler.removeCallbacks(r);}},new PenGesture.Sink(){public void click(boolean twice){dispatchClick(twice);}public void hold(String state){send(new Intent("com.oplus.ipemanager.action.STYLUS_BUTTON_STATE_CHANGED").setPackage("com.oplus.healthservice").putExtra("stylus_button_status",state),null);}});
   IntentFilter lifecycle=new IntentFilter(Intent.ACTION_SCREEN_OFF);lifecycle.addAction("android.intent.action.USER_SWITCHED");lifecycle.addAction(Intent.ACTION_SHUTDOWN);
   context.registerReceiver(new BroadcastReceiver(){public void onReceive(Context c,Intent i){reset();}},lifecycle,Context.RECEIVER_EXPORTED);
   context.registerReceiver(new BroadcastReceiver(){public void onReceive(Context c,Intent i){startCoreAfterUnlock();}},new IntentFilter("android.intent.action.USER_UNLOCKED"),Context.RECEIVER_EXPORTED);
   context.registerReceiver(new BroadcastReceiver(){public void onReceive(Context c,Intent i){if(REQUEST.equals(i.getAction()))snapshot();}},new IntentFilter(REQUEST),PRIV,handler,Context.RECEIVER_EXPORTED);
   observer=new UEventObserver(){public void onUEvent(UEvent e){if(!DEVPATH.equals(e.get("DEVPATH","")))return;
     String mac=e.get("MAC","");String charging=e.get("CHARGING_STATE","Unknown");int attach=number(e.get("ATTACHED",""),-1),level=number(e.get("LEVEL",""),-1);
     handler.post(()->publishHardware(mac,attach,charging,level));}};
   observer.startObserving("DEVPATH="+DEVPATH);mark("tb371fc_pen_ctn_bridge_ready",1);snapshot();registerMonitor();mark("tb371fc_pen_system_bridge_ready",1);
   Log.i(TAG,"native input and CTN730 observers started");
  }catch(Throwable e){Log.e(TAG,"native pen observer startup failed",e);}
 }
 static void mark(String key,int value){try{Settings.Global.putInt(context.getContentResolver(),key,value);}catch(Throwable e){Log.w(TAG,"diagnostic state unavailable",e);}}
 static void startCoreAfterUnlock(){try{
  Intent i=new Intent().setClassName("com.oplus.ipemanager","com.oplus.ipemanager.btadsorb.CoreService");
  Class<?> user=Class.forName("android.os.UserHandle");Object current=user.getField("CURRENT").get(null);
  Context.class.getMethod("startServiceAsUser",Intent.class,user).invoke(context,i,current);
 }catch(Throwable e){Log.w(TAG,"stock pen service unlock startup unavailable",e);}}
 static int number(String s,int fallback){try{return Integer.parseInt(s.trim());}catch(Throwable e){return fallback;}}
 static boolean mac(String a){return a!=null&&a.matches("(?i)[0-9a-f]{2}(:[0-9a-f]{2}){5}")&&!a.equalsIgnoreCase("00:00:00:00:00:00")&&!a.equalsIgnoreCase("02:00:00:00:00:00");}
 static String cached(String name)throws IOException{try(BufferedReader r=new BufferedReader(new FileReader(CTN+name))){String s=r.readLine();return s==null?"":s.trim();}}
 static void snapshot(){try{int attached=number(cached("attached"),-1);String a=cached("mac"),charging=cached("charge_state");int level=number(cached("level"),-1);publishHardware(a,attached,charging,level);}catch(Throwable e){Log.w(TAG,"cached CTN730 state unavailable",e);}}
 static void publishHardware(String address,int attached,String charging,int level){
  if(attached!=0&&attached!=1)return;boolean current=mac(address);if(current)lastMac=address;
  Intent i=new Intent(HARDWARE).setPackage("com.oplus.ipemanager").putExtra("attached",attached).putExtra("charging",charging).putExtra("mac_is_current",current);
  if(current)i.putExtra("mac",address);else if(attached==0&&mac(lastMac))i.putExtra("mac",lastMac);
  if(current&&attached==1&&level>=0&&level<=100)i.putExtra("level",level);
  send(i,PRIV);
 }
 static boolean pen(InputDevice d){if(d==null||d.getName()==null)return false;String s=d.getName().toLowerCase(Locale.ROOT).trim();
  return s.equals("nvtcapacitivepen")||s.equals("lenovo precision pen 3")||s.equals("lenovo precision pen3")||s.startsWith("lenovo precision pen 3 consumer")||s.startsWith("lenovo precision pen3 consumer")||s.equals("小新触控笔二代")||s.equals("小新触控笔(第二代)")||s.equals("小新触控笔（第二代）")||s.equals("xiaoxin stylus 2");}
 public static boolean key(Object owner,KeyEvent e){
  if(!started||e==null||!pen(e.getDevice()))return false;
  int code=e.getKeyCode(),scan=e.getScanCode();boolean primary=code==KeyEvent.KEYCODE_STYLUS_BUTTON_PRIMARY||scan==331||code==KeyEvent.KEYCODE_F1;
  boolean secondary=code==KeyEvent.KEYCODE_STYLUS_BUTTON_SECONDARY||scan==332||code==KeyEvent.KEYCODE_F2;
  if(!primary&&!secondary)return false;
  if(e.getRepeatCount()>0)return true;
  final int action=e.getAction();
  handler.post(()->{if(action==KeyEvent.ACTION_DOWN){if(primary)gesture.press();}else if(action==KeyEvent.ACTION_UP){if(primary)gesture.release();else gesture.secondary();}});
  return true;
 }
 static void reset(){if(gesture!=null)gesture.reset();lastButtons=0;lastDevice=-1;}
 static boolean motion(MotionEvent e){
  if(!pen(e.getDevice()))return false;boolean stylus=false;
  for(int n=0;n<e.getPointerCount();n++)if(e.getToolType(n)==MotionEvent.TOOL_TYPE_STYLUS||e.getToolType(n)==MotionEvent.TOOL_TYPE_ERASER)stylus=true;
  if(!stylus)return false;if(e.getActionMasked()==MotionEvent.ACTION_CANCEL){reset();return false;}
  if(lastDevice!=e.getDeviceId()){reset();lastDevice=e.getDeviceId();}
  int buttons=e.getButtonState()&(MotionEvent.BUTTON_STYLUS_PRIMARY|MotionEvent.BUTTON_STYLUS_SECONDARY),changed=buttons^lastButtons;
  if((changed&MotionEvent.BUTTON_STYLUS_PRIMARY)!=0){if((buttons&MotionEvent.BUTTON_STYLUS_PRIMARY)!=0)gesture.press();else gesture.release();}
  if((changed&MotionEvent.BUTTON_STYLUS_SECONDARY)!=0&&(buttons&MotionEvent.BUTTON_STYLUS_SECONDARY)==0)gesture.secondary();
  lastButtons=buttons;return false;
 }
 static void registerMonitor(){try{
  Object input=context.getSystemService(Context.INPUT_SERVICE);monitor=input.getClass().getMethod("monitorGestureInput",String.class,int.class).invoke(input,"TB371FCNativePen",0);
  Object channel=monitor.getClass().getMethod("getInputChannel").invoke(monitor);
  Class<?> listener=Class.forName("android.view.BatchedInputEventReceiver$SimpleBatchedInputEventReceiver$InputEventListener");
  Object callback=Proxy.newProxyInstance(listener.getClassLoader(),new Class<?>[]{listener},(proxy,method,args)->{
   if(method.getName().equals("onInputEvent")&&args!=null&&args.length>0){if(args[0] instanceof MotionEvent)motion((MotionEvent)args[0]);return false;}
   if(method.getName().equals("hashCode"))return System.identityHashCode(proxy);if(method.getName().equals("equals"))return args!=null&&args.length==1&&proxy==args[0];if(method.getName().equals("toString"))return "TB371FCNativePenListener";return null;
  });
  Class<?> simple=Class.forName("android.view.BatchedInputEventReceiver$SimpleBatchedInputEventReceiver");
  receiver=simple.getConstructor(Class.forName("android.view.InputChannel"),Looper.class,Choreographer.class,listener).newInstance(channel,Looper.getMainLooper(),Choreographer.getInstance(),callback);
  mark("tb371fc_pen_input_bridge_ready",1);
 }catch(Throwable e){Log.w(TAG,"input observer unavailable; no touch events consumed",e);}}
 static void dispatchClick(boolean twice){try{int action=Settings.Global.getInt(context.getContentResolver(),twice?"ipe_pencil_double_click":"ipe_pencil_single_click",twice?1:4);if(action==0)return;
  String name=twice?"com.oplus.ipemanager.action.PENCIL_DOUBLE_CLICK":"com.oplus.ipemanager.action.PENCIL_SINGLE_CLICK";
  for(String pkg:action==4?new String[]{"com.oplus.healthservice"}:new String[]{"com.coloros.note","com.oplus.screenshot"})send(new Intent(name).setPackage(pkg).putExtra("action",action).addFlags(0x01000000),action==4?"com.oplus.ipemanager.permission.receiver.DOUBLE_CLICK":null);
 }catch(Throwable e){Log.w(TAG,"native pen action unavailable",e);}}
 static void send(Intent intent,String permission){if(context==null)return;try{
  Class<?> user=Class.forName("android.os.UserHandle");Object current=user.getField("CURRENT").get(null);
  Context.class.getMethod("sendBroadcastAsUser",Intent.class,user,String.class).invoke(context,intent,current,permission);
 }catch(Throwable e){Log.w(TAG,"native pen broadcast unavailable",e);}}
}
