/** Separate-VM metadata check; no HMI activators or service setters are invoked. */
public final class RuntimeLinkCheck {
 public static void main(String[] args)throws Exception{
  String[] names={"de.vw.mib.asl.internal.wcpcp.WcpCp","de.vw.mib.asl.internal.wcpcp.WcpCpInvoker","de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership","de.vw.mib.asl.internal.wcpcp.Mu1447SessionHealth","de.vw.mib.asl.internal.wcpcp.Mu1447Lifecycle","de.vw.mib.asl.internal.wcpcp.Mu1447Lifecycle$Stopped","de.vw.mib.asl.internal.system.input.CpWcpTouch","de.vw.mib.asl.internal.system.input.CpWcpTouch$Sender","de.vw.mib.asl.internal.system.input.TouchInputDeviceImpl","org.omonob.cpmap.wireless.WirelessMapsBootstrap"};
  ClassLoader loader=Class.forName("RuntimeLinkCheck").getClassLoader();
  for(int i=0;i<names.length;i++){Class c=Class.forName(names[i],false,loader);c.getDeclaredFields();c.getDeclaredMethods();c.getDeclaredConstructors();}
  Class integer=Integer.TYPE,target=Class.forName("de.vw.mib.genericevents.Target",false,loader),dispatcher=Class.forName("de.vw.mib.genericevents.EventDispatcherHSM",false,loader),service=Class.forName("de.vw.mib.genericevents.ServiceRegister",false,loader);
  dispatcher.getMethod("registerTarget",new Class[]{target,Class.forName("java.lang.String")});dispatcher.getMethod("getTarget",new Class[]{integer});dispatcher.getMethod("unregisterTarget",new Class[]{integer});service.getMethod("removeObservers",new Class[]{Class.forName("[I"),integer});
  Class proxy=Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIProxy",false,loader),listener=Class.forName("de.vw.mib.asl.framework.api.dsiproxy.DSIServiceStateListener",false,loader);
  proxy.getMethod("removeServiceStateListener",new Class[]{Class.forName("java.lang.Class"),integer,listener});
  System.out.println("MU1447_RUNTIME_JAVA=PASS classes=10 activators_invoked=0");
 }
}
