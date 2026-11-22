import java.nio.file.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class Normalize {
 public static void main(String[] args)throws Exception{for(String arg:args){Path p=Paths.get(arg);ClassNode c=new ClassNode();new ClassReader(Files.readAllBytes(p)).accept(c,ClassReader.SKIP_FRAMES);c.version=46;
  for(MethodNode m:c.methods)for(AbstractInsnNode n:m.instructions){
   if(n.getOpcode()==Opcodes.INVOKEDYNAMIC||n instanceof LdcInsnNode&&((LdcInsnNode)n).cst instanceof Type)throw new AssertionError("unsupported bytecode "+c.name);
   if(n instanceof TypeInsnNode&&((TypeInsnNode)n).desc.equals("java/lang/StringBuilder"))((TypeInsnNode)n).desc="java/lang/StringBuffer";
   if(n instanceof MethodInsnNode){MethodInsnNode x=(MethodInsnNode)n;if(x.owner.equals("java/lang/StringBuilder"))x.owner="java/lang/StringBuffer";x.desc=x.desc.replace("java/lang/StringBuilder","java/lang/StringBuffer");}
  }
  ClassWriter w=new ClassWriter(ClassWriter.COMPUTE_MAXS);c.accept(w);Files.write(p,w.toByteArray());}}
}
