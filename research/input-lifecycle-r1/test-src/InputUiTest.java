package org.tb371fc.inputcontract;

import android.graphics.Point;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.MotionEvent.PointerCoords;
import com.android.uiautomator.core.*;
import com.android.uiautomator.testrunner.UiAutomatorTestCase;
import java.io.*;

/** Finite navigation tests through Android UI automation, without hardware events. */
public class InputUiTest extends UiAutomatorTestCase {
    static final String SETTINGS="com.android.settings", FILES="com.coloros.filemanager";
    final File output=new File("/data/local/tmp/tb371fc-input-ui-r1");
    void report(String value) {
        Bundle b=new Bundle();b.putString("stream","CASE "+value+"\n");getAutomationSupport().sendStatus(0,b);
    }
    String command(String... args)throws Exception {
        Process p=new ProcessBuilder(args).redirectErrorStream(true).start();
        String result;
        try(InputStream in=p.getInputStream()){result=new String(in.readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);}
        if(p.waitFor()!=0)throw new AssertionError(result);return result;
    }
    boolean foreground(String name) {
        long until=SystemClock.uptimeMillis()+6000;
        while(SystemClock.uptimeMillis()<until){if(name.equals(getUiDevice().getCurrentPackageName()))return true;sleep(100);}
        return false;
    }
    void settings()throws Exception {
        command("am","start","-W","-a","android.settings.SETTINGS");assertTrue("Settings foreground",foreground(SETTINGS));
    }
    void files()throws Exception {
        command("am","start","-W","-n","com.coloros.filemanager/com.oplus.filemanager.main.ui.MainActivity");
        assertTrue("Files foreground",foreground(FILES));
    }
    void homeSwipe() {
        int w=getUiDevice().getDisplayWidth(),h=getUiDevice().getDisplayHeight();
        assertTrue("Home gesture injected",getUiDevice().swipe(w/2,h-3,w/2,h/3,45));
        assertTrue("Gesture returned to Launcher",foreground("com.android.launcher"));
    }
    public void testInputLifecycle()throws Exception {
        output.mkdirs();
        try {
            settings();
            UiObject about=new UiObject(new UiSelector().textMatches("关于本机|关于设备|关于平板"));
            if(about.exists()) {
                String old=getUiDevice().getCurrentActivityName();assertTrue("Ordinary tap",about.click());
                sleep(500);getUiDevice().takeScreenshot(new File(output,"ordinary-tap.png"));
                report("ordinary_tap_delivered");
            } else {
                UiObject wifi=new UiObject(new UiSelector().text("WLAN"));
                assertTrue("Read-only settings navigation item",wifi.exists());assertTrue("Ordinary tap",wifi.click());
                sleep(500);report("ordinary_tap_delivered");
            }
            homeSwipe();report("normal_home_pass");

            settings();
            int w=getUiDevice().getDisplayWidth(),h=getUiDevice().getDisplayHeight();
            // A task change interrupts an actual ongoing Android gesture; the
            // dispatcher supplies cancellation with a consistent downTime.
            Process swipe=new ProcessBuilder("input","swipe",String.valueOf(w/2),String.valueOf(h-3),
                String.valueOf(w/2),String.valueOf(h/3),"600").redirectErrorStream(true).start();
            sleep(100);files();
            try(InputStream in=swipe.getInputStream()){in.readAllBytes();}assertEquals(0,swipe.waitFor());
            sleep(500);homeSwipe();report("interrupted_gesture_then_home_pass");

            settings();w=getUiDevice().getDisplayWidth();h=getUiDevice().getDisplayHeight();
            Point middle=new Point(w/2,h/2);
            assertTrue(getUiDevice().swipe(new Point[]{new Point(w/2,h-3),middle,middle,middle,middle,middle},20));
            assertTrue("Overview/Launcher after hold",foreground("com.android.launcher"));
            getUiDevice().takeScreenshot(new File(output,"overview.png"));report("hold_to_overview_pass");

            files();w=getUiDevice().getDisplayWidth();h=getUiDevice().getDisplayHeight();
            PointerCoords[][] paths=new PointerCoords[4][30];
            for(int pointer=0;pointer<4;pointer++)for(int step=0;step<30;step++) {
                float progress=step/29f;
                float x=((pointer&1)==0?0.2f:0.8f),y=((pointer&2)==0?0.25f:0.75f);
                PointerCoords c=new PointerCoords();c.x=(x+(0.5f-x)*progress*0.65f)*w;
                c.y=(y+(0.5f-y)*progress*0.65f)*h;c.pressure=1;c.size=1;paths[pointer][step]=c;
            }
            android.util.Log.i("TB371FCInputContract","BEGIN_FOUR_POINTER_PINCH");
            assertTrue(new UiObject(new UiSelector().packageName(FILES)).performMultiPointerGesture(paths));
            sleep(800);getUiDevice().takeScreenshot(new File(output,"after-four-pointer.png"));
            report("four_pointer_sequence_delivered");homeSwipe();report("home_after_multi_pointer_pass");

            settings();homeSwipe();getUiDevice().takeScreenshot(new File(output,"final-home.png"));
            report("final_ordinary_home_pass");
        } catch(Throwable error) {
            getUiDevice().takeScreenshot(new File(output,"failure.png"));
            getUiDevice().dumpWindowHierarchy("tb371fc-input-ui-failure.xml");
            throw error;
        }
    }
}
