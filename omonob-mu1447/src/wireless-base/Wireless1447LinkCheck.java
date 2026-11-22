/** Link only: no instance creation, static initialization or hardware activation. */
public final class Wireless1447LinkCheck {
 public static void main(String[] args) throws Exception {
  String[] names={
   "de.vw.mib.asl.internal.wcpcp.WcpCp",
   "de.vw.mib.asl.internal.wcpcp.WcpCpInvoker",
   "de.vw.mib.asl.internal.wcpcp.WcpHotspot",
   "de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership",
   "de.vw.mib.asl.internal.wcpsi.WcpSi",
   "de.vw.mib.asl.internal.wcpsi.WcpSiInterceptor",
   "de.vw.mib.asl.internal.system.input.CpWcpTouch",
   "de.vw.mib.asl.internal.system.input.TouchInputDeviceImpl",
   "org.omonob.cpmap.wireless.WirelessMapsBootstrap",
   "org.omonob.phone.PhoneConnectionRuntime",
   "org.omonob.phone.PhoneSelectionPolicy",
   "org.omonob.phone.PhoneConnectionSettings"};
  ClassLoader loader=ClassLoader.getSystemClassLoader();
  for(int i=0;i<names.length;i++){
   Class c=Class.forName(names[i],false,loader);
   c.getDeclaredConstructors();c.getDeclaredMethods();c.getDeclaredFields();
  }
  System.out.println("MU1447_WIRELESS_JAVA=PASS classes=12 activators_invoked=0");
 }
}
