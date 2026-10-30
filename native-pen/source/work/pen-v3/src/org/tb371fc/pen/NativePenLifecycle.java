package org.tb371fc.pen;
import android.app.Service;
import android.bluetooth.*;
import android.content.*;
import android.os.*;
import android.util.Log;
import java.util.*;

/** Runs inside the stock CoreService. Protected Bluetooth events and bounded requests only. */
public final class NativePenLifecycle {
  private static final String TAG="TB371FCPen";
  private static final String CONNECT="com.oplus.ipemanager.action.CONNECT_PENCIL";
  private static final String DISCONNECT="com.oplus.ipemanager.action.DISCONNECT_PENCIL";
  private static final IdentityHashMap<Object,NativePenLifecycle> OWNERS=new IdentityHashMap<>();
  final Service service;final Handler handler=new Handler(Looper.getMainLooper());
  final SharedPreferences prefs;boolean closed;int generation;
  final BroadcastReceiver hardwareReceiver=new BroadcastReceiver(){public void onReceive(Context c,Intent i){if(NativeHardwareState.receive(c,i))schedule();}};
  final BroadcastReceiver receiver=new BroadcastReceiver(){public void onReceive(Context c,Intent i){
    if(i==null)return;
    if(BluetoothAdapter.ACTION_STATE_CHANGED.equals(i.getAction())){
      if(i.getIntExtra(BluetoothAdapter.EXTRA_STATE,BluetoothAdapter.ERROR)==BluetoothAdapter.STATE_ON)schedule();
      else{generation++;handler.removeCallbacksAndMessages(null);}return;
    }
    BluetoothDevice d=i.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
    if(!identity(d))return;
    if(BluetoothDevice.ACTION_BOND_STATE_CHANGED.equals(i.getAction())&&d.getBondState()==BluetoothDevice.BOND_BONDED)schedule();
    else if(BluetoothDevice.ACTION_ACL_CONNECTED.equals(i.getAction()))schedule();
  }};
  NativePenLifecycle(Service s){service=s;prefs=s.getSharedPreferences("tb371fc_native_pen",Context.MODE_PRIVATE);}
  static BluetoothAdapter adapter(Context c){BluetoothManager m=(BluetoothManager)c.getSystemService(Context.BLUETOOTH_SERVICE);return m==null?null:m.getAdapter();}
  static boolean identity(BluetoothDevice d){try{return d!=null&&d.getBondState()==BluetoothDevice.BOND_BONDED&&(PenSession.officialName(d.getName())||NativeHardwareState.known(d.getAddress()))&&PenSession.validAddress(d.getAddress());}catch(Throwable e){return false;}}
  public static void created(Object owner){
    if(!(owner instanceof Service)||OWNERS.containsKey(owner))return;
    try{NativePenLifecycle p=new NativePenLifecycle((Service)owner);NativeHardwareState.initialize(p.service);
      IntentFilter f=new IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED);f.addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED);f.addAction(BluetoothDevice.ACTION_ACL_CONNECTED);
      p.service.registerReceiver(p.receiver,f,Context.RECEIVER_EXPORTED);
      p.service.registerReceiver(p.hardwareReceiver,new IntentFilter(NativeHardwareState.ACTION),"android.permission.BLUETOOTH_PRIVILEGED",p.handler,Context.RECEIVER_EXPORTED);
      p.service.sendBroadcast(new Intent("org.tb371fc.pen.REQUEST_CTN730_STATE").setPackage("android"),"android.permission.BLUETOOTH_PRIVILEGED");
      OWNERS.put(owner,p);p.schedule();
      Log.i(TAG,"native lifecycle registered; reconnect requires an existing bonded pen");
    }catch(Throwable e){Log.e(TAG,"lifecycle unavailable",e);}
  }
  public static void destroyed(Object owner){NativePenLifecycle p=OWNERS.remove(owner);if(p==null)return;p.closed=true;p.generation++;p.handler.removeCallbacksAndMessages(null);try{p.service.unregisterReceiver(p.receiver);p.service.unregisterReceiver(p.hardwareReceiver);}catch(Throwable e){Log.w(TAG,"receiver teardown",e);}}
  public static void started(Object owner,Intent intent){
    NativePenLifecycle p=OWNERS.get(owner);if(p==null||intent==null)return;
    String action=intent.getAction();if(!CONNECT.equals(action)&&!DISCONNECT.equals(action))return;
    try{String address=intent.getStringExtra("device_mac_info");BluetoothAdapter a=adapter(p.service);
      if(a==null||!PenSession.validAddress(address))return;BluetoothDevice d=a.getRemoteDevice(address);if(!identity(d))return;
      boolean disconnect=DISCONNECT.equals(action);boolean auto=intent.getBooleanExtra("tb371fc_native_auto_connect",false);
      if(!auto)p.prefs.edit().putBoolean("userDisconnected",disconnect).putString("address",address).apply();
      if(disconnect){p.generation++;p.handler.removeCallbacksAndMessages(null);Object manager=owner.getClass().getField("b").get(owner);BluetoothGatt g=NativeGatt.active(manager);if(g!=null)g.disconnect();}
    }catch(Throwable e){Log.w(TAG,"explicit pen request",e);}
  }
  void schedule(){
    if(closed||prefs.getBoolean("userDisconnected",false))return;
    int g=++generation;handler.removeCallbacksAndMessages(null);
    for(long delay:new long[]{1000,5000,12000})handler.postDelayed(()->attempt(g),delay);
  }
  void attempt(int g){
    if(closed||g!=generation||prefs.getBoolean("userDisconnected",false))return;
    try{BluetoothAdapter a=adapter(service);if(a==null||!a.isEnabled())return;
      Object manager=service.getClass().getField("b").get(service);
      if(NativeGatt.active(manager)!=null)return; // The stock manager owns its existing GATT.
      String remembered=prefs.getString("address","");BluetoothDevice selected=null;int count=0;
      for(BluetoothDevice d:a.getBondedDevices())if(identity(d)){count++;if(d.getAddress().equalsIgnoreCase(remembered)){selected=d;break;}selected=d;}
      if(selected==null||(count>1&&!selected.getAddress().equalsIgnoreCase(remembered)))return;
      Intent i=new Intent(CONNECT).setClassName(service,"com.oplus.ipemanager.btadsorb.CoreService");
      i.putExtra("device_mac_info",selected.getAddress());i.putExtra("tb371fc_native_auto_connect",true);service.startService(i);
      Log.i(TAG,"bounded stock GATT reconnect requested");
    }catch(Throwable e){Log.w(TAG,"bounded reconnect unavailable",e);}
  }
  static void requestHid(Object manager,BluetoothDevice d){
    if(!identity(d))return;
    try{manager.getClass().getMethod("v",BluetoothDevice.class).invoke(manager,d);Log.i(TAG,"stock HID profile requested after verified GATT services");}
    catch(Throwable e){Log.w(TAG,"stock HID profile unavailable",e);}
  }
}
