package org.tb371fc.pen;
/** Pure parsers: reject malformed values rather than invent battery or metadata. */
public final class PenGattValues {
  public static int battery(byte[] b){return b!=null&&b.length==1&&(b[0]&255)<=100?b[0]&255:-1;}
  /** Lenovo 2A1A mapping from the supplied reference; 00 is unknown. */
  public static int lenovoCharge(byte[] b){if(b==null||b.length!=1)return -1;int state=((b[0]&255)>>>4)&3;return state==0?-1:state==3?1:0;}
  public static String text(byte[] b){
    if(b==null||b.length==0||b.length>96)return null;
    StringBuilder s=new StringBuilder();for(byte v:b){int n=v&255;if(n==0)break;if(n<32||n>126)return null;s.append((char)n);}
    String r=s.toString().trim();return r.isEmpty()?null:r;
  }
}
