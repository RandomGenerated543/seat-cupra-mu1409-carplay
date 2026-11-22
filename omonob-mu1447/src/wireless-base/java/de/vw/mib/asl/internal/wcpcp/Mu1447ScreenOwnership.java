package de.vw.mib.asl.internal.wcpcp;
/** Independent take/borrow state. A visible underlying canvas is not ownership. */
public final class Mu1447ScreenOwnership {
 private static boolean taken,borrowed;
 private Mu1447ScreenOwnership() {}
 public static synchronized void onTransfer(int transfer) {
  if(transfer==1)taken=true;
  else if(transfer==2)taken=false;
  else if(transfer==3)borrowed=true;
  else if(transfer==4)borrowed=false;
 }
 public static synchronized void onObserver(int event) {
  if(event==6100008 || event==1076641831)taken=false;
  else if(event==6100012)taken=true;
 }
 public static synchronized boolean isBlocked(){return taken||borrowed;}
 public static synchronized void reset(){taken=false;borrowed=false;}
}
