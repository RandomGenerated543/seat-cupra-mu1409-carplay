import java.nio.file.*;import java.util.*;import java.util.zip.*;import org.objectweb.asm.*;import org.objectweb.asm.tree.*;
public class AbiChecks {
 static Map<String,byte[]> entries(Path p)throws Exception{Map<String,byte[]> m=new TreeMap<>();try(ZipFile z=new ZipFile(p.toFile())){Enumeration<? extends ZipEntry> e=z.entries();while(e.hasMoreElements()){ZipEntry n=e.nextElement();m.put(n.getName(),z.getInputStream(n).readAllBytes());}}return m;}
 static void check(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
 static ClassNode parse(byte[]b){ClassNode c=new ClassNode();new ClassReader(b).accept(c,ClassReader.SKIP_FRAMES);return c;}
 public static void main(String[] a)throws Exception{
  Path b=Paths.get(a[0]),old=Paths.get(a[1]),donor=Paths.get(a[2]);Map<String,byte[]> cp=entries(b.resolve("CP-fixed.jar")),original=entries(donor);
  for(String n:original.keySet())if(!n.endsWith("/WcpCp.class"))check(Arrays.equals(original.get(n),cp.get(n)),"unrelated CP entry changed "+n);
  Map<String,byte[]> outer=entries(b.resolve("Touch-runtime.jar")),prior=entries(old.resolve("CarPlayWireless-Touch-MU1447.jar"));String touch="de/vw/mib/asl/internal/system/input/TouchInputDeviceImpl.class";ClassNode before=parse(prior.get(touch)),after=parse(outer.get(touch));
  for(int i=0;i<before.methods.size();i++){MethodNode x=before.methods.get(i),y=after.methods.get(i);check(x.name.equals(y.name)&&x.desc.equals(y.desc),"OEM method signature changed");if(!x.name.equals("updateTouchInput")){ClassWriter wx=new ClassWriter(0),wy=new ClassWriter(0);ClassNode cx=new ClassNode(),cy=new ClassNode();before.accept(cx);after.accept(cy);cx.methods=Arrays.asList(x);cy.methods=Arrays.asList(y);cx.accept(wx);cy.accept(wy);check(Arrays.equals(wx.toByteArray(),wy.toByteArray()),"unrelated OEM method changed "+x.name);}}
  int classes=0;for(String jar:new String[]{"CP-fixed.jar","Touch-runtime.jar","Bootstrap-runtime.jar","link-check.jar"})for(Map.Entry<String,byte[]> e:entries(b.resolve(jar)).entrySet())if(e.getKey().endsWith(".class")){ClassNode c=parse(e.getValue());check(c.version==46,"wrong J9 class version "+c.name);for(MethodNode m:c.methods)for(AbstractInsnNode n:m.instructions){check(n.getOpcode()!=Opcodes.INVOKEDYNAMIC,"invokedynamic");check(!(n instanceof LdcInsnNode&&((LdcInsnNode)n).cst instanceof Type),"class literal "+c.name);if(n instanceof MethodInsnNode)check(!((MethodInsnNode)n).owner.equals("java/lang/StringBuilder"),"StringBuilder");}classes++;}
  System.out.println("ABI=PASS target_class_version=46 no_new_Java5_bytecode OEM_touch_methods_preserved unrelated_donor_entries_preserved classes="+classes);
 }
}
