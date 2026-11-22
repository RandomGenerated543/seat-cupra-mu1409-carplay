import java.nio.file.*;import java.util.*;import java.util.zip.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class PatchTouchBootstrap {
 public static void main(String[] a)throws Exception{boolean bootstrap=a[0].equals("bootstrap");int hits=0;
 try(ZipFile z=new ZipFile(a[1]);ZipOutputStream out=new ZipOutputStream(Files.newOutputStream(Paths.get(a[2])))){
  Enumeration<? extends ZipEntry> e=z.entries();while(e.hasMoreElements()){
   ZipEntry n=e.nextElement();byte[] b=z.getInputStream(n).readAllBytes();
   if(n.getName().endsWith(bootstrap?"WirelessMapsBootstrap.class":"TouchInputDeviceImpl.class")){
    ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);
    for(MethodNode m:c.methods)for(AbstractInsnNode ins:m.instructions.toArray())if(ins instanceof MethodInsnNode){MethodInsnNode call=(MethodInsnNode)ins;
     if(bootstrap&&m.name.equals("start")&&call.owner.equals("de/vw/mib/asl/internal/wcpcp/WcpCp")&&call.name.equals("start")){m.instructions.insertBefore(ins,new MethodInsnNode(Opcodes.INVOKESTATIC,"de/vw/mib/asl/internal/system/input/CpWcpTouch","start","()V",false));hits++;}
     if(!bootstrap&&m.name.equals("updateTouchInput")&&call.name.equals("onTouch")){
      AbstractInsnNode first=ins;for(int i=0;i<4;i++)first=first.getPrevious();
      JumpInsnNode decision=(JumpInsnNode)ins.getNext();LabelNode start=new LabelNode(),end=new LabelNode(),handler=new LabelNode();m.instructions.insertBefore(first,start);m.instructions.insert(ins,end);
      InsnList fallback=new InsnList();fallback.add(handler);fallback.add(new InsnNode(Opcodes.POP));fallback.add(new JumpInsnNode(Opcodes.GOTO,decision.label));m.instructions.add(fallback);m.tryCatchBlocks.add(new TryCatchBlockNode(start,end,handler,"java/lang/Throwable"));hits++;
     }
    }
    ClassWriter outClass=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(outClass);b=outClass.toByteArray();
   }
   out.putNextEntry(new ZipEntry(n.getName()));out.write(b);out.closeEntry();
  }
 }
 if(hits!=1)throw new AssertionError("patch sites="+hits);System.out.println("PATCH="+a[0]+" sites=1");
 }
}
