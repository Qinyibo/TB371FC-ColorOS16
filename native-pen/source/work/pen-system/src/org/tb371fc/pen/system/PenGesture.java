package org.tb371fc.pen.system;
/** No Android dependencies: one button stream, deterministic timing, bounded delayed work. */
public final class PenGesture {
  public interface Loop {long now();void post(Runnable r,long delay);void cancel(Runnable r);}
  public interface Sink {void click(boolean doubleClick);void hold(String state);}
  final Loop loop;final Sink sink;long down=-1,lastTap=-1,lastSecondary=-1;boolean held;Runnable longTimer,tapTimer,holdExpiry;
  public PenGesture(Loop l,Sink s){loop=l;sink=s;}
  public void press(){if(down>=0)return;down=loop.now();held=false;longTimer=()->{if(down>=0){held=true;sink.hold("down");holdExpiry=()->reset();loop.post(holdExpiry,30000);}};loop.post(longTimer,650);}
  public void release(){if(down<0)return;long duration=loop.now()-down;down=-1;if(longTimer!=null)loop.cancel(longTimer);longTimer=null;if(holdExpiry!=null)loop.cancel(holdExpiry);holdExpiry=null;
    if(!held&&duration>=650){sink.hold("down");sink.hold("up");return;}
    if(held){held=false;sink.hold("up");return;}
    long now=loop.now();if(tapTimer!=null&&now-lastTap<=300){loop.cancel(tapTimer);tapTimer=null;lastTap=-1;sink.click(true);return;}
    lastTap=now;tapTimer=()->{tapTimer=null;lastTap=-1;sink.click(false);};loop.post(tapTimer,300);
  }
  public void secondary(){long now=loop.now();if(lastSecondary>=0&&now-lastSecondary<150)return;lastSecondary=now;if(tapTimer!=null)loop.cancel(tapTimer);tapTimer=null;lastTap=-1;sink.click(true);}
  public void reset(){if(longTimer!=null)loop.cancel(longTimer);if(tapTimer!=null)loop.cancel(tapTimer);if(holdExpiry!=null)loop.cancel(holdExpiry);longTimer=tapTimer=holdExpiry=null;down=lastTap=lastSecondary=-1;if(held)sink.hold("cancel");held=false;}
}
