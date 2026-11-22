package de.vw.mib.asl.internal.wcpcp;
import java.io.File;import java.io.FileInputStream;
/** Consumes a read-only receiver-session probe. Never derives connection death from canvas ownership. */
public final class Mu1447SessionHealth {
 private static String token="",monitor="";private static long sample=-1,lastProgress,lastValid,lastCall;private static boolean knownUp;
 private Mu1447SessionHealth(){}
 private static String root(){String r=System.getProperty("wcpcp.root");return r==null?"":r;}
 private static String read()throws Exception{
  File f=new File(root()+"/ramdisk/mu1447-wcp-session.status");long size=f.length();if(size<1||size>256)throw new Exception("bounds");
  byte[] b=new byte[(int)size];FileInputStream in=new FileInputStream(f);int at=0;try{while(at<b.length){int n=in.read(b,at,b.length-at);if(n<1)throw new Exception("short");at+=n;}if(in.read()!=-1)throw new Exception("changed");}finally{in.close();}
  return new String(b,"US-ASCII");
 }
 private static long positive(String s)throws Exception{if(s.length()<1||s.length()>19)throw new Exception("number");for(int i=0;i<s.length();i++)if(s.charAt(i)<'0'||s.charAt(i)>'9')throw new Exception("number");long n=Long.parseLong(s);if(n<0)throw new Exception("number");return n;}
 public static synchronized boolean observe(boolean video){
  long now=System.currentTimeMillis();if(now<lastCall||now-lastCall>60000L){lastProgress=now;lastValid=now;}lastCall=now;
  try{
   String text=read();String[] line=new String[7];int at=0;for(int i=0;i<7;i++){int end=text.indexOf('\n',at);if(end<at)throw new Exception("line");line[i]=text.substring(at,end);at=end+1;}if(at!=text.length()||!"format=1".equals(line[0]))throw new Exception("format");
   String[] keys={"receiver_pid=","monitor_pid=","generation=","sample=","state=","revision="};for(int i=0;i<6;i++)if(!line[i+1].startsWith(keys[i]))throw new Exception("field");
   long receiver=positive(line[1].substring(13));long pid=positive(line[2].substring(12));long generation=positive(line[3].substring(11));long n=positive(line[4].substring(7));String who=Long.toString(pid);
   if(pid<1||!line[6].equals("revision=mu1447_session_v01"))throw new Exception("revision");
   if(!who.equals(monitor)||n!=sample){monitor=who;sample=n;lastProgress=now;}
   if(now-lastProgress<=5000L){
    if(line[5].equals("state=active")){
     if(receiver<2)throw new Exception("receiver");String next=who+":"+receiver+":"+generation;
     boolean changed=knownUp&&!next.equals(token);token=next;knownUp=true;lastValid=now;return !changed;
    }
    if(line[5].equals("state=idle")){knownUp=false;lastValid=now;return false;}
   }
  }catch(Throwable ignored){}
  return video||(knownUp&&now-lastValid<5000L);
 }
 public static synchronized void reset(){token="";monitor="";sample=-1;lastProgress=0;lastValid=0;lastCall=0;knownUp=false;}
}
