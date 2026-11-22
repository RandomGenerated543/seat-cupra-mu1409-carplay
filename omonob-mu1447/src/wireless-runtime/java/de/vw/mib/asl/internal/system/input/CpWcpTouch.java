package de.vw.mib.asl.internal.system.input;
import java.io.File;import java.net.DatagramPacket;import java.net.DatagramSocket;import java.net.InetAddress;
import de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership;
/** Bounded asynchronous sender. The input callback does no I/O or thread creation. */
public final class CpWcpTouch implements Runnable {
 private static final Object LOCK=new Object(),MANAGER=new Object();private static final int CAP=64;
 private static final int[][] queue=new int[CAP][4];private static final long[] epochs=new long[CAP],sessions=new long[CAP];
 private static int head,count,seq;private static boolean open,routed;private static long gestureEpoch,gestureSession;
 private static volatile boolean ready,disabled,sending;private static volatile long sendStarted;
 private static Thread supervisor,sender;private static DatagramSocket socket;
 private CpWcpTouch(){}
 private static String root(){String s=System.getProperty("wcpcp.root");return s==null?"":s;}
 public static synchronized void start(){if(supervisor!=null&&supervisor.isAlive())return;try{supervisor=new Thread(new CpWcpTouch(),"Mu1447TouchManager");supervisor.setDaemon(true);supervisor.start();}catch(Throwable e){ready=false;supervisor=null;}}
 public static void attach(Object unused){start();}
 private static boolean press(int type){return type==4||type==8;}
 private static boolean move(int type){return type==5||type==6||type==9||type==10;}
 private static void put(int type,int x,int y,int value){int at=(head+count)%CAP;int[] row=queue[at];row[0]=type;row[1]=x;row[2]=y;row[3]=value;epochs[at]=gestureEpoch;sessions[at]=gestureSession;count++;LOCK.notifyAll();}
 public static boolean onTouch(int type,int x,int y,int value){
  synchronized(LOCK){
   boolean allowed=ready&&!disabled&&Mu1447ScreenOwnership.canTouch();
   if(press(type)){
    if(type==8&&open&&routed){if(allowed&&count<CAP-1)put(type,x,y,value);return true;}
    open=true;routed=allowed&&count<CAP-2;gestureEpoch=Mu1447ScreenOwnership.epoch();gestureSession=Mu1447ScreenOwnership.sessionEpoch();
    if(routed)put(type,x,y,value);return routed;
   }
   if(open&&routed){
    if(type==3){if(ready&&count<CAP)put(type,x,y,value);open=false;routed=false;return true;}
    if(!allowed||gestureEpoch!=Mu1447ScreenOwnership.epoch())return true;
    if(move(type)&&count>0){int at=(head+count-1)%CAP;int[] last=queue[at];if(move(last[0])&&epochs[at]==gestureEpoch&&sessions[at]==gestureSession){last[0]=type;last[1]=x;last[2]=y;last[3]=value;return true;}}
    if(count<CAP-1)put(type,x,y,value);return true;
   }
   if(open){if(type==3){open=false;routed=false;}return false;}
   if(type==3){open=false;routed=false;}
   if(allowed&&count<CAP-1){gestureEpoch=Mu1447ScreenOwnership.epoch();gestureSession=Mu1447ScreenOwnership.sessionEpoch();put(type,x,y,value);return true;}return false;
  }
 }
 public void run(){
  while(true){
   try{
    disabled=new File(root()+"/mnt/persist/wcp_touch_off").exists();
    synchronized(MANAGER){
     if(sender==null||!sender.isAlive()){
      ready=false;socket=new DatagramSocket();sender=new Thread(new Sender(socket),"Mu1447TouchSender");sender.setDaemon(true);sender.start();ready=true;
     }
    }
    if(sending){long age=System.currentTimeMillis()-sendStarted;if(age<0||age>2000L){ready=false;DatagramSocket s=socket;if(s!=null)s.close();}}
    Thread.sleep(100L);
   }catch(InterruptedException stop){ready=false;DatagramSocket s=socket;if(s!=null)s.close();return;}
   catch(Throwable failure){ready=false;try{Thread.sleep(250L);}catch(InterruptedException stop){return;}}
  }
 }
 private static final class Sender implements Runnable {
  private final DatagramSocket own;Sender(DatagramSocket s){own=s;}
  public void run(){boolean deliveredPress=false;long deliveredSession=-1;
   try{
    InetAddress loop=InetAddress.getByName("127.0.0.1");
    while(true){int[] event=new int[4];long epoch,session;
     synchronized(LOCK){if(count==0){LOCK.wait(100L);continue;}int[] row=queue[head];for(int i=0;i<4;i++)event[i]=row[i];epoch=epochs[head];session=sessions[head];head=(head+1)%CAP;count--;}
     if(session!=Mu1447ScreenOwnership.sessionEpoch())continue;
     if(disabled||!Mu1447ScreenOwnership.canTouch()||epoch!=Mu1447ScreenOwnership.epoch()){
      if(event[0]!=3||!deliveredPress||deliveredSession!=session)continue;
     }
     byte[] b=new byte[12];b[0]=87;b[1]=84;b[2]=1;b[3]=(byte)event[0];b[4]=(byte)(event[1]>>8);b[5]=(byte)event[1];b[6]=(byte)(event[2]>>8);b[7]=(byte)event[2];b[8]=(byte)(event[3]>>8);b[9]=(byte)event[3];seq=(seq+1)&65535;b[10]=(byte)(seq>>8);b[11]=(byte)seq;
     sendStarted=System.currentTimeMillis();sending=true;try{own.send(new DatagramPacket(b,b.length,loop,7102));}finally{sending=false;}
     if(press(event[0])){deliveredPress=true;deliveredSession=session;}if(event[0]==3)deliveredPress=false;
    }
   }catch(Throwable failure){}finally{ready=false;sending=false;own.close();synchronized(LOCK){head=0;count=0;}}
  }
 }
}
