import java.nio.file.*;import java.lang.reflect.*;import java.util.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class StartupLatencyTests {
 static volatile boolean visible;static volatile Throwable failure;
 public static class Canvas {public boolean isCanvasVisible(){return visible;}}
 public static class Services {private Object properties=new Canvas();}
 public static class Api {public Object getServices(){return new Services();}}
 public static class Factory {public static Object get(){return new Api();}}
 static void check(boolean x,String why){if(!x)throw new AssertionError(why);}
 static byte[] boundary(byte[] bytes,boolean touch){ClassNode c=new ClassNode();new ClassReader(bytes).accept(c,ClassReader.SKIP_FRAMES);
  for(MethodNode m:c.methods){InsnList x=new InsnList();boolean replace=false;
   if(touch){if(m.name.equals("start")){x.add(new InsnNode(Opcodes.RETURN));replace=true;}}
   else if(Arrays.asList("drainQueue","maybeConfirmScreen","ensureOwnerMarker","maybeOemExit","maybeAudio","maybeDebugHmiEvent","maybeAutoFront","maybeBtDisable","maybeFrontReq","updateFgFlag").contains(m.name)){x.add(new InsnNode(Opcodes.RETURN));replace=true;}
   else if(m.name.equals("sessionFresh")){x.add(new InsnNode(Opcodes.ICONST_1));x.add(new InsnNode(Opcodes.IRETURN));replace=true;}
   else if(m.name.equals("maybeRegisterAndDrive")){x.add(new InsnNode(Opcodes.ICONST_1));x.add(new FieldInsnNode(Opcodes.PUTSTATIC,c.name,"weRegistered","Z"));x.add(new InsnNode(Opcodes.RETURN));replace=true;}
   if(replace)JavaAudit.replace(m,x);
  }ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 public static void main(String[]args)throws Exception{
  boolean slow=args.length>2;String cpName=RuntimeTests.CP,touchName=RuntimeTests.TOUCH;
  Map<String,byte[]> map=JavaAudit.read(Paths.get(args[0]));map.putAll(JavaAudit.read(Paths.get(args[1])));map.put(cpName,boundary(map.get(cpName),false));map.put(touchName,boundary(map.get(touchName),true));JavaAudit.Loader loader=new JavaAudit.Loader(map);
  Class cp=loader.loadClass(cpName),own=loader.loadClass(RuntimeTests.OWN),life=loader.loadClass("de.vw.mib.asl.internal.wcpcp.Mu1447Lifecycle");JavaAudit.field(cp,"stage",3);JavaAudit.field(cp,"mGetReceiverEventId",RuntimeTests.Event.class.getMethod("getReceiverEventId"));JavaAudit.field(cp,"mCanvasGetApi",Factory.class.getMethod("get"));Method loop=JavaAudit.method(cp,"loop"),ready=own.getMethod("canTouch");
  Path root=Files.createTempDirectory("mu1447-startup-latency-");System.setProperty("wcpcp.root",root.toString());
  Thread worker=new Thread(()->{try{loop.invoke(null);}catch(InvocationTargetException e){if(!(e.getCause() instanceof InterruptedException))failure=e.getCause();}catch(Throwable e){failure=e;}});worker.setDaemon(true);worker.start();
  long deadline=System.currentTimeMillis()+2000;while(worker.getState()!=Thread.State.TIMED_WAITING&&System.currentTimeMillis()<deadline)Thread.sleep(1);check(worker.getState()==Thread.State.TIMED_WAITING,"worker not at idle wait");check(!(Boolean)ready.invoke(null),"touch active before visible canvas");
  visible=true;long start=System.nanoTime();JavaAudit.method(cp,"onObserverEvent",Object.class).invoke(null,new RuntimeTests.Event(6100008));
  deadline=System.currentTimeMillis()+1600;while(!(Boolean)ready.invoke(null)&&System.currentTimeMillis()<deadline)Thread.sleep(1);long elapsed=(System.nanoTime()-start)/1000000L;check((Boolean)ready.invoke(null),"visible event did not enable touch");worker.interrupt();worker.join(1000);check(!worker.isAlive()&&failure==null,"worker failed or leaked");
  if(slow)check(elapsed>=500,"old polling delay not reproduced");else{
   check(elapsed<250,"event wake still waits for idle timer");Object lock=JavaAudit.get(cp,"LOCK");synchronized(lock){life.getMethod("beginTurn").invoke(null);life.getMethod("signalScreen").invoke(null);start=System.nanoTime();life.getMethod("awaitEvents",Object.class,long.class).invoke(null,lock,1000L);check((System.nanoTime()-start)/1000000<250,"notification lost before wait");life.getMethod("beginTurn").invoke(null);start=System.nanoTime();life.getMethod("awaitEvents",Object.class,long.class).invoke(null,lock,30L);check((System.nanoTime()-start)/1000000>=20,"idle wait changed to busy loop");}
  }
  System.out.println((slow?"OLD_STARTUP_DELAY_REPRODUCED":"STARTUP_WAKE=PASS")+" host_ready_delay_ms="+elapsed+(slow?"":" no_lost_notification unchanged_idle_wait"));
 }
}
