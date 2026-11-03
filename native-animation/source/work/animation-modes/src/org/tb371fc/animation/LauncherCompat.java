package org.tb371fc.animation;

import android.view.MotionEvent;
import com.android.launcher3.Alarm;
import com.android.common.util.AppFeatureUtils;
import com.android.common.util.LauncherAnimConfig;
import com.android.common.util.PlatformLevelUtils;
import com.oplus.quickstep.common.settingsvalue.CommonSettingsValueProxy;

/** Select native paths and timing; never rewrite settled card geometry. */
public final class LauncherCompat {
    /** The lightweight fling controller has no native stacked-overview lifecycle. */
    public static boolean lightDesktopController(int level) {
        return PlatformLevelUtils.isAnimationLevel(level)
                && !(level == 4 && CommonSettingsValueProxy.isStackLayout());
    }

    public static void desktopPause(Alarm alarm, MotionEvent event, int screenHeight) {
        if (!PlatformLevelUtils.isAnimationLevel(4) || !CommonSettingsValueProxy.isStackLayout()) return;
        if (event.getActionMasked() == MotionEvent.ACTION_MOVE && event.getY() < screenHeight * .96f) {
            alarm.setAlarm(120L);
        } else {
            alarm.cancelAlarm();
        }
    }

    /** Retain the native transition's relative timings while slowing it by 25%. */
    public static long lightLaunchDuration(long original) {
        return PlatformLevelUtils.isAnimationLevel(4) ? original * 5L / 4L : original;
    }

    public static boolean lightRecentWithoutStack(boolean original) {
        return original && !CommonSettingsValueProxy.isStackLayout();
    }

    public static boolean lightEnterRecentsWithoutStack(AppFeatureUtils original) {
        return original.isLightEnterRecentsAnimation() && !CommonSettingsValueProxy.isStackLayout();
    }
    public static boolean supportsStack() {
        return PlatformLevelUtils.isAnimationLevel(1)
                || PlatformLevelUtils.isAnimationLevel(2)
                || PlatformLevelUtils.isAnimationLevel(4);
    }

    public static boolean lightRecentsWithoutStack() {
        return LauncherAnimConfig.isLevelBOrBPlus() && !CommonSettingsValueProxy.isStackLayout();
    }

    public static boolean adaptiveLowWithoutStack() {
        return LauncherAnimConfig.INSTANCE.isAdaptiveLowAnimation()
                && !CommonSettingsValueProxy.isStackLayout();
    }

    public static long recentsPauseTimeout(long original) {
        return CommonSettingsValueProxy.isStackLayout() ? Math.min(original, 120L) : original;
    }

    public static long stackTransitionDuration(long original) {
        return PlatformLevelUtils.isAnimationLevel(4) && CommonSettingsValueProxy.isStackLayout()
                ? Math.min(original, 280L) : original;
    }

}
