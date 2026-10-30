import org.tb371fc.pen.PenGattValues;
public final class ParserTest {
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[] args){
  for(int i=0;i<256;i++)check(PenGattValues.battery(new byte[]{(byte)i})==(i<=100?i:-1));
  check(PenGattValues.battery(null)==-1);check(PenGattValues.battery(new byte[]{})==-1);check(PenGattValues.battery(new byte[]{50,1})==-1);
  check("1.2.3".equals(PenGattValues.text(new byte[]{49,46,50,46,51,0,0})));
  check(PenGattValues.text(new byte[]{1,2})==null);check(PenGattValues.text(new byte[97])==null);
  check(PenGattValues.text(new byte[]{(byte)255})==null);check(PenGattValues.text(new byte[]{32,32})==null);
  for(int i=0;i<256;i++){int state=(i>>>4)&3;check(PenGattValues.lenovoCharge(new byte[]{(byte)i})==(state==0?-1:state==3?1:0));}
  check(PenGattValues.lenovoCharge(null)==-1);check(PenGattValues.lenovoCharge(new byte[]{1,2})==-1);
  System.out.println("PASS battery, Lenovo charge flags and malformed metadata inputs");
 }
}
