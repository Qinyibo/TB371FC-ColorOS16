package org.tb371fc.pen;
import android.bluetooth.*;
import android.content.*;
import android.util.Log;

/** Only called by a receiver that requires a privileged sender permission. */
public final class NativeHardwareState {
  public static final String ACTION="org.tb371fc.pen.CTN730_STATE";
  private static String address="";
  private static int level=-1,charging=-1;
  static void initialize(Context c){level=charging=-1;String a=c.getSharedPreferences("tb371fc_native_pen",0).getString("ctn730Address","");if(PenSession.validAddress(a))address=a;}
  static boolean known(String a){return PenSession.validAddress(a)&&address.equalsIgnoreCase(a);}
  static void applyCached(){if(PenSession.validAddress(address))NativeGatt.hardwareSample(address,level,charging);}
  static boolean receive(Context context,Intent intent){
    if(intent==null||!ACTION.equals(intent.getAction()))return false;
    String a=intent.getStringExtra("mac");int attached=intent.getIntExtra("attached",-1);
    if(attached==0){level=charging=-1;return false;}
    if(!PenSession.validAddress(a)||attached!=1||!intent.getBooleanExtra("mac_is_current",false))return false;
    if(!address.equalsIgnoreCase(a))level=charging=-1;
    address=a;context.getSharedPreferences("tb371fc_native_pen",0).edit().putString("ctn730Address",a).apply();
    int sample=intent.getIntExtra("level",-1);if(sample>=0&&sample<=100)level=sample;
    String charge=intent.getStringExtra("charging");charging="Charging".equals(charge)?1:("Full".equals(charge)||"Notcharging".equals(charge))?0:-1;
    NativeGatt.hardwareSample(a,level,charging);
    try{BluetoothAdapter adapter=NativePenLifecycle.adapter(context);if(adapter==null||!adapter.isEnabled())return true;
      BluetoothDevice d=adapter.getRemoteDevice(a);
      if(d.getBondState()==BluetoothDevice.BOND_NONE&&!context.getSharedPreferences("tb371fc_native_pen",0).getBoolean("userDisconnected",false)){d.createBond();Log.i("TB371FCPen","CTN730 physical pen requested real Bluetooth bonding");}
    }catch(Throwable e){Log.w("TB371FCPen","CTN730 bonding request unavailable",e);}return true;
  }
}
