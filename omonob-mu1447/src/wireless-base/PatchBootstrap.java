import java.nio.file.*;import java.util.*;import java.util.zip.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class PatchBootstrap {
 public static void main(String[] a)throws Exception{
  try(ZipFile z=new ZipFile(a[0]);ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(Paths.get(a[1])))){
   Enumeration<? extends ZipEntry> es=z.entries();int hits=0;
   while(es.hasMoreElements()){
    ZipEntry e=es.nextElement();byte[] b=z.getInputStream(e).readAllBytes();
    if(e.getName().endsWith("WirelessMapsBootstrap.class")){
     ClassNode c=new ClassNode();new ClassReader(b).accept(c,0);
     for(MethodNode m:c.methods)if(m.name.equals("start"))for(AbstractInsnNode n:m.instructions.toArray()){
      if(n instanceof MethodInsnNode&&((MethodInsnNode)n).owner.equals("org/omonob/phone/PhoneConnectionRuntime")&&((MethodInsnNode)n).name.equals("start")){
       InsnList x=new InsnList();for(String owner:new String[]{"de/vw/mib/asl/internal/wcpsi/WcpSi","de/vw/mib/asl/internal/wcpcp/WcpCp"})x.add(new MethodInsnNode(Opcodes.INVOKESTATIC,owner,"start","()V",false));
       m.instructions.insert(n,x);hits++;
      }
     }
     ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);b=w.toByteArray();
    }
    out.putNextEntry(new ZipEntry(e.getName()));out.write(b);out.closeEntry();
   }
   if(hits!=1)throw new AssertionError("startup_sites="+hits);
  }
  System.out.println("BOOTSTRAP=PASS explicit_phone_and_carplay_bridges_start_idempotently");
 }
}
