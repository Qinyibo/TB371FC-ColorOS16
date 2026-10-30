package org.tb371fc.pen;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.util.Log;
import java.security.MessageDigest;
import java.util.*;

/** Real GATT session -> the existing MyDevices SDK, with the real Lenovo name. */
public final class NativeDeviceCard {
  static Object enumeration(String name,String value)throws Exception{return Class.forName("com.oplus.mydevices.sdk.device."+name).getField(value).get(null);}
  static Object call(Object object,String name,Class<?> type,Object value)throws Exception{return object.getClass().getMethod(name,type).invoke(object,value);}
  public static void publish(Context context,BluetoothDevice device,boolean connected,int battery,int charging){
    if(!NativePenLifecycle.identity(device))return;
    try{
      String address=device.getAddress(),name=device.getName();if(name==null||name.trim().isEmpty())name="手写笔";
      byte[] digest=MessageDigest.getInstance("SHA-256").digest(address.getBytes("UTF-8"));StringBuilder id=new StringBuilder("tb371fc.pen.");
      for(byte b:digest)id.append(String.format(Locale.ROOT,"%02x",b&255));
      Object builder=Class.forName("com.oplus.mydevices.sdk.device.DeviceInfo$Builder").getConstructor().newInstance();
      call(builder,"deviceId",String.class,id.toString());call(builder,"mac",String.class,address);
      call(builder,"modelId",String.class,"tb371fc.lenovo.pen");call(builder,"deviceName",String.class,name);
      Object type=enumeration("DeviceType","PENCIL");call(builder,"deviceType",type.getClass(),type);
      Object state=enumeration("ConnectState",connected?"CONNECTED":"DISCONNECTED");
      Class<?> connection=Class.forName("com.oplus.mydevices.sdk.device.Connection");
      Object link=connection.getConstructor(state.getClass(),long.class,long.class).newInstance(state,connected?System.currentTimeMillis():0L,connected?0L:System.currentTimeMillis());
      call(builder,"connection",connection,link);call(builder,"connectProtocol",int.class,8);
      ArrayList<Object> list=new ArrayList<>();
      // This SDK has no unknown-charging representation. Omit the battery row until both samples are real.
      if(connected&&battery>=0&&charging>=0){Object bt=enumeration("BatteryType","SINGLE");Class<?> bi=Class.forName("com.oplus.mydevices.sdk.device.BatteryInfo");list.add(bi.getConstructor(bt.getClass(),int.class,boolean.class).newInstance(bt,battery,charging==1));}
      call(builder,"batteryInfoList",ArrayList.class,list);
      Object info=builder.getClass().getMethod("build").invoke(builder);
      Class<?> managerClass=Class.forName("com.oplus.mydevices.sdk.DeviceInfoManager");Object manager=managerClass.getField("INSTANCE").get(null);
      managerClass.getMethod("add",info.getClass()).invoke(manager,info);
    }catch(Throwable e){Log.w("TB371FCPen","native device card handoff unavailable",e);}
  }
}
