import java.nio.file.*;import java.util.*;import java.util.jar.*;import java.lang.reflect.*;
import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class JavaAudit {
 static final String CP="de/vw/mib/asl/internal/wcpcp/WcpCp",HELPER="de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership";
 public static volatile boolean ready;public static volatile int attempts,loops,claims;
 public static boolean resolve(){attempts++;return ready;}
 public static void loop(){loops++;}
 public static void claim(boolean value){if(value)claims++;}
 static class Loader extends ClassLoader {
  final Map<String,byte[]> classes;Loader(Map<String,byte[]> c){super(JavaAudit.class.getClassLoader());classes=c;}
  protected Class<?> loadClass(String n,boolean r)throws ClassNotFoundException{
   synchronized(getClassLoadingLock(n)){Class<?> c=findLoadedClass(n);if(c==null)c=classes.containsKey(n)?defineClass(n,classes.get(n),0,classes.get(n).length):super.loadClass(n,false);if(r)resolveClass(c);return c;}
  }
 }
 static Map<String,byte[]> read(Path jar)throws Exception{
  Map<String,byte[]> map=new HashMap<>();try(JarFile z=new JarFile(jar.toFile())){for(Enumeration<JarEntry> e=z.entries();e.hasMoreElements();){JarEntry n=e.nextElement();if(n.getName().endsWith(".class"))map.put(n.getName().replace('/','.').replace(".class",""),z.getInputStream(n).readAllBytes());}}return map;
 }
 static void replace(MethodNode m,InsnList x){m.instructions.clear();m.instructions.add(x);m.tryCatchBlocks.clear();if(m.localVariables!=null)m.localVariables.clear();}
 static byte[] boundaryStubs(byte[] b){
  ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);
  for(MethodNode m:c.methods){InsnList x=new InsnList();
   if(m.name.equals("waitLocator")){x.add(new TypeInsnNode(Opcodes.NEW,"java/lang/Object"));x.add(new InsnNode(Opcodes.DUP));x.add(new MethodInsnNode(Opcodes.INVOKESPECIAL,"java/lang/Object","<init>","()V",false));x.add(new InsnNode(Opcodes.ARETURN));replace(m,x);}
   if(m.name.equals("resolve")){x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"JavaAudit","resolve","()Z",false));x.add(new InsnNode(Opcodes.IRETURN));replace(m,x);}
   if(m.name.equals("addStateListener")||m.name.equals("registerObserver")){x.add(new InsnNode(Opcodes.ICONST_1));x.add(new InsnNode(Opcodes.IRETURN));replace(m,x);}
   if(m.name.equals("loop")){x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"JavaAudit","loop","()V",false));x.add(new InsnNode(Opcodes.RETURN));replace(m,x);}
   if(m.name.equals("start"))for(AbstractInsnNode n:m.instructions.toArray())if(n instanceof MethodInsnNode&&((MethodInsnNode)n).owner.endsWith("/WcpHotspot")&&((MethodInsnNode)n).name.equals("start"))m.instructions.remove(n);
  }
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 static byte[] notificationStub(byte[] b){
  ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);
  for(MethodNode m:c.methods)if(m.name.equals("sendUpdateMode")){
   InsnList x=new InsnList();x.add(new VarInsnNode(Opcodes.ILOAD,0));x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"JavaAudit","claim","(Z)V",false));x.add(new InsnNode(Opcodes.RETURN));replace(m,x);
  }
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 static void field(Class<?> c,String n,Object v)throws Exception{Field f=c.getDeclaredField(n);f.setAccessible(true);f.set(null,v);}
 static Object get(Class<?> c,String n)throws Exception{Field f=c.getDeclaredField(n);f.setAccessible(true);return f.get(null);}
 static Method method(Class<?> c,String n,Class<?>...args)throws Exception{Method m=c.getDeclaredMethod(n,args);m.setAccessible(true);return m;}
 public static class Resource {public int resourceID=2,transferType;public Resource(int t){transferType=t;}}
 public static class Event {final int id;public Event(int n){id=n;}public int getReceiverEventId(){return id;}}
 static void transfer(Class<?> cp,int t)throws Exception{method(cp,"trackScreen",Object[].class).invoke(null,new Object[]{new Object[]{new Object[]{new Resource(t)}}});}
 static void observer(Class<?> cp,int n)throws Exception{method(cp,"onObserverEvent",Object.class).invoke(null,new Event(n));}
 public static void main(String[] a)throws Exception{
  Path root=Files.createTempDirectory("mu1447-audit-");System.setProperty("wcpcp.root",root.toString());System.setProperty("cpvc.offline","1");Files.createDirectories(root.resolve("dev/shmem"));
  Map<String,byte[]> classes=read(Paths.get(a[0]));Class<?> cp=new Loader(classes).loadClass(CP.replace('/','.'));Class<?> ownership=cp.getClassLoader().loadClass(HELPER);
  Method blocked=ownership.getMethod("isBlocked"),reset=ownership.getMethod("reset");field(cp,"mGetReceiverEventId",Event.class.getMethod("getReceiverEventId"));field(cp,"stage",3);
  // Actual shipped methods, with no HMI dependencies invoked on this early-return path.
  transfer(cp,3);observer(cp,6100012);transfer(cp,4);
  field(cp,"fgCarplay",true);method(cp,"syncCanvas").invoke(null);
  if(!Boolean.TRUE.equals(blocked.invoke(null))||!Boolean.FALSE.equals(get(cp,"fgCarplay")))throw new AssertionError("expected stuck camera state not reproduced");
  System.out.println("REPRODUCED ownership: borrow -> left-observer -> unborrow leaves taken=true; syncCanvas refuses recovery");
  reset.invoke(null);transfer(cp,3);observer(cp,6100008);
  if(!Boolean.TRUE.equals(blocked.invoke(null)))throw new AssertionError();
  System.out.println("REPRODUCED ownership: enter-observer cannot clear an outstanding borrow; no expiry/reconciliation path");
  Path heartbeat=root.resolve("dev/shmem/wcp_cp_session");Files.writeString(heartbeat,"1");
  if(!Boolean.TRUE.equals(method(cp,"sessionFresh").invoke(null)))throw new AssertionError();Files.delete(heartbeat);
  if(!Boolean.FALSE.equals(method(cp,"sessionFresh").invoke(null)))throw new AssertionError();
  System.out.println("REPRODUCED liveness: losing the main-video marker makes sessionFresh=false without consulting receiver process/control connection");
  // Replace only outbound notification boundary; actual camera/confirmation code runs.
  Map<String,byte[]> screen=new HashMap<>(classes);screen.put(CP.replace('/','.'),notificationStub(classes.get(CP.replace('/','.'))));
  Class<?> camera=new Loader(screen).loadClass(CP.replace('/','.'));Class<?> owner=camera.getClassLoader().loadClass(HELPER);
  owner.getMethod("onTransfer",int.class).invoke(null,3);field(camera,"stage",3);field(camera,"weRegistered",true);field(camera,"confirmScreen",true);
  claims=0;method(camera,"maybeConfirmScreen").invoke(null);
  if(claims!=1||!Boolean.TRUE.equals(owner.getMethod("isBlocked").invoke(null)))throw new AssertionError("missing contradictory owner claim");
  System.out.println("REPRODUCED parking handoff: maybeConfirmScreen sends device ownership=true while our own helper still marks camera borrow blocked");
  // Stub only boot dependency boundaries; leave start/run and their latches untouched.
  Map<String,byte[]> boot=new HashMap<>(classes);boot.put(CP.replace('/','.'),boundaryStubs(classes.get(CP.replace('/','.'))));
  Class<?> start=new Loader(boot).loadClass(CP.replace('/','.'));ready=false;attempts=0;loops=0;
  start.getMethod("start").invoke(null);long until=System.currentTimeMillis()+2000;while(attempts<1&&System.currentTimeMillis()<until)Thread.sleep(5);Thread.sleep(40);
  if(attempts!=1)throw new AssertionError("first boot resolve was not called");ready=true;start.getMethod("start").invoke(null);Thread.sleep(100);
  if(attempts!=1||loops!=0||!Boolean.TRUE.equals(get(start,"started")))throw new AssertionError("boot failure did not remain latched");
  System.out.println("REPRODUCED startup: one temporary resolve failure leaves started=true; start() cannot retry after dependencies become ready");
 }
}
