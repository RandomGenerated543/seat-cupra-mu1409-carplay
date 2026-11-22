import java.nio.file.*;import java.util.*;import java.util.zip.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class Patch1447NativeTouch {
 public static void main(String[] a)throws Exception{
  ClassNode c=new ClassNode();new ClassReader(Files.readAllBytes(Paths.get(a[0]))).accept(c,ClassReader.SKIP_FRAMES);
  if(!c.name.equals("de/vw/mib/asl/internal/system/input/TouchInputDeviceImpl"))throw new AssertionError();
  int changed=0;
  for(MethodNode m:c.methods){
   for(AbstractInsnNode n:m.instructions){
    if(n.getOpcode()==Opcodes.INVOKEDYNAMIC || n instanceof LdcInsnNode&&((LdcInsnNode)n).cst instanceof Type)throw new AssertionError("newer bytecode cannot normalize");
   }
   if(m.name.equals("updateTouchInput")&&m.desc.equals("(IIIIIII)V")){
    InsnList x=new InsnList();for(int local:new int[]{1,3,4,5})x.add(new VarInsnNode(Opcodes.ILOAD,local));
    x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,"de/vw/mib/asl/internal/system/input/CpWcpTouch","onTouch","(IIII)Z",false));
    LabelNode original=new LabelNode();x.add(new JumpInsnNode(Opcodes.IFEQ,original));x.add(new InsnNode(Opcodes.RETURN));x.add(original);m.instructions.insert(x);changed++;
   }
  }
  if(changed!=1)throw new AssertionError();c.version=46;
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);byte[] replacement=w.toByteArray();
  try(ZipFile z=new ZipFile(a[1]);ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(Paths.get(a[2])))){
   Enumeration<? extends ZipEntry> entries=z.entries();while(entries.hasMoreElements()){
    ZipEntry e=entries.nextElement();out.putNextEntry(new ZipEntry(e.getName()));out.write(e.getName().equals(c.name+".class")?replacement:z.getInputStream(e).readAllBytes());out.closeEntry();
   }
  }
  System.out.println("MU1447_NATIVE_TOUCH=PASS OEM_methods_preserved=1 forwarding_site=1");
 }
}
