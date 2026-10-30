import org.tb371fc.pen.PenSession;
public final class SessionTest {
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[] args){
  PenSession p=new PenSession(s->{});String a="12:34:56:78:9A:BC";
  check(p.begin(a,"unknown",true)==-1);
  long g=p.beginHardware(a,"actual hardware name",true,true);check(g>=0);
  check(!p.ready(g,a,false,true));check(!p.ready(g,a,true,false));check(p.ready(g,a,true,true));
  check(p.battery(g,new byte[]{0}));check(p.snapshot().battery==0);check(!p.battery(g,new byte[]{(byte)101}));
  p.disconnect();check(!p.snapshot().connected);check(p.snapshot().battery==-1);check(!p.ready(g,a,true,true));check(!p.battery(g,new byte[]{80}));
  check(p.beginHardware("00:00:00:00:00:00","anything",true,true)==-1);
  check(p.beginHardware(a,"anything",false,true)==-1);
  System.out.println("PASS real-link requirements, hardware identity, stale callbacks and unknown battery");
 }
}
