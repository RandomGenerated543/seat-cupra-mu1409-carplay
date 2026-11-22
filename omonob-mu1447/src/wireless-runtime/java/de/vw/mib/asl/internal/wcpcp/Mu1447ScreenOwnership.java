package de.vw.mib.asl.internal.wcpcp;
/** Resource ownership and observed canvas state are separate signals. No I/O. */
public final class Mu1447ScreenOwnership {
 private static boolean taken,borrowed,suppressed,pendingUi,ready,foreground;
 private static long epoch,lastTick,sessionEpoch;
 private Mu1447ScreenOwnership(){}
 public static synchronized void onTransfer(int t){
  if(t==1){taken=true;pendingUi=false;}
  else if(t==2){taken=false;if(!borrowed)suppressed=false;}
  else if(t==3)borrowed=true;
  else if(t==4){borrowed=false;if(pendingUi){taken=false;pendingUi=false;}if(!taken)suppressed=false;}
  if(t>=1&&t<=4)epoch++;
 }
 public static synchronized void onObserver(int event){
  if(event==6100008||event==1076641831){
   if(!borrowed&&!taken)suppressed=false;
  }else if(event==6100012||event==6100007)suppressed=true;else return;
  epoch++;
 }
 public static synchronized void onService(String method){
  if("requestUI".equals(method)||"requestUI2".equals(method)){
   if(borrowed)pendingUi=true;else{taken=false;suppressed=false;}epoch++;
  }
 }
 public static synchronized boolean isBlocked(){return taken||borrowed||suppressed;}
 public static synchronized boolean allowAutomaticFront(){return !taken&&!borrowed;}
 public static synchronized boolean clampForeground(boolean value){return value&&!isBlocked();}
 public static synchronized void updateRuntime(boolean registered,boolean visible){ready=registered;foreground=visible&&!isBlocked();lastTick=System.currentTimeMillis();}
 public static synchronized boolean canTouch(){long age=System.currentTimeMillis()-lastTick;return ready&&foreground&&!isBlocked()&&age>=0&&age<=3000L;}
 public static synchronized long epoch(){return epoch;}
 public static synchronized long sessionEpoch(){return sessionEpoch;}
 public static synchronized void sessionDown(){ready=false;foreground=false;pendingUi=false;suppressed=true;epoch++;sessionEpoch++;}
 public static synchronized void reset(){taken=false;borrowed=false;suppressed=false;pendingUi=false;ready=false;foreground=false;lastTick=0;epoch++;sessionEpoch++;}
}
