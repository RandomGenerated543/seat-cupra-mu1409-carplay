package de.mibr.hmi;
import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintStream;
import de.vw.mib.widgets.DropDownButton;
import de.vw.mib.widgets.TextArea;
import de.vw.mib.widgets.models.WidgetModel;
/** Bounded RAM-only observer. No widget, settings or production control writes. */
final class MibrDropdownTrace {
 private MibrDropdownTrace(){}
 private static String type(Object o){return o==null?"null":o.getClass().getName();}
 private static void widget(PrintStream p,String label,WidgetModel w){
  if(w==null){p.println(label+"=null");return;}
  p.println(label+".class="+type(w)+" xy="+w.get_x()+","+w.get_y()+" size="+w.get_width()+"x"+w.get_height());
 }
 static synchronized void record(String stage,Throwable failure,MibrOemSsmTemplate.Binding stock,Object button,int key){
  PrintStream out=null;
  try{
   File file=new File("/tmp/mibr-seat-dropdown.log");
   out=new PrintStream(new FileOutputStream(file.getPath(),file.length()<65536));
   out.println("DROPDOWN_TRACE=v2 time_ms="+System.currentTimeMillis()+" stage="+stage+" key="+key);
   out.println("button.class="+type(button));
   if(stock!=null){
    widget(out,"view",stock.view);widget(out,"popup",stock.popup);widget(out,"options",stock.options);widget(out,"option",stock.option);
    out.println("popup.option_chrome="+(stock.popup.get_height()-stock.options.get_height()));
    de.vw.mib.properties.values.LayoutAttribs frame=stock.popup.get_layoutAttribs();
    out.println("native.frame_insets="+(frame==null?0:frame.getInsetTop())+","+(frame==null?0:frame.getInsetBottom()));
    if(button instanceof DropDownButton){
     DropDownButton d=(DropDownButton)button;
     out.println("controller.class="+type(d.getController())+" dropdown_ref_matches="+(d.get_dropDownRef()==stock.popup)+" inactive_ref_null="+(d.get_inactiveAreaRef()==null));
    }
    try{
     TextArea sample=(TextArea)MibrOemSsmTemplate.target(stock.option,MibrOemSsmTemplate.OPTION_TEXT_TARGET_ID,TextArea.class);
     widget(out,"sample",sample);out.println("sample.font_null="+(sample.get_font()==null));
    }catch(Throwable probe){out.println("sample.probe_error="+probe);}
   }
   if(failure!=null)failure.printStackTrace(out);
   out.println("DROPDOWN_TRACE_END");
  }catch(Throwable ignored){}finally{if(out!=null)try{out.close();}catch(Throwable ignored){}}
 }
}
