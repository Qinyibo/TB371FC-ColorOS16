import android.content.Context;
import android.hardware.display.DisplayManager;
import android.media.AudioManager;
import android.media.AudioPlaybackConfiguration;
import android.media.AudioDeviceCallback;
import android.media.AudioDeviceInfo;
import android.os.Handler;
import android.os.Looper;
import android.view.Display;
import java.lang.reflect.Method;
import java.util.List;

// Root-only app_process helper. No recorder, microphone, HAL restart or Binder service.
public class R94SpeakerDirection {
    private static int retries=0;
    private static long generationStart=0;
    private static void log(String s){System.out.println("UPTIME="+android.os.SystemClock.elapsedRealtime()+" "+s);}
    private static native boolean stopRequested();
    private static native int apply(int rotation, int swapped);
    private static native int restore();
    private static native int swap();
    private static Handler handler;
    private static AudioManager audio;
    private static DisplayManager display;
    private static Method devicesForStream;
    private static int lastRotation=-1,lastSwap=-1,lastResult=-99;
    private static String lastGate="";
    private static void gate(String value){if(!value.equals(lastGate)){log(value);lastGate=value;}}
    private static void tick() {
        try {
            int devices=((Integer)devicesForStream.invoke(audio, AudioManager.STREAM_MUSIC)).intValue();
            boolean music=audio.isMusicActive();
            int mode=audio.getMode();
            if(!music || devices!=2 || mode!=AudioManager.MODE_NORMAL) { gate("MEDIA_GATE music="+music+" devices="+devices+" mode="+mode); restore(); retries=0; return; }
            Display d=display.getDisplay(Display.DEFAULT_DISPLAY);
            if(d==null) { restore(); return; }
            int r=d.getRotation(),s=swap();
            if(r<0||r>3||s<0||s>1) { gate("ROTATION_SWAP_GATE rotation="+r+" swap="+s); restore(); return; }
            int result=apply(r,s);
            if(result==4) {
                retries=0;
                handler.removeCallbacks(retry);
                handler.removeCallbacks(monitor);
                handler.postDelayed(monitor,1500);
            } else if ((result==-21 || result==-22) && retries<12 &&
                       android.os.SystemClock.elapsedRealtime()-generationStart<10000) {
                retries++;
                handler.removeCallbacks(retry);
                handler.postDelayed(retry,500);
            }
            if(r!=lastRotation||s!=lastSwap||result!=lastResult) {
                log("ACTUAL_DISPLAY_MEDIA_ROUTE rotation="+r+" swap="+s+" result="+result+" devices="+devices);
                lastRotation=r;lastSwap=s;lastResult=result;
            }
        } catch(Throwable e) { restore(); log("ROUTE_CALLBACK_REFUSED "+e+" cause="+e.getCause()); }
    }
    private static final Runnable update=()->tick();
    private static final Runnable settle=()->tick();
    private static final Runnable retry=()->tick();
    private static final Runnable monitor=()->tick();
    private static void schedule() {
        generationStart=android.os.SystemClock.elapsedRealtime();retries=0;
        handler.removeCallbacks(update);handler.removeCallbacks(settle);handler.removeCallbacks(retry);handler.removeCallbacks(monitor);
        handler.postDelayed(update,250);handler.postDelayed(settle,1200);
    }
    private static final Runnable stopCheck=new Runnable() {
        public void run() {
            if(stopRequested()) {
                int result=restore();
                log("NATIVE_RESTORE_ON_CONTROLLED_STOP result="+result);
                handler.removeCallbacksAndMessages(null);
                if(result==0) Looper.myLooper().quitSafely();
                else handler.postDelayed(this,500); // Keep native ledger; retry instead of forgetting ownership.
            } else handler.postDelayed(this,100);
        }
    };
    private static void silentValidation(String library) throws Exception {
        System.load(library);
        Looper.prepare();
        Class<?> at=Class.forName("android.app.ActivityThread");
        Object thread=at.getDeclaredMethod("systemMain").invoke(null);
        Context context=(Context)at.getDeclaredMethod("getSystemContext").invoke(thread);
        AudioManager am=(AudioManager)context.getSystemService(Context.AUDIO_SERVICE);
        Method devices=AudioManager.class.getDeclaredMethod("getDevicesForStream",int.class);devices.setAccessible(true);
        if(am.isMusicActive()||am.getMode()!=AudioManager.MODE_NORMAL||((Integer)devices.invoke(am,AudioManager.STREAM_MUSIC))!=2){log("SILENT_VALIDATION_REFUSED_USER_AUDIO_OR_ROUTE");System.exit(20);}
        android.media.AudioTrack track=new android.media.AudioTrack.Builder().setAudioAttributes(new android.media.AudioAttributes.Builder().setUsage(android.media.AudioAttributes.USAGE_MEDIA).build()).setAudioFormat(new android.media.AudioFormat.Builder().setSampleRate(48000).setEncoding(android.media.AudioFormat.ENCODING_PCM_16BIT).setChannelMask(android.media.AudioFormat.CHANNEL_OUT_STEREO).build()).setBufferSizeInBytes(48000*4).setTransferMode(android.media.AudioTrack.MODE_STATIC).build();
        short[] silence=new short[96000];if(track.write(silence,0,silence.length)!=silence.length)throw new IllegalStateException("silent buffer write");
        track.setVolume(0f);track.setLoopPoints(0,48000,-1);
        Runtime.getRuntime().addShutdownHook(new Thread(()->{restore();}));
        try {
            track.play();log("SILENT_VALIDATION_READY PID="+android.os.Process.myPid());Thread.sleep(900);
            int[] masks={0x34|0x36<<8,0x36|0x35<<8,0x37|0x35<<8,0x34|0x37<<8};
            for(int r=0;r<4;r++){
                if(stopRequested()||((Integer)devices.invoke(am,AudioManager.STREAM_MUSIC))!=2||am.getMode()!=AudioManager.MODE_NORMAL)throw new IllegalStateException("route changed");
                int rc=apply(r,swap());for(int attempt=0;rc==-21&&attempt<8;attempt++){Thread.sleep(200);rc=apply(r,swap());}
                log("SILENT_NEW_ADDRESS_ROUTE rotation="+r+" result="+rc+" historical_pair_not_physical_calibration="+Integer.toHexString(masks[r]));
                if(rc!=4)throw new IllegalStateException("route not applied");Thread.sleep(400);
            }
        } finally {int restored=restore();log("SILENT_VALIDATION_RESTORED result="+restored);track.stop();track.release();}
        System.exit(0);
    }
    public static void main(String[] args) throws Exception {
        if(args.length==2 && args[1].equals("--silent-validate")){silentValidation(args[0]);return;}
        if(args.length!=1)throw new IllegalArgumentException("library path required");
        System.load(args[0]);
        Looper.prepare();handler=new Handler(Looper.myLooper());
        Class<?> activityThread=Class.forName("android.app.ActivityThread");
        Object thread=activityThread.getDeclaredMethod("systemMain").invoke(null);
        Context context=(Context)activityThread.getDeclaredMethod("getSystemContext").invoke(thread);
        audio=(AudioManager)context.getSystemService(Context.AUDIO_SERVICE);
        display=(DisplayManager)context.getSystemService(Context.DISPLAY_SERVICE);
        devicesForStream=AudioManager.class.getDeclaredMethod("getDevicesForStream",int.class);
        devicesForStream.setAccessible(true);
        Runtime.getRuntime().addShutdownHook(new Thread(()->{restore();System.out.println("OWNED_ROUTE_RESTORED_ON_STOP");}));
        display.registerDisplayListener(new DisplayManager.DisplayListener(){
            public void onDisplayAdded(int id){if(id==0)schedule();}
            public void onDisplayRemoved(int id){if(id==0)restore();}
            public void onDisplayChanged(int id){if(id==0)schedule();}
        },handler);
        audio.registerAudioPlaybackCallback(new AudioManager.AudioPlaybackCallback(){
            public void onPlaybackConfigChanged(List<AudioPlaybackConfiguration> configs){schedule();}
        },handler);
        audio.registerAudioDeviceCallback(new AudioDeviceCallback(){
            public void onAudioDevicesAdded(AudioDeviceInfo[] devices){schedule();}
            public void onAudioDevicesRemoved(AudioDeviceInfo[] devices){schedule();}
        },handler);
        log("NATIVE_API19_LISTENERS_READY_COMPLEMENTARY_INPUTS_BASELINE1 PID="+android.os.Process.myPid()+" UID="+android.os.Process.myUid());
        handler.post(stopCheck);schedule();Looper.loop();
        log("CONTROLLED_HELPER_EXIT");System.exit(0);
    }
}
