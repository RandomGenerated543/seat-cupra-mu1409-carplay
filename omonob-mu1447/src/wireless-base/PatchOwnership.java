import java.nio.file.*;import java.util.*;import java.util.zip.*;import java.io.*;
import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class PatchOwnership {
 static final String HELPER="de/vw/mib/asl/internal/wcpcp/Mu1447ScreenOwnership";
 static InsnList call(String method,String desc){InsnList x=new InsnList();x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,HELPER,method,desc,false));return x;}
 static byte[] patch(String entry,byte[] bytes){
  ClassNode c=new ClassNode();new ClassReader(bytes).accept(c,0);
  if(c.version!=46)throw new IllegalStateException("unexpected class version "+c.version);
  int changes=0;
  for(MethodNode m:c.methods){
   if(c.name.endsWith("/WcpCp")){
    if(m.name.equals("trackScreen")){
     int hits=0;boolean pending=false;
     for(AbstractInsnNode n:m.instructions.toArray()){
      if(n instanceof LdcInsnNode && "transferType".equals(((LdcInsnNode)n).cst))pending=true;
      if(pending && n instanceof MethodInsnNode && ((MethodInsnNode)n).name.equals("intField")){
       InsnList x=new InsnList();x.add(new InsnNode(Opcodes.DUP));x.add(call("onTransfer","(I)V"));m.instructions.insert(n,x);pending=false;hits++;
      }
     }
     if(hits!=1)throw new IllegalStateException("transfer sites "+hits);changes++;
    }
    if(m.name.equals("onObserverEvent")){
     int hits=0;for(AbstractInsnNode n:m.instructions.toArray()){
      if(n instanceof MethodInsnNode && ((MethodInsnNode)n).name.equals("intOf")){
       InsnList x=new InsnList();x.add(new InsnNode(Opcodes.DUP));x.add(call("onObserver","(I)V"));m.instructions.insert(n,x);hits++;
      }
     }
     if(hits!=1)throw new IllegalStateException("observer sites "+hits);changes++;
    }
    if(m.name.equals("syncCanvas")){
     InsnList x=call("isBlocked","()Z");LabelNode allow=new LabelNode();x.add(new JumpInsnNode(Opcodes.IFEQ,allow));x.add(new InsnNode(Opcodes.ICONST_0));x.add(new FieldInsnNode(Opcodes.PUTSTATIC,c.name,"fgCarplay","Z"));x.add(new InsnNode(Opcodes.RETURN));x.add(allow);m.instructions.insert(x);changes++;
    }
    if(m.name.equals("updateFgFlag")){
     InsnList x=call("isBlocked","()Z");LabelNode allow=new LabelNode();x.add(new JumpInsnNode(Opcodes.IFEQ,allow));x.add(new InsnNode(Opcodes.ICONST_0));x.add(new FieldInsnNode(Opcodes.PUTSTATIC,c.name,"fgCarplay","Z"));x.add(allow);m.instructions.insert(x);changes++;
    }
    if(m.name.equals("onSessionDown")){m.instructions.insert(call("reset","()V"));changes++;}
   }else if(c.name.endsWith("/CpWcpTouch") && m.name.equals("onTouch")){
    InsnList x=call("isBlocked","()Z");LabelNode allow=new LabelNode();x.add(new JumpInsnNode(Opcodes.IFEQ,allow));
    for(String field:new String[]{"gestureOpen","toCarPlay"}){x.add(new InsnNode(Opcodes.ICONST_0));x.add(new FieldInsnNode(Opcodes.PUTSTATIC,c.name,field,"Z"));}
    x.add(new InsnNode(Opcodes.ICONST_0));x.add(new InsnNode(Opcodes.IRETURN));x.add(allow);m.instructions.insert(x);changes++;
   }
  }
  int expected=c.name.endsWith("/WcpCp")?5:c.name.endsWith("/CpWcpTouch")?1:0;
  if(changes!=expected)throw new IllegalStateException("patch count "+c.name+"="+changes);
  if(changes==0)return bytes;
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);return w.toByteArray();
 }
 public static void main(String[] a)throws Exception{
  if(a[0].equals("--normalize")){ClassNode c=new ClassNode();new ClassReader(Files.readAllBytes(Paths.get(a[1]))).accept(c,ClassReader.SKIP_FRAMES);c.version=46;ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);Files.write(Paths.get(a[1]),w.toByteArray());return;}
  try(ZipFile input=new ZipFile(a[0]);ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(Paths.get(a[1])))){
   Enumeration<? extends ZipEntry> es=input.entries();while(es.hasMoreElements()){
    ZipEntry e=es.nextElement();byte[] b=input.getInputStream(e).readAllBytes();
    if(e.getName().endsWith("WcpCp.class")||e.getName().endsWith("CpWcpTouch.class"))b=patch(e.getName(),b);
    out.putNextEntry(new ZipEntry(e.getName()));out.write(b);out.closeEntry();
   }
   if(a.length==3){out.putNextEntry(new ZipEntry(HELPER+".class"));out.write(Files.readAllBytes(Paths.get(a[2])));out.closeEntry();}
  }
 }
}
