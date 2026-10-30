package org.tb371fc.pen;
import java.io.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.GZIPInputStream;

/** Exact source-span recipe. No ZIP re-encoding, Android services, or network access. */
public final class NativePayloadV2 {
  static String sha(File f) throws Exception {
    MessageDigest d=MessageDigest.getInstance("SHA-256");
    try(InputStream in=new FileInputStream(f)){byte[] b=new byte[65536];for(int n;(n=in.read(b))!=-1;)d.update(b,0,n);}
    StringBuilder s=new StringBuilder();for(byte b:d.digest())s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();
  }
  static void copy(InputStream in,OutputStream out,long count) throws Exception {
    byte[] b=new byte[65536];while(count>0){int n=in.read(b,0,(int)Math.min(count,b.length));if(n<0)throw new EOFException();out.write(b,0,n);count-=n;}
  }
  static void apply(File source,File recipe,File next,long expectedSize)throws Exception {
    try(RandomAccessFile src=new RandomAccessFile(source,"r");DataInputStream in=new DataInputStream(new GZIPInputStream(new FileInputStream(recipe)));FileOutputStream out=new FileOutputStream(next)){
      if(in.readLong()!=0x52393450454e3032L)throw new SecurityException("Recipe magic");
      long written=0;byte[] b=new byte[65536];
      while(true){int op=in.readUnsignedByte();if(op==0)break;long count;
        if(op==1){long offset=in.readLong();count=in.readLong();if(offset<0||count<0||offset>src.length()-count)throw new SecurityException("Source bounds");src.seek(offset);
          long left=count;while(left>0){int n=src.read(b,0,(int)Math.min(left,b.length));if(n<0)throw new EOFException();out.write(b,0,n);left-=n;}
        }else if(op==2){count=in.readLong();if(count<0||count>expectedSize-written)throw new SecurityException("Literal bounds");copy(in,out,count);}
        else throw new SecurityException("Recipe opcode");
        written+=count;if(written>expectedSize)throw new SecurityException("Output bounds");
      }
      if(written!=expectedSize||in.read()!=-1)throw new SecurityException("Recipe size or trailing data");out.getFD().sync();
    }
  }
  public static void main(String[] args)throws Exception {
    if(args.length!=2&&args.length!=3)throw new IllegalArgumentException("assets output [source-directory]");
    File assets=new File(args[0]),output=new File(args[1]);Properties cfg=new Properties();
    try(InputStream in=new FileInputStream(new File(assets,"manifest.properties"))){cfg.load(in);}
    // Validate every base and recipe before producing either file.
    for(String k:new String[]{"ipe","ws"}){
      File src=new File(args.length==3?new File(args[2],cfg.getProperty(k+".sourceName")).getPath():cfg.getProperty(k+".source"));
      if(!sha(src).equals(cfg.getProperty(k+".sourceSha")))throw new SecurityException("Base changed: "+k);
      if(!sha(new File(assets,k+".recipe.gz")).equals(cfg.getProperty(k+".recipeSha")))throw new SecurityException("Recipe changed: "+k);
    }
    for(String k:new String[]{"ipe","ws"}){
      File src=new File(args.length==3?new File(args[2],cfg.getProperty(k+".sourceName")).getPath():cfg.getProperty(k+".source"));
      File dir=new File(output,k),target=new File(dir,cfg.getProperty(k+".name"));String expected=cfg.getProperty(k+".outputSha");
      if(target.isFile()){if(!sha(target).equals(expected))throw new SecurityException("Cache differs: "+k);System.out.println("CURRENT "+k);continue;}
      if(!dir.isDirectory()&&!dir.mkdirs())throw new IOException("mkdir "+dir);
      File next=new File(dir,target.getName()+".next");
      apply(src,new File(assets,k+".recipe.gz"),next,Long.parseLong(cfg.getProperty(k+".outputSize")));
      if(!sha(next).equals(expected))throw new SecurityException("Output differs: "+k);
      if(!next.renameTo(target))throw new IOException("publish "+k);System.out.println("BUILT "+k+" "+expected);
    }
    System.out.println("BOTH_VERIFIED");
  }
}
