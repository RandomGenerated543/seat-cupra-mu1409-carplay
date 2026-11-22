import java.nio.file.*;import java.util.*;import java.lang.reflect.*;import java.net.*;import java.util.concurrent.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class RuntimeTests {
 static final String CP="de.vw.mib.asl.internal.wcpcp.WcpCp",OWN="de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership",TOUCH="de.vw.mib.asl.internal.system.input.CpWcpTouch";
 static Class<?> cp,own,touch;static int notifications;static volatile int tries,observerTries,loops;
 public static class Resource {public int resourceID,owner,transferType;public Resource(){}Resource(int t){resourceID=2;transferType=t;}}
 public static class Event {int id;Event(int n){id=n;}public int getReceiverEventId(){return id;}}
 public static class App {}
 public static class Canvas {public boolean isCanvasVisible(){return true;}}
 public static class Services {private Object properties=new Canvas();}
 public static class Api {public Object getServices(){return new Services();}}
 public static class Factory {public static Object get(){return new Api();}}
 static class RecordingSocket extends DatagramSocket {final CountDownLatch entered=new CountDownLatch(1),unblock=new CountDownLatch(1);final List<Integer> events=Collections.synchronizedList(new ArrayList<Integer>());boolean stall;RecordingSocket(boolean s)throws Exception{super((SocketAddress)null);stall=s;}public void send(DatagramPacket p){entered.countDown();try{if(stall)unblock.await();}catch(InterruptedException e){throw new RuntimeException(e);}events.add(p.getData()[3]&255);}public void close(){unblock.countDown();super.close();}}
 static void set(Class<?> c,String n,Object x)throws Exception{JavaAudit.field(c,n,x);}static Object get(Class<?> c,String n)throws Exception{return JavaAudit.get(c,n);}static Method method(Class<?> c,String n,Class<?>...a)throws Exception{return JavaAudit.method(c,n,a);}
 static void call(String name,Class<?>[] types,Object...v)throws Exception{method(own,name,types).invoke(null,v);}
 static boolean blocked()throws Exception{return (Boolean)method(own,"isBlocked").invoke(null);}
 static void reset()throws Exception{call("reset",new Class[0]);set(cp,"confirmScreen",false);}
 static void transfer(int t)throws Exception{method(cp,"trackScreen",Object[].class).invoke(null,new Object[]{new Object[]{new Object[]{new Resource(t)}}});}
 static void observer(int n)throws Exception{method(cp,"onObserverEvent",Object.class).invoke(null,new Event(n));}
 public static void capture(Object[] args){Object array=args[0];for(int i=0;i<Array.getLength(array);i++){Resource r=(Resource)Array.get(array,i);if(r.resourceID==2&&r.owner==2)notifications++;}}
 static byte[] outbound(byte[] b){ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);for(MethodNode m:c.methods)if(m.name.equals("sendNotification")){InsnList x=new InsnList();x.add(new VarInsnNode(Opcodes.ALOAD,2));x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"RuntimeTests","capture","([Ljava/lang/Object;)V",false));x.add(new InsnNode(Opcodes.RETURN));JavaAudit.replace(m,x);}ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();}
 static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
 static String health(long sample,String state,long generation){return "format=1\nreceiver_pid=123\nmonitor_pid=456\ngeneration="+generation+"\nsample="+sample+"\nstate="+state+"\nrevision=mu1447_session_v01\n";}
 public static boolean initReady(){return ++tries>=3;}public static boolean observerReady(){return ++observerTries>=2;}public static void loopDone(){loops++;}
 static byte[] mockInit(byte[] b,boolean life){
  ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);
  for(MethodNode m:c.methods){InsnList x=new InsnList();boolean change=false;
   if(life&&m.name.equals("addListener")){x.add(new InsnNode(Opcodes.ICONST_1));x.add(new InsnNode(Opcodes.IRETURN));change=true;}
   if(!life&&m.name.equals("waitLocator")){x.add(new TypeInsnNode(Opcodes.NEW,"java/lang/Object"));x.add(new InsnNode(Opcodes.DUP));x.add(new MethodInsnNode(Opcodes.INVOKESPECIAL,"java/lang/Object","<init>","()V",false));x.add(new InsnNode(Opcodes.ARETURN));change=true;}
   String target=!life&&m.name.equals("resolve")?"initReady":!life&&m.name.equals("registerObserver")?"observerReady":!life&&m.name.equals("loop")?"loopDone":null;
   if(target!=null){x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"RuntimeTests",target,target.equals("loopDone")?"()V":"()Z",false));x.add(new InsnNode(target.equals("loopDone")?Opcodes.RETURN:Opcodes.IRETURN));change=true;}
   if(change)JavaAudit.replace(m,x);
  }ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 public static void main(String[] a)throws Exception{
  Path root=Files.createTempDirectory("mu1447-runtime-tests-");Files.createDirectories(root.resolve("dev/shmem"));Files.createDirectories(root.resolve("ramdisk"));System.setProperty("wcpcp.root",root.toString());System.setProperty("cpvc.offline","1");
  Map<String,byte[]> map=JavaAudit.read(Paths.get(a[0]));map.putAll(JavaAudit.read(Paths.get(a[1])));map.put(CP,outbound(map.get(CP)));
  JavaAudit.Loader loader=new JavaAudit.Loader(map);cp=loader.loadClass(CP);own=loader.loadClass(OWN);touch=loader.loadClass(TOUCH);
  set(cp,"stage",3);set(cp,"mGetReceiverEventId",Event.class.getMethod("getReceiverEventId"));set(cp,"mCanvasGetApi",Factory.class.getMethod("get"));set(cp,"resourceComp",Resource.class);set(cp,"appStateComp",App.class);set(cp,"weRegistered",true);
  reset();transfer(3);observer(6100012);transfer(4);check(!blocked(),"camera left/unborrow latched");method(cp,"syncCanvas").invoke(null);check((Boolean)get(cp,"fgCarplay"),"canvas did not recover");
  reset();transfer(1);transfer(3);observer(6100012);transfer(4);check(blocked(),"unborrow cleared independent take");transfer(2);check(!blocked(),"untake did not recover");
  reset();transfer(1);observer(6100008);check(blocked(),"stale enter erased independent take");transfer(2);long beforeEpoch=(Long)method(own,"epoch").invoke(null);observer(4000024);check((Long)method(own,"epoch").invoke(null)==beforeEpoch,"audio observer cancelled touch gesture");
  reset();transfer(3);observer(6100008);method(cp,"syncCanvas").invoke(null);check(blocked()&&!(Boolean)get(cp,"fgCarplay"),"stale canvas/observer stole camera");
  notifications=0;set(cp,"confirmScreen",true);method(cp,"maybeConfirmScreen").invoke(null);check(notifications==0&&(Boolean)get(cp,"confirmScreen"),"blocked screen claim escaped/deferred request lost");transfer(4);method(cp,"maybeConfirmScreen").invoke(null);check(notifications==1&&!(Boolean)get(cp,"confirmScreen"),"camera release did not replay exactly once");method(cp,"maybeConfirmScreen").invoke(null);check(notifications==1,"duplicate notification");
  reset();transfer(3);method(cp,"onServiceCall",String.class,Object[].class).invoke(null,"requestUI",new Object[]{new Object[]{0}});check(blocked(),"explicit UI stole camera");transfer(4);check(!blocked(),"explicit deferred UI did not release");
  reset();transfer(3);call("sessionDown",new Class[0]);check(blocked(),"phone disconnect erased physical camera ownership");transfer(4);check(!blocked(),"camera could not release after session end");
  reset();set(cp,"weRegistered",false);call("updateRuntime",new Class[]{boolean.class,boolean.class},false,true);check(!(Boolean)method(own,"canTouch").invoke(null),"native wired HMI touch intercepted");
  System.out.println("OWNERSHIP=PASS mixed_camera_order independent_take stale_canvas deferred_claim_once explicit_UI session_drop_during_camera wired_fallback");
  Class<?> h=loader.loadClass("de.vw.mib.asl.internal.wcpcp.Mu1447SessionHealth");Path status=root.resolve("ramdisk/mu1447-wcp-session.status");Files.writeString(status,health(1,"active",1));check((Boolean)method(h,"observe",boolean.class).invoke(null,false),"active receiver depended on video");Files.writeString(status,health(2,"active",1));check((Boolean)method(h,"observe",boolean.class).invoke(null,false),"video gap ended live session");Files.writeString(status,health(3,"idle",2));check(!(Boolean)method(h,"observe",boolean.class).invoke(null,true),"real end hidden by stale video heartbeat");
  Files.writeString(status,"garbage\n");check((Boolean)method(h,"observe",boolean.class).invoke(null,true),"unknown probe broke video fallback");
  Files.writeString(status,health(4,"active",3));check((Boolean)method(h,"observe",boolean.class).invoke(null,false),"new session not active");Files.writeString(status,health(5,"active",4));check(!(Boolean)method(h,"observe",boolean.class).invoke(null,false),"unobserved session replacement did not release old service");Files.writeString(status,health(6,"active",4));check((Boolean)method(h,"observe",boolean.class).invoke(null,false),"replacement did not recover");
  set(h,"lastProgress",System.currentTimeMillis()-20000L);set(h,"lastValid",System.currentTimeMillis()-20000L);check(!(Boolean)method(h,"observe",boolean.class).invoke(null,false),"stopped monitor retained session");
  System.out.println("SESSION=PASS active_without_main_video real_end_with_stale_video unknown_fallback");
  reset();call("updateRuntime",new Class[]{boolean.class,boolean.class},true,true);set(touch,"ready",true);set(touch,"disabled",false);
  RecordingSocket socket=new RecordingSocket(true);Class<?> sender=loader.loadClass(TOUCH+"$Sender");Constructor<?> ctor=sender.getDeclaredConstructor(DatagramSocket.class);ctor.setAccessible(true);Thread worker=new Thread((Runnable)ctor.newInstance(socket));worker.setDaemon(true);worker.start();
  Method on=touch.getMethod("onTouch",int.class,int.class,int.class,int.class);long start=System.nanoTime();check((Boolean)on.invoke(null,4,100,100,0),"press not accepted");check((System.nanoTime()-start)<200000000L,"input blocked");check(socket.entered.await(1,TimeUnit.SECONDS),"sender not entered");
  for(int i=0;i<10000;i++)on.invoke(null,5,100+i,100,0);check(((Integer)get(touch,"count"))<64,"unbounded queue");
  transfer(3);check((Boolean)on.invoke(null,3,100,100,0),"old release leaked to OEM camera");check(!(Boolean)on.invoke(null,4,101,101,0),"camera touch swallowed");transfer(4);call("updateRuntime",new Class[]{boolean.class,boolean.class},true,true);check(!(Boolean)on.invoke(null,5,102,102,0),"OEM half gesture leaked to phone after camera release");check(!(Boolean)on.invoke(null,3,102,102,0),"OEM release leaked");
  socket.close();worker.interrupt();worker.join(1000);set(touch,"ready",true);set(touch,"disabled",true);check(!(Boolean)on.invoke(null,4,1,1,0),"touch-off cache ignored");
  Map<String,byte[]> initMap=JavaAudit.read(Paths.get(a[0]));initMap.putAll(JavaAudit.read(Paths.get(a[1])));String life="de.vw.mib.asl.internal.wcpcp.Mu1447Lifecycle";initMap.put(CP,mockInit(initMap.get(CP),false));initMap.put(life,mockInit(initMap.get(life),true));JavaAudit.Loader initLoader=new JavaAudit.Loader(initMap);Class<?> initCp=initLoader.loadClass(CP),initLife=initLoader.loadClass(life);set(initCp,"started",true);method(initLife,"run").invoke(null);check(tries>=3&&observerTries==2&&loops==1,"startup did not retry readiness/observer registration");check(!(Boolean)get(initCp,"started")&&!(Boolean)get(initCp,"active"),"startup latch stayed poisoned");set(initCp,"started",true);method(initLife,"run").invoke(null);check(loops==2&&!(Boolean)get(initCp,"started"),"second startup could not run");
  System.out.println("STARTUP=PASS delayed_locator observer_retry restartable_latch cleanup");
  System.out.println("TOUCH=PASS blocked_sender_does_not_block_input bounded_coalescing camera_gesture_handoff no_partial_OEM_gesture disable_fallback");
 }
}
