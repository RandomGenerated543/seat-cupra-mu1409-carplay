package de.vw.mib.asl.internal.wcpcp;
import java.io.File;import java.lang.reflect.Method;import java.lang.reflect.Proxy;
import de.vw.mib.asl.internal.system.input.CpWcpTouch;
/** Restartable worker and idempotent registration. OEM interfaces remain unchanged. */
public final class Mu1447Lifecycle {
 private static Object listener,listenerLocator,observerProxy,observerDispatcher,observerService;private static boolean listenerAdded,listenerDirty,observerDirty,needsCleanup;
 private static final int[] EVENTS={6100008,6100012,1076641831,6100007,4000024};
 private Mu1447Lifecycle(){}
 public static void start(){
  synchronized(WcpCp.LOCK){if(WcpCp.started)return;WcpCp.started=true;}
  try{WcpHotspot.start();CpWcpTouch.start();Thread t=new Thread(new WcpCp(),"WcpCp");t.setDaemon(true);t.setPriority(1);t.start();}
  catch(Throwable e){synchronized(WcpCp.LOCK){WcpCp.started=false;}WcpCp.log2("start failed",String.valueOf(e));}
 }
 private static boolean off(){return new File(WcpCp.OFF_FLAG).exists();}
 private static boolean addListener()throws Exception{
  Class proxy=Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIProxy"),type=Class.forName("java.lang.Class"),integer=Integer.TYPE,iface=Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIServiceStateListener");
  if(listener!=null&&(listenerDirty||(listenerAdded&&listenerLocator!=WcpCp.locator))){proxy.getMethod("removeServiceStateListener",new Class[]{type,integer,iface}).invoke(listenerLocator,new Object[]{WcpCp.cpInterface,new Integer(0),listener});listenerDirty=false;listenerAdded=false;}
  if(listenerAdded&&listenerLocator==WcpCp.locator)return true;
  if(listener==null){listener=Proxy.newProxyInstance(iface.getClassLoader(),new Class[]{iface},new WcpCpInvoker(1));}
  listenerLocator=WcpCp.locator;listenerDirty=true;
  proxy.getMethod("addServiceStateListener",new Class[]{type,integer,iface}).invoke(listenerLocator,new Object[]{WcpCp.cpInterface,new Integer(0),listener});listenerAdded=true;listenerDirty=false;return true;
 }
 public static Object registerTarget(Method unused,Object dispatcher,Object[] args)throws Exception{
  if(WcpCp.observerTargetId>=0){
   Object current=Class.forName("de.vw.mib.genericevents.EventDispatcherHSM").getMethod("getTarget",new Class[]{Integer.TYPE}).invoke(observerDispatcher,new Object[]{new Integer(WcpCp.observerTargetId)});
   if(current!=observerProxy)throw new Exception("observer target ownership changed");return new Integer(WcpCp.observerTargetId);
  }
  Class target=Class.forName("de.vw.mib.genericevents.Target"),string=Class.forName("java.lang.String");
  Method method=Class.forName("de.vw.mib.genericevents.EventDispatcherHSM").getMethod("registerTarget",new Class[]{target,string});
  Object id=method.invoke(dispatcher,new Object[]{args[0],"hsmtask"});
  if(!(id instanceof Integer)||((Integer)id).intValue()<0)throw new Exception("invalid observer target");
  observerProxy=args[0];observerDispatcher=dispatcher;WcpCp.observerTargetId=((Integer)id).intValue();return id;
 }
 public static Object addObservers(Method method,Object service,Object[] args)throws Exception{
  observerService=service;
  if(observerDirty)Class.forName("de.vw.mib.genericevents.ServiceRegister").getMethod("removeObservers",new Class[]{Class.forName("[I"),Integer.TYPE}).invoke(service,args);
  observerDirty=true;Object result=method.invoke(service,args);observerDirty=false;return result;
 }
 private static boolean cleanup(){
  needsCleanup=true;boolean clean=true;
  Mu1447ScreenOwnership.sessionDown();
  try{WcpCp.unregisterService("runtime worker cleanup");}catch(Throwable failure){clean=false;}
  try{WcpCp.clearOwnerMarker();}catch(Throwable failure){clean=false;}
  if(WcpCp.observerTargetId>=0&&observerProxy!=null){
   try{
    Class dispatcher=Class.forName("de.vw.mib.genericevents.EventDispatcherHSM");
    Object target=dispatcher.getMethod("getTarget",new Class[]{Integer.TYPE}).invoke(observerDispatcher,new Object[]{new Integer(WcpCp.observerTargetId)});
    if(target==observerProxy){
     if(observerService!=null)Class.forName("de.vw.mib.genericevents.ServiceRegister").getMethod("removeObservers",new Class[]{Class.forName("[I"),Integer.TYPE}).invoke(observerService,new Object[]{EVENTS,new Integer(WcpCp.observerTargetId)});
     dispatcher.getMethod("unregisterTarget",new Class[]{Integer.TYPE}).invoke(observerDispatcher,new Object[]{new Integer(WcpCp.observerTargetId)});
    }
    observerProxy=null;observerDispatcher=null;observerService=null;observerDirty=false;
    WcpCp.observerTargetId=-1;WcpCp.observerRegistered=false;
   }catch(Throwable failure){clean=false;WcpCp.log2("observer cleanup pending",String.valueOf(failure));}
  }
  if(listener!=null&&listenerLocator!=null){
   try{
    Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIProxy").getMethod("removeServiceStateListener",new Class[]{Class.forName("java.lang.Class"),Integer.TYPE,Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIServiceStateListener")}).invoke(listenerLocator,new Object[]{WcpCp.cpInterface,new Integer(0),listener});
    listener=null;listenerLocator=null;listenerAdded=false;listenerDirty=false;
   }catch(Throwable failure){clean=false;WcpCp.log2("listener cleanup pending",String.valueOf(failure));}
  }
  WcpCp.active=false;needsCleanup=!clean;return clean;
 }
 public static void run(){
  try{
   int failures=0;
   while(!off()){
    boolean initialized=false;
    for(int attempts=0;attempts<600&&!off();attempts++){
     try{
      if(needsCleanup&&!cleanup()){Thread.sleep(500L);continue;}
      WcpCp.stage=WcpCp.readStage();WcpCp.fakeAddr=WcpCp.readAddr();
      Object locator=WcpCp.waitLocator();if(locator==null)break;WcpCp.locator=locator;
      if(WcpCp.resolve()&&addListener()&&(WcpCp.observerRegistered||WcpCp.registerObserver())){initialized=true;break;}
     }catch(Throwable failure){if(attempts%20==0)WcpCp.log2("initialization retry",String.valueOf(failure));}
     Thread.sleep(500L);
    }
    if(!initialized)break;
    WcpCp.active=true;
    try{WcpCp.loop();break;}catch(Stopped stop){break;}catch(Throwable failure){WcpCp.log2("worker restart",String.valueOf(failure));cleanup();if(++failures>=5)break;Thread.sleep(1000L);}
   }
  }catch(InterruptedException stop){Thread.currentThread().interrupt();}
  finally{cleanup();synchronized(WcpCp.LOCK){WcpCp.started=false;}}
 }
 public static void tick(){
  Mu1447ScreenOwnership.updateRuntime(WcpCp.sessionLive&&WcpCp.weRegistered,WcpCp.fgCarplay);
  CpWcpTouch.start();if(off())throw new Stopped();
 }
 private static final class Stopped extends RuntimeException {private static final long serialVersionUID=1L;}
}
