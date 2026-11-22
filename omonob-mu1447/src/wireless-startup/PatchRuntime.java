import java.nio.file.*;import java.util.*;import java.util.zip.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class PatchRuntime {
 static final String CP="de/vw/mib/asl/internal/wcpcp/WcpCp",OWN="de/vw/mib/asl/internal/wcpcp/Mu1447ScreenOwnership",LIFE="de/vw/mib/asl/internal/wcpcp/Mu1447Lifecycle",HEALTH="de/vw/mib/asl/internal/wcpcp/Mu1447SessionHealth";
 static final Set<String> fields=new HashSet<>(Arrays.asList("LOCK","started","active","stage","fakeAddr","locator","observerRegistered","observerTargetId","serviceRegister","dispatcher","cpInterface","sessionLive","weRegistered","fgCarplay"));
 static final Set<String> methods=new HashSet<>(Arrays.asList("<init>","log2","readStage","readAddr","waitLocator","resolve","registerObserver","unregisterService","clearOwnerMarker","loop"));
 static void body(MethodNode m,String owner,String method){m.instructions.clear();m.tryCatchBlocks.clear();if(m.localVariables!=null)m.localVariables.clear();m.instructions.add(new MethodInsnNode(Opcodes.INVOKESTATIC,owner,method,"()V",false));m.instructions.add(new InsnNode(Opcodes.RETURN));}
 static InsnList call(String owner,String name,String desc){InsnList x=new InsnList();x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,owner,name,desc,false));return x;}
 static byte[] cp(byte[] b,boolean prepare){
  ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);if(!c.name.equals(CP)||c.version!=46)throw new AssertionError();
  for(FieldNode f:c.fields)if(fields.contains(f.name))f.access&=~Opcodes.ACC_PRIVATE;
  int targetSites=0,observerSites=0,tickSites=0,healthSites=0,waitSites=0,turnSites=0,signalSites=0;
  for(MethodNode m:c.methods){
   if(methods.contains(m.name))m.access&=~Opcodes.ACC_PRIVATE;
   if(prepare)continue;
   if(m.name.equals("start")||m.name.equals("run")){body(m,LIFE,m.name);continue;}
   if(m.name.equals("trackScreen")){
    boolean found=false;int hits=0;for(AbstractInsnNode n:m.instructions.toArray()){
     if(n instanceof LdcInsnNode&&"transferType".equals(((LdcInsnNode)n).cst))found=true;
     if(found&&n instanceof MethodInsnNode&&((MethodInsnNode)n).name.equals("intField")){InsnList x=new InsnList();x.add(new InsnNode(Opcodes.DUP));x.add(call(OWN,"onTransfer","(I)V"));m.instructions.insert(n,x);found=false;hits++;}
    }if(hits!=1)throw new AssertionError("transfer");
   }
   if(m.name.equals("onObserverEvent")){int hits=0;for(AbstractInsnNode n:m.instructions.toArray())if(n instanceof MethodInsnNode&&((MethodInsnNode)n).name.equals("intOf")){InsnList x=new InsnList();x.add(new InsnNode(Opcodes.DUP));x.add(call(OWN,"onObserver","(I)V"));m.instructions.insert(n,x);hits++;}if(hits!=1)throw new AssertionError("observer");}
   if(m.name.equals("onObserverEvent")||m.name.equals("onServiceCall")){
    for(AbstractInsnNode n:m.instructions.toArray())if(n.getOpcode()==Opcodes.RETURN){m.instructions.insertBefore(n,call(LIFE,"signalScreen","()V"));signalSites++;}
   }
   if(m.name.equals("onServiceCall")){InsnList x=new InsnList();x.add(new VarInsnNode(Opcodes.ALOAD,0));x.add(call(OWN,"onService","(Ljava/lang/String;)V"));m.instructions.insert(x);}
   if(m.name.equals("sendUpdateMode")){
    InsnList x=new InsnList();LabelNode allow=new LabelNode();x.add(new VarInsnNode(Opcodes.ILOAD,0));x.add(new JumpInsnNode(Opcodes.IFEQ,allow));x.add(call(OWN,"isBlocked","()Z"));x.add(new JumpInsnNode(Opcodes.IFEQ,allow));x.add(new InsnNode(Opcodes.ICONST_1));x.add(new FieldInsnNode(Opcodes.PUTSTATIC,CP,"confirmScreen","Z"));x.add(new InsnNode(Opcodes.RETURN));x.add(allow);m.instructions.insert(x);
   }
   if(m.name.equals("maybeAutoFront")){InsnList x=call(OWN,"allowAutomaticFront","()Z");LabelNode allow=new LabelNode();x.add(new JumpInsnNode(Opcodes.IFNE,allow));x.add(new InsnNode(Opcodes.RETURN));x.add(allow);m.instructions.insert(x);}
   if(m.name.equals("onSessionDown"))for(AbstractInsnNode n:m.instructions.toArray())if(n.getOpcode()==Opcodes.RETURN)m.instructions.insertBefore(n,call(OWN,"sessionDown","()V"));
   if(m.name.equals("unregisterService"))m.instructions.insert(call(OWN,"sessionDown","()V"));
   if(m.name.equals("sessionFresh"))for(AbstractInsnNode n:m.instructions.toArray())if(n.getOpcode()==Opcodes.IRETURN){m.instructions.insertBefore(n,call(HEALTH,"observe","(Z)Z"));healthSites++;}
   if(m.name.equals("loop")){
    for(AbstractInsnNode n:m.instructions.toArray())if(n instanceof MethodInsnNode){MethodInsnNode invoke=(MethodInsnNode)n;
     if(invoke.owner.equals(CP)&&invoke.name.equals("drainQueue")){m.instructions.insertBefore(n,call(LIFE,"beginTurn","()V"));turnSites++;}
     if(invoke.owner.equals("java/lang/Object")&&invoke.name.equals("wait")&&invoke.desc.equals("(J)V")){m.instructions.set(n,new MethodInsnNode(Opcodes.INVOKESTATIC,LIFE,"awaitEvents","(Ljava/lang/Object;J)V",false));waitSites++;}
    }
   }
   if(m.name.equals("loop"))for(AbstractInsnNode n:m.instructions.toArray())if(n instanceof MethodInsnNode&&((MethodInsnNode)n).name.equals("updateFgFlag")){m.instructions.insert(n,call(LIFE,"tick","()V"));tickSites++;}
   if(m.name.equals("registerObserver"))for(AbstractInsnNode n:m.instructions.toArray())if(n instanceof MethodInsnNode&&((MethodInsnNode)n).owner.equals("java/lang/reflect/Method")&&((MethodInsnNode)n).name.equals("invoke")){
    // Identify reflective invocations by the preceding field load, not all Method.invoke calls.
    AbstractInsnNode p=n.getPrevious();boolean target=false,observers=false;for(int i=0;p!=null&&i<40;i++,p=p.getPrevious())if(p instanceof FieldInsnNode){String name=((FieldInsnNode)p).name;if(name.equals("mRegisterTarget")){target=true;break;}if(name.equals("mAddObserver")){observers=true;break;}if(name.equals("mGetReceiverEventId"))break;}
    if(target||observers){if(target)targetSites++;else observerSites++;m.instructions.set(n,new MethodInsnNode(Opcodes.INVOKESTATIC,LIFE,target?"registerTarget":"addObservers","(Ljava/lang/reflect/Method;Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;",false));}
   }
   for(AbstractInsnNode n:m.instructions.toArray()){
    if(n instanceof FieldInsnNode&&n.getOpcode()==Opcodes.PUTSTATIC&&((FieldInsnNode)n).name.equals("fgCarplay"))m.instructions.insertBefore(n,call(OWN,"clampForeground","(Z)Z"));
    if(m.name.equals("syncCanvas")&&n instanceof MethodInsnNode&&((MethodInsnNode)n).name.equals("booleanValue"))m.instructions.insert(n,call(OWN,"clampForeground","(Z)Z"));
   }
  }
  if(!prepare&&(targetSites!=1||observerSites!=1||tickSites!=1||healthSites!=1||waitSites!=1||turnSites!=1||signalSites<2))throw new AssertionError("sites target="+targetSites+" observer="+observerSites+" tick="+tickSites+" health="+healthSites);
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 public static void main(String[] a)throws Exception{
  boolean prepare=a[0].equals("prepare");try(ZipFile z=new ZipFile(a[1]);ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(Paths.get(a[2])))){
   Enumeration<? extends ZipEntry> e=z.entries();while(e.hasMoreElements()){ZipEntry n=e.nextElement();byte[] b=z.getInputStream(n).readAllBytes();if(n.getName().equals(CP+".class"))b=cp(b,prepare);out.putNextEntry(new ZipEntry(n.getName()));out.write(b);out.closeEntry();}
   if(!prepare){Path dir=Paths.get(a[3]);try(java.util.stream.Stream<Path> paths=Files.walk(dir)){for(Path p:(Iterable<Path>)paths.filter(x->x.toString().endsWith(".class"))::iterator){String name=dir.relativize(p).toString().replace('\\','/');if(!name.startsWith("de/vw/mib/asl/internal/wcpcp/Mu1447"))continue;out.putNextEntry(new ZipEntry(name));out.write(Files.readAllBytes(p));out.closeEntry();}}}
  }
 }
}
