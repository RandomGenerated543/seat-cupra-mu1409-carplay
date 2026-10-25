package de.mibr.hmi;
/** Standalone verification only: no menu activation or production controls. */
public final class MibrR13MigrationProbe {
 public static void main(String[] args)throws Exception{
  if(MibrSettingsCatalog.KEYS.length!=48)throw new IllegalStateException("CATALOG");
  int view=-1;for(int i=0;i<MibrSettingsCatalog.KEYS.length;i++)if("viewarea.selected".equals(MibrSettingsCatalog.KEYS[i]))view=i;
  if(view<0||new MibrDraftChoiceModel(view).options().length!=3)throw new IllegalStateException("THREE_VIEW_CHOICES");
  if(!"leftAligned".equals(MibrV3Protocol.decode(MibrV3Protocol.encode("leftAligned"))))throw new IllegalStateException("PROTOCOL");
  if(args.length==1&&"--oem-link".equals(args[0])){
   String[] names={"de.vw.mib.cio.internal.Activator","generated.de.vw.mib.global.view.internal.WidgetFactoryImpl","de.mibr.hmi.MibrHomeList","de.mibr.hmi.MibrSsmNativePage","de.mibr.hmi.MibrOwnedSsmRows","de.mibr.hmi.MibrNativeDropdownEditor","de.mibr.hmi.MibrV3Client"};
   for(int i=0;i<names.length;i++){Class c=Class.forName(names[i],false,MibrR13MigrationProbe.class.getClassLoader());c.getDeclaredMethods();c.getDeclaredConstructors();}
  }
  System.out.println("R13_MIGRATION_J9_PROBE=PASS catalog=48 offered_views=3 controls_invoked=0");
 }
}
