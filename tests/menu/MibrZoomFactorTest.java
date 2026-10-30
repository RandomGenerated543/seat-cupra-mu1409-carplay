package de.mibr.hmi;
public final class MibrZoomFactorTest {
 public static void main(String[] args){
  int id=MibrV3Protocol.index("display.zoomFactor");
  if(id<0 || !MibrPopupEditorModel.visible(id) || !MibrPopupEditorModel.saveAllowed(id))throw new RuntimeException("MENU_NOT_WRITABLE");
  MibrDraftChoiceModel d=new MibrDraftChoiceModel(id);
  if(!"70%".equals(d.labelFor("70")) || !"150%".equals(d.labelFor("150")))throw new RuntimeException("PERCENT_LABEL");
  if(d.chooseDraft("20") || d.chooseDraft("69") || d.chooseDraft("151") || d.chooseDraft("70%"))throw new RuntimeException("BOUNDS");
  if(!d.chooseDraft("70") || !d.chooseDraft("150"))throw new RuntimeException("CHOICES");
  if(!"reconnect".equals(MibrSettingsCatalog.APPLY[id]))throw new RuntimeException("WRONG_APPLY_CLASS");
  if(MibrSettingsCatalog.KEYS.length!=49 || MibrSettingsCatalog.READ_ONLY.length!=49 || MibrMenuDefinition.NATIVE_UI_KEYS.length!=12)throw new RuntimeException("SCHEMA_DRIFT");
  System.out.println("ZOOM_MENU=PASS percentage_labels bounds writable restart_class schema49");
 }
}
