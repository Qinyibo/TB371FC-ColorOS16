package android.os;
/** Compile only. Excluded from DEX; Android supplies the real implementation. */
public abstract class UEventObserver {
 public final void startObserving(String match){}
 public final void stopObserving(){}
 public abstract void onUEvent(UEvent event);
 public static final class UEvent {public String get(String key){return null;}public String get(String key,String fallback){return fallback;}}
}
