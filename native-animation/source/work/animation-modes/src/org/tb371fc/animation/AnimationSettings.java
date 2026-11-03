package org.tb371fc.animation;

import android.app.Activity;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/** A native preference attached to the existing Display & Brightness page. */
public final class AnimationSettings {
    private static final String TAG = "TB371FCAnimation";
    private static final String PROPERTY = "persist.sys.oplus.anim_level";
    private static final String ACTIVE = "debug.r94.animation_active_level";
    private static final String KEY = "tb371fc_animation_style";

    private static int property(String key, int fallback) {
        try {
            Class<?> type = Class.forName("android.os.SystemProperties");
            return (Integer) type.getMethod("getInt", String.class, int.class)
                    .invoke(null, key, fallback);
        } catch (Exception exception) {
            Log.w(TAG, "Cannot read animation mode", exception);
            return fallback;
        }
    }

    private static String label(int value) {
        return value == 4 ? "动画流畅" : "动画质量";
    }

    private static String summary(int desired) {
        int active = property(ACTIVE, desired);
        return label(desired) + (active != desired ? " · 重启后生效" : "");
    }

    private static void setSummary(Object preference, Class<?> type, int value) throws Exception {
        preference.getClass().getMethod("setAssignment", CharSequence.class).invoke(preference, summary(value));
    }

    public static void attach(Object fragment) {
        try {
            Context context = (Context) fragment.getClass().getMethod("getContext").invoke(fragment);
            if (context == null) return;
            Object screen = fragment.getClass().getMethod("getPreferenceScreen").invoke(fragment);
            if (screen == null) return;
            ClassLoader loader = fragment.getClass().getClassLoader();
            Class<?> preferenceType = Class.forName("androidx.preference.Preference", true, loader);
            Class<?> groupType = Class.forName("androidx.preference.PreferenceGroup", true, loader);
            Class<?> listType = Class.forName("com.coui.appcompat.preference.COUIListPreference", true, loader);
            Object existing = groupType.getMethod("findPreference", CharSequence.class).invoke(screen, KEY);
            if (existing != null) return;
            Object preference = listType.getConstructor(Context.class).newInstance(context);
            preferenceType.getMethod("setKey", String.class).invoke(preference, KEY);
            preferenceType.getMethod("setTitle", CharSequence.class).invoke(preference, "动画风格");
            Object parent = groupType.getMethod("findPreference", CharSequence.class)
                    .invoke(screen, "display_more_settings_category");
            if (parent == null) parent = screen;
            Object refresh = groupType.getMethod("findPreference", CharSequence.class)
                    .invoke(screen, "screen_refresh_rate");
            int order = refresh == null ? 7 : (Integer) preferenceType.getMethod("getOrder").invoke(refresh) + 1;
            int children = (Integer) groupType.getMethod("getPreferenceCount").invoke(parent);
            for (int i = 0; i < children; i++) {
                Object child = groupType.getMethod("getPreference", int.class).invoke(parent, i);
                int childOrder = (Integer) preferenceType.getMethod("getOrder").invoke(child);
                if (childOrder >= order && childOrder < Integer.MAX_VALUE)
                    preferenceType.getMethod("setOrder", int.class).invoke(child, childOrder + 1);
            }
            preferenceType.getMethod("setOrder", int.class).invoke(preference, order);
            preferenceType.getMethod("setPersistent", boolean.class).invoke(preference, false);
            listType.getMethod("setEntries", CharSequence[].class).invoke(preference,
                    (Object) new CharSequence[]{"动画质量", "动画流畅"});
            listType.getMethod("setEntryValues", CharSequence[].class).invoke(preference,
                    (Object) new CharSequence[]{"2", "4"});
            listType.getMethod("setValue", String.class).invoke(preference,
                    property(PROPERTY, 2) == 4 ? "4" : "2");
            Class.forName("androidx.preference.DialogPreference", true, loader)
                    .getMethod("setDialogTitle", CharSequence.class).invoke(preference, "动画风格");
            setSummary(preference, preferenceType, property(PROPERTY, 2));

            Class<?> listenerType = Class.forName(
                    "androidx.preference.Preference$OnPreferenceChangeListener", true, loader);
            Object listener = Proxy.newProxyInstance(loader, new Class<?>[]{listenerType},
                    (proxy, method, args) -> {
                        if (!method.getName().equals("onPreferenceChange")) {
                            if (method.getName().equals("hashCode")) return System.identityHashCode(proxy);
                            if (method.getName().equals("equals")) return proxy == args[0];
                            return "AnimationModeListener";
                        }
                        String selection = String.valueOf(args[1]);
                        if (!selection.equals("2") && !selection.equals("4")) return false;
                        int mode = Integer.parseInt(selection);
                        if (property(PROPERTY, 2) == mode) return true;
                        try {
                            Class<?> properties = Class.forName("android.os.SystemProperties");
                            properties.getMethod("set", String.class, String.class)
                                    .invoke(null, PROPERTY, selection);
                            if (property(PROPERTY, -1) != mode) throw new IllegalStateException("Mode not saved");
                            Settings.Secure.putString(context.getContentResolver(), "key_recent_style", "stacked");
                            Settings.Secure.putInt(context.getContentResolver(), "disable_assistant_screen", 0);
                            setSummary(preference, preferenceType, mode);
                            new Handler(Looper.getMainLooper()).postDelayed(() -> {
                                if (context instanceof Activity && ((Activity) context).isFinishing()) return;
                                try {
                                    Class<?> builderType = Class.forName("com.coui.appcompat.dialog.COUIAlertDialogBuilder", true, loader);
                                    Object builder = builderType.getConstructor(Context.class).newInstance(context);
                                    builderType.getMethod("setTitle", CharSequence.class).invoke(builder, "重启后生效");
                                    builderType.getMethod("setMessage", CharSequence.class).invoke(builder,
                                            "已选择“" + label(mode) + "”，重启后生效。");
                                    DialogInterface.OnClickListener reboot = (dialog, which) -> {
                                            try {
                                                ((PowerManager) context.getSystemService(Context.POWER_SERVICE)).reboot(null);
                                            } catch (RuntimeException exception) {
                                                Log.e(TAG, "Reboot failed", exception);
                                                Toast.makeText(context, "请手动重启平板", Toast.LENGTH_LONG).show();
                                            }
                                    };
                                    builderType.getMethod("setPositiveButton", CharSequence.class, DialogInterface.OnClickListener.class)
                                            .invoke(builder, "立即重启", reboot);
                                    builderType.getMethod("setNegativeButton", CharSequence.class, DialogInterface.OnClickListener.class)
                                            .invoke(builder, "稍后", null);
                                    builderType.getMethod("show").invoke(builder);
                                } catch (Exception exception) {
                                    Log.e(TAG, "Cannot show reboot dialog", exception);
                                    Toast.makeText(context, "已保存，重启后生效", Toast.LENGTH_LONG).show();
                                }
                            }, 150);
                            Log.i(TAG, "Saved mode=" + mode);
                            return true;
                        } catch (Exception exception) {
                            Log.e(TAG, "Cannot save animation mode", exception);
                            Toast.makeText(context, "切换未完成，请重试", Toast.LENGTH_LONG).show();
                            return false;
                        }
                    });
            preferenceType.getMethod("setOnPreferenceChangeListener", listenerType)
                    .invoke(preference, listener);
            groupType.getMethod("addPreference", preferenceType).invoke(parent, preference);
            Log.i(TAG, "Animation preference attached");
        } catch (Exception exception) {
            Log.e(TAG, "Cannot attach animation preference", exception);
        }
    }
}
