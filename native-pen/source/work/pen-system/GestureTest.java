import java.util.*;import org.tb371fc.pen.system.PenGesture;
public final class GestureTest {
 static class Loop implements PenGesture.Loop {long t;Map<Runnable,Long> queue=new IdentityHashMap<>();public long now(){return t;}public void post(Runnable r,long d){queue.put(r,t+d);}public void cancel(Runnable r){queue.remove(r);}void advance(long n){long end=t+n;while(true){Runnable next=null;long at=Long.MAX_VALUE;for(Map.Entry<Runnable,Long> e:queue.entrySet())if(e.getValue()<at){at=e.getValue();next=e.getKey();}if(next==null||at>end)break;t=at;queue.remove(next);next.run();}t=end;}}
 static class Sink implements PenGesture.Sink {List<String> calls=new ArrayList<>();public void click(boolean twice){calls.add(twice?"double":"single");}public void hold(String s){calls.add(s);}}
 static void eq(Object a,Object b){if(!a.equals(b))throw new AssertionError(a+" != "+b);}
 public static void main(String[] args){
  Loop l=new Loop();Sink s=new Sink();PenGesture p=new PenGesture(l,s);
  p.press();l.advance(50);p.release();l.advance(299);eq(s.calls.toString(),"[]");l.advance(1);eq(s.calls.toString(),"[single]");s.calls.clear();
  p.press();l.advance(40);p.release();l.advance(150);p.press();l.advance(30);p.release();l.advance(500);eq(s.calls.toString(),"[double]");s.calls.clear();
  p.press();p.press();l.advance(650);eq(s.calls.toString(),"[down]");p.release();p.release();l.advance(500);eq(s.calls.toString(),"[down, up]");s.calls.clear();
  p.press();l.advance(700);p.reset();l.advance(40000);eq(s.calls.toString(),"[down, cancel]");s.calls.clear();
  p.press();l.advance(40);p.release();p.reset();l.advance(500);eq(s.calls.toString(),"[]");
  p.secondary();p.secondary();l.advance(160);p.secondary();eq(s.calls.toString(),"[double, double]");s.calls.clear();
  p.press();l.advance(31000);eq(s.calls.toString(),"[down, cancel]");p.release();l.advance(1000);eq(s.calls.toString(),"[down, cancel]");
  System.out.println("PASS seven native pen gesture timing and teardown scenarios");
 }
}
