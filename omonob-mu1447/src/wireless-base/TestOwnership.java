import java.lang.reflect.*;import java.nio.file.*;
import de.vw.mib.asl.internal.wcpcp.Mu1447ScreenOwnership;
public class TestOwnership {
 public static final class Resource {public int resourceID=2,transferType;Resource(int t){transferType=t;}}
 static Class<?> cp;static Method track,sync;static Field fg,stage;
 static void transfer(int t)throws Exception{track.invoke(null,new Object[]{new Object[]{new Object[]{new Resource(t)}}});}
 static void blocked()throws Exception{
  if(!Mu1447ScreenOwnership.isBlocked())throw new AssertionError();
  fg.setBoolean(null,true);sync.invoke(null);
  if(fg.getBoolean(null))throw new AssertionError("canvas reclaimed touch while borrowed");
  Class<?> touch=Class.forName("de.vw.mib.asl.internal.system.input.CpWcpTouch");
  Object r=touch.getMethod("onTouch",int.class,int.class,int.class,int.class).invoke(null,4,100,100,0);
  if(!Boolean.FALSE.equals(r))throw new AssertionError("popup touch swallowed");
 }
 public static void main(String[] a)throws Exception{
  Path root=Files.createTempDirectory("mu1447-screen-");System.setProperty("wcpcp.root",root.toString());Files.createDirectories(root.resolve("dev/shmem"));
  cp=Class.forName("de.vw.mib.asl.internal.wcpcp.WcpCp");
  track=cp.getDeclaredMethod("trackScreen",Object[].class);track.setAccessible(true);
  sync=cp.getDeclaredMethod("syncCanvas");sync.setAccessible(true);
  fg=cp.getDeclaredField("fgCarplay");fg.setAccessible(true);stage=cp.getDeclaredField("stage");stage.setAccessible(true);stage.setInt(null,3);
  Mu1447ScreenOwnership.reset();transfer(3);blocked();transfer(2);blocked();transfer(4);
  if(Mu1447ScreenOwnership.isBlocked())throw new AssertionError("unborrow did not release");
  transfer(1);transfer(3);blocked();transfer(4);blocked();transfer(2);
  if(Mu1447ScreenOwnership.isBlocked())throw new AssertionError("untake did not release");
  transfer(1);Mu1447ScreenOwnership.onObserver(6100008);
  if(Mu1447ScreenOwnership.isBlocked())throw new AssertionError("explicit return stuck");
  transfer(3);Mu1447ScreenOwnership.onObserver(6100008);blocked();
  Mu1447ScreenOwnership.reset();if(Mu1447ScreenOwnership.isBlocked())throw new AssertionError();
  System.out.println("PATCHED_JAVA=PASS camera_borrow_stale_canvas touch_to_HMI independent_take_borrow explicit_return session_reset class_verification");
 }
}
