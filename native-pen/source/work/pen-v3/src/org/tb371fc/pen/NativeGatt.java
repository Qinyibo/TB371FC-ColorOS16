package org.tb371fc.pen;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.util.Log;
import java.lang.reflect.Field;
import java.util.IdentityHashMap;
import java.util.UUID;
import java.util.ArrayDeque;

/** In-process IPeManager compatibility branch. No Xposed, su, polling or private pen commands. */
public final class NativeGatt {
    private static final String TAG="TB371FCPen";
    private static final UUID HID=UUID.fromString("00001812-0000-1000-8000-00805f9b34fb");
    private static final UUID BATTERY=UUID.fromString("0000180f-0000-1000-8000-00805f9b34fb");
    private static final UUID LEVEL=UUID.fromString("00002a19-0000-1000-8000-00805f9b34fb");
    private static final UUID CCC=UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
    private static final UUID INFO=UUID.fromString("0000180a-0000-1000-8000-00805f9b34fb");
    private static UUID id(String shortId) { return UUID.fromString("0000"+shortId+"-0000-1000-8000-00805f9b34fb"); }
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final IdentityHashMap<Object,Session> SESSIONS=new IdentityHashMap<>();

    private NativeGatt() {}
    public static boolean official(String name) { return PenSession.officialName(name); }
    public static boolean connected(Object owner) {
        // Stock callback already starts discovery. Do not publish readiness before services().
        return target(active(owner));
    }
    public static boolean descriptor(Object owner,int status) {
        if(!target(active(owner))) return false;
        MAIN.post(()->{Session s=SESSIONS.get(owner);if(s!=null && s.pending!=null && s.pending.descriptor!=null)complete(s,s.pending,status);});
        return true;
    }
    private static Context context(Object owner) throws Exception {
        Object c=owner.getClass().getMethod("p").invoke(owner);
        if(!(c instanceof Context)) throw new IllegalStateException("IPe context type changed");
        return (Context)c;
    }
    static BluetoothGatt active(Object owner) {
        try { return (BluetoothGatt)owner.getClass().getMethod("r").invoke(owner); }
        catch(Throwable e) { Log.w(TAG,"current GATT unavailable",e); return null; }
    }
    private static boolean target(BluetoothGatt gatt) {
        if(gatt==null) return false;
        try {
            BluetoothDevice d=gatt.getDevice();
            return NativePenLifecycle.identity(d);
        } catch(Throwable e) { Log.w(TAG,"pen identity unavailable",e); return false; }
    }

    private static Object manager(Object callback) throws Exception {return callback.getClass().getField("a").get(callback);}
    public static void hardwareSample(String address,int level,int charging){
        MAIN.post(()->{for(Session s:SESSIONS.values()){
            if(active(s.owner)!=s.gatt||!s.gatt.getDevice().getAddress().equalsIgnoreCase(address)||!s.policy.snapshot().connected)continue;
            if(level>=0)s.policy.battery(s.generation,new byte[]{(byte)level});
            if(charging>=0)s.publishCharging(charging);
        }});
    }
    public static boolean readValue(Object callback,BluetoothGatt gatt,BluetoothGattCharacteristic c,byte[] value,int status) {
        if(!target(gatt))return false;
        try {Object o=manager(callback); if(active(o)==gatt)onValue(o,gatt,c,value==null?null:value.clone(),status,true);}
        catch(Throwable e){Log.w(TAG,"value callback rejected",e);}return true;
    }
    public static boolean readLegacy(Object callback,BluetoothGatt gatt,BluetoothGattCharacteristic c,int status) {
        return readValue(callback,gatt,c,c==null?null:c.getValue(),status);
    }
    public static boolean changed(Object callback,BluetoothGatt gatt,BluetoothGattCharacteristic c) {
        return changedValue(callback,gatt,c,c==null?null:c.getValue());
    }
    public static boolean changedValue(Object callback,BluetoothGatt gatt,BluetoothGattCharacteristic c,byte[] value) {
        if(!target(gatt))return false;
        try {Object o=manager(callback);if(active(o)==gatt)onValue(o,gatt,c,value==null?null:value.clone(),BluetoothGatt.GATT_SUCCESS,false);}
        catch(Throwable e){Log.w(TAG,"notification rejected",e);}return true;
    }
    public static boolean serviceResult(Object callback,BluetoothGatt gatt,int status) {
        if(!target(gatt))return false;
        try {Object o=manager(callback);if(active(o)==gatt && status==BluetoothGatt.GATT_SUCCESS)services(o,gatt);
            else Log.w(TAG,"failed or stale service discovery; no connected state published");}
        catch(Throwable e){Log.w(TAG,"service callback rejected",e);}return true;
    }
    public static boolean descriptorValue(Object callback,BluetoothGatt gatt,BluetoothGattDescriptor descriptor,int status) {
        if(!target(gatt))return false;
        try {Object o=manager(callback);MAIN.post(()->{Session s=SESSIONS.get(o);
            if(s!=null&&s.gatt==gatt&&active(o)==gatt&&s.pending!=null&&s.pending.descriptor==descriptor)complete(s,s.pending,status);});}
        catch(Throwable e){Log.w(TAG,"descriptor callback rejected",e);}return true;
    }
    public static void descriptorDispatch(Object callback,BluetoothGatt gatt,BluetoothGattDescriptor descriptor,int status) {
        if(descriptorValue(callback,gatt,descriptor,status))return;
        try{Object o=manager(callback);o.getClass().getMethod("h",int.class).invoke(o,status);}
        catch(Throwable e){Log.w(TAG,"stock descriptor callback",e);}
    }

    public static boolean services(Object owner,BluetoothGatt gatt) {
        if(!target(gatt)) return false;
        // Do not let the OEM branch issue OPPO-specific instructions to a Lenovo pen.
        MAIN.post(()->prepare(owner,gatt));
        return true;
    }
    private static void prepare(Object owner,BluetoothGatt gatt) {
        try {
            if(active(owner)!=gatt) { Log.w(TAG,"ignored stale services callback"); return; }
            Session previous=SESSIONS.get(owner);
            if(previous!=null && previous.gatt==gatt && previous.policy.snapshot().connected) return;
            remove(owner);
            Session s=new Session(owner,gatt,context(owner)); SESSIONS.put(owner,s);
            BluetoothGattService batteryService=gatt.getService(BATTERY);
            BluetoothGattCharacteristic batteryLevel=batteryService==null?null:batteryService.getCharacteristic(LEVEL);
            boolean realBattery=batteryLevel!=null&&(batteryLevel.getProperties()&(BluetoothGattCharacteristic.PROPERTY_READ|BluetoothGattCharacteristic.PROPERTY_NOTIFY|BluetoothGattCharacteristic.PROPERTY_INDICATE))!=0;
            boolean supported=realBattery&&(gatt.getService(HID)!=null||NativeHardwareState.known(gatt.getDevice().getAddress()));
            if(!s.policy.ready(s.generation,gatt.getDevice().getAddress(),true,supported)) {
                Log.w(TAG,"pen services need protocol verification; no connected state published");
                return;
            }
            BluetoothGattService battery=gatt.getService(BATTERY);
            BluetoothGattCharacteristic level=battery==null?null:battery.getCharacteristic(LEVEL);
            queue(s,level,true);
            queue(s,battery==null?null:battery.getCharacteristic(id("2a1a")),true);
            BluetoothGattService info=gatt.getService(INFO);
            if(info!=null)for(String key:new String[]{"2a26","2a27","2a28","2a25"})queue(s,info.getCharacteristic(id(key)),false);
            drain(s);
            if(gatt.getService(HID)!=null)NativePenLifecycle.requestHid(owner,gatt.getDevice());
            NativeHardwareState.applyCached();
        } catch(Throwable e) { remove(owner); Log.e(TAG,"native pen session rejected",e); }
    }
    public static boolean characteristic(Object owner,BluetoothGattCharacteristic c,int status) {
        BluetoothGatt gatt=active(owner);
        if(!target(gatt)) return false;
        // Capture immutable bytes before returning to Bluetooth's callback thread.
        byte[] value=c==null || c.getValue()==null?null:c.getValue().clone();
        onValue(owner,gatt,c,value,status,true);
        return true;
    }
    private static void onValue(Object owner,BluetoothGatt gatt,BluetoothGattCharacteristic c,byte[] value,int status,boolean read) {
        UUID uuid=c==null?null:c.getUuid();
        MAIN.post(()->{
            Session s=SESSIONS.get(owner);
            if(s==null || s.gatt!=gatt || active(owner)!=gatt) return;
            if(c==null||c.getService()==null||gatt.getService(c.getService().getUuid())!=c.getService())return;
            if(LEVEL.equals(uuid)&&BATTERY.equals(c.getService().getUuid())) {
                if(status==BluetoothGatt.GATT_SUCCESS) s.policy.battery(s.generation,value);
            }
            else if(id("2a1a").equals(uuid)&&BATTERY.equals(c.getService().getUuid())&&status==BluetoothGatt.GATT_SUCCESS){
                int charging=PenGattValues.lenovoCharge(value);
                if(charging>=0)s.publishCharging(charging);
            }
            else if(INFO.equals(c.getService().getUuid())&&status==BluetoothGatt.GATT_SUCCESS){
                String text=PenGattValues.text(value);
                if(text!=null)try {
                    if(id("2a26").equals(uuid)){preference(s.context,"pencil_sp_fw_version",text);s.firmwareSeen=true;}
                    else if(id("2a28").equals(uuid)&&!s.firmwareSeen)preference(s.context,"pencil_sp_fw_version",text);
                    else if(id("2a27").equals(uuid))preference(s.context,"pencil_sp_hw_version",text);
                    else if(id("2a25").equals(uuid))preference(s.context,"pencil_sp_serial_num",text);
                }catch(Throwable e){Log.w(TAG,"device information handoff",e);}
            }
            if(read&&s.pending!=null&&s.pending.descriptor==null&&s.pending.characteristic==c)complete(s,s.pending,status);
        });
    }
    public static void disconnected(Object owner) { MAIN.post(()->remove(owner)); }
    public static boolean notification(Object owner,BluetoothGattCharacteristic c) {
        BluetoothGatt gatt=active(owner);if(!target(gatt))return false;
        byte[] value=c==null||c.getValue()==null?null:c.getValue().clone();onValue(owner,gatt,c,value,BluetoothGatt.GATT_SUCCESS,false);return true;
    }
    private static final class Op {
        final BluetoothGattCharacteristic characteristic;final BluetoothGattDescriptor descriptor;final byte[] value;
        Op(BluetoothGattCharacteristic c,BluetoothGattDescriptor d,byte[] v){characteristic=c;descriptor=d;value=v;}
    }
    private static void queue(Session s,BluetoothGattCharacteristic c,boolean subscribe) {
        if(c==null)return;
        if((c.getProperties()&BluetoothGattCharacteristic.PROPERTY_READ)!=0)s.operations.add(new Op(c,null,null));
        if(!subscribe)return;boolean notify=(c.getProperties()&BluetoothGattCharacteristic.PROPERTY_NOTIFY)!=0;
        boolean indicate=(c.getProperties()&BluetoothGattCharacteristic.PROPERTY_INDICATE)!=0;BluetoothGattDescriptor d=c.getDescriptor(CCC);
        if(d!=null&&(notify||indicate))s.operations.add(new Op(c,d,notify?BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE:BluetoothGattDescriptor.ENABLE_INDICATION_VALUE));
    }
    private static void drain(Session s) {
        if(SESSIONS.get(s.owner)!=s||active(s.owner)!=s.gatt||s.pending!=null)return;
        while(!s.operations.isEmpty()){
            Op op=s.operations.remove();s.pending=op;boolean started=false;
            try{if(op.descriptor==null)started=s.gatt.readCharacteristic(op.characteristic);
                else if(s.gatt.setCharacteristicNotification(op.characteristic,true)){op.descriptor.setValue(op.value);started=s.gatt.writeDescriptor(op.descriptor);}}
            catch(Throwable e){Log.w(TAG,"GATT operation unavailable",e);}
            if(started){s.timeout=()->{if(SESSIONS.get(s.owner)==s&&s.pending==op){Log.w(TAG,"bounded GATT operation timed out");complete(s,op,-1);}};MAIN.postDelayed(s.timeout,5000);return;}
            s.pending=null;
        }
    }
    private static void complete(Session s,Op op,int status) {
        if(s.pending!=op)return;if(s.timeout!=null)MAIN.removeCallbacks(s.timeout);s.timeout=null;s.pending=null;
        if(status!=BluetoothGatt.GATT_SUCCESS)Log.w(TAG,"GATT metadata operation failed: "+status);
        drain(s);
    }
    private static void remove(Object owner) {
        Session s=SESSIONS.remove(owner);
        if(s!=null){if(s.timeout!=null)MAIN.removeCallbacks(s.timeout);s.operations.clear();s.pending=null;s.policy.disconnect();}
        // GATT belongs to the stock manager. Its teardown alone closes it.
    }
    private static void callInt(Object owner,String name,int value) throws Exception {
        owner.getClass().getMethod(name,int.class).invoke(owner,value);
    }
    private static void stockInt(int value,String key) throws Exception {
        Class.forName("d2.b").getMethod("a",int.class,String.class).invoke(null,value,key);
    }
    private static void stockString(String key,String value) throws Exception {
        Class.forName("d2.b").getMethod("b",String.class,String.class).invoke(null,key,value);
    }
    private static void preference(Context c,String key,String value) throws Exception {
        Class.forName("x1.b").getMethod("g",Context.class,String.class,String.class).invoke(null,c,key,value);
    }
    private static void batteryCallback(Object owner,String field,int level) throws Exception {
        Object callback=owner.getClass().getField(field).get(owner);
        if(callback!=null) callback.getClass().getMethod("onBatteryLevel",int.class).invoke(callback,level);
    }
    private static final class Session implements PenSession.Sink {
        final Object owner;
        final BluetoothGatt gatt;
        final Context context;
        final PenSession policy;
        final long generation;
        boolean published;
        boolean claimed,firmwareSeen;
        int charging=-1;
        final ArrayDeque<Op> operations=new ArrayDeque<>();Op pending;Runnable timeout;
        Session(Object o,BluetoothGatt g,Context c) {
            owner=o;gatt=g;context=c;policy=new PenSession(this);
            BluetoothDevice d=g.getDevice(); generation=policy.beginHardware(d.getAddress(),d.getName(),true,NativeHardwareState.known(d.getAddress()));
        }
        void publishCharging(int value){if(value==charging)return;try{
            stockString("ipe_pencil_charging_state",String.valueOf(value));
            Class.forName("x1.b").getMethod("f",Context.class,int.class,String.class).invoke(null,context,value,"pencil_sp_charging_state");charging=value;
            for(String field:new String[]{"J0","M0","y0"})try{Object cb=owner.getClass().getField(field).get(owner);if(cb!=null)cb.getClass().getMethod(field.equals("y0")?"notifyChargingState":"onChargingState",boolean.class).invoke(cb,value==1);}catch(Throwable e){Log.w(TAG,"charging callback detached");}
            PenSession.Snapshot state=policy.snapshot();NativeDeviceCard.publish(context,gatt.getDevice(),state.connected,state.battery,charging);
        }catch(Throwable e){Log.w(TAG,"charging handoff",e);}}
        @Override public void stateChanged(PenSession.Snapshot state) {
            try {
                if(state.connected) {
                    if(!published) {
                        stockString("ipe_pencil_mac_addr",state.address);
                        preference(context,"sp_key_pencil_device_name",state.name);
                        owner.getClass().getField("M").set(owner,state.name);
                        // K/L are actual current-package battery caches, not connection state.
                        owner.getClass().getField("K").setInt(owner,-1);
                        owner.getClass().getField("L").setInt(owner,-1);
                        claimed=true;
                        stockInt(1,"settings_enable_oppo_pencil");
                        stockInt(2,"ipe_pencil_connect_state");
                        if(Settings.Global.getInt(context.getContentResolver(),"settings_enable_oppo_pencil",0)!=1)
                            throw new IllegalStateException("native settings handoff not acknowledged");
                        // r0 is the verified UI/SDK connection callback, not a hardware command.
                        callInt(owner,"r0",2); published=true;
                        NativeDeviceCard.publish(context,gatt.getDevice(),true,state.battery,charging);
                    }
                    if(state.battery>=0) {
                        owner.getClass().getField("K").setInt(owner,state.battery);
                        owner.getClass().getField("L").setInt(owner,state.battery);
                        stockInt(state.battery,"ipe_pencil_battery_level");
                        preference(context,"pencil_sp_battery_level",String.valueOf(state.battery));
                        for(String field:new String[]{"J0","M0"}) {
                            try { batteryCallback(owner,field,state.battery); }
                            catch(Throwable e) { Log.w(TAG,"battery callback detached: "+field,e); }
                        }
                        NativeDeviceCard.publish(context,gatt.getDevice(),true,state.battery,charging);
                    }
                } else if(claimed) {
                    clearOwnedConnection();
                    callInt(owner,"r0",0); published=false;claimed=false;
                    charging=-1;NativeDeviceCard.publish(context,gatt.getDevice(),false,-1,-1);
                }
            } catch(Throwable e) {
                Log.e(TAG,"native UI handoff failed",e);
                try { if(claimed) clearOwnedConnection(); } catch(Throwable cleanup) { Log.e(TAG,"handoff cleanup failed",cleanup); }
                published=false;claimed=false;
            }
        }
        private void clearOwnedConnection() throws Exception {
            if(!gatt.getDevice().getAddress().equalsIgnoreCase(Settings.Global.getString(context.getContentResolver(),"ipe_pencil_mac_addr"))) return;
            if(Settings.Global.getInt(context.getContentResolver(),"settings_enable_oppo_pencil",-1)==1)
                stockInt(0,"settings_enable_oppo_pencil");
            if(Settings.Global.getInt(context.getContentResolver(),"ipe_pencil_connect_state",-1)==2)
                stockInt(0,"ipe_pencil_connect_state");
        }
    }
}
