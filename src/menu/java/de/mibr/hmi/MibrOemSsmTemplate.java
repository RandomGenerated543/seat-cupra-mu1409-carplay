package de.mibr.hmi;

import de.vw.mib.widgets.Button;
import de.vw.mib.widgets.TextArea;
import de.vw.mib.widgets.DropDown;
import de.vw.mib.widgets.DropDownButton;
import de.vw.mib.widgets.ListItem;
import de.vw.mib.widgets.WidgetList;
import de.vw.mib.widgets.models.ContainerModel;
import de.vw.mib.widgets.models.ViewModel;
import de.vw.mib.widgets.models.WidgetModel;

/**
 * Non-mutating exact-MU1409 Seat stock setup template discovery.
 * Source: decoded original skin1/skin4/skin5 Ssm_5458.java:
 * getName=SMI_SETUP_MAIN, internal view id 957, root targetId 24786208,
 * SelectDevice (PLAIN),
 * ConnectionType (VALUE/dropdown) and ExternalApps (CHECK) masters. The CHECK
 * row is the stock checkbox row of the same view (image arrays 147/686/1365,
 * ImageGlowContainer); no state images are grafted from another view.
 * This is not a HOME GridMenu or a page launcher.
 *
 * The owned ViewHandler host first creates a separate Ssm through its stock
 * lifecycle, then calls inspect(handler.getView()). Only that isolated instance
 * is adapted; its widgets are never attached to Sgm or to another stock Ssm.
 */
public final class MibrOemSsmTemplate {
    public static final int ROOT_TARGET_ID=24786208;
    public static final int INTERNAL_VIEW_ID=957;
    public static final String VIEW_NAME="SMI_SETUP_MAIN";
    public static final String ROW_PLAIN="SelectDevice";
    public static final String ROW_VALUE="ConnectionType";
    public static final String ROW_CHECK="ExternalApps";
    // ORIGINAL MU1409 Seat Ssm skin1/skin4/skin5; no Skoda donor view.
    public static final int MAIN_LIST_TARGET_ID=47234883;
    public static final int PLAIN_TARGET_ID=120460962;
    public static final int VALUE_TARGET_ID=53708779;
    public static final int OPENER_TARGET_ID=40267630;
    public static final int POPUP_TARGET_ID=86648370;
    public static final int TITLE_TARGET_ID=76384521;
    public static final int CLOSE_TARGET_ID=18238209;
    public static final int OPTION_LIST_TARGET_ID=45796615;
    public static final int OPTION_TARGET_ID=37984426;
    public static final int OPTION_TEXT_TARGET_ID=47818560;
    public static final int PLAIN_BUTTON_TARGET_ID=4894361;
    public static final int PLAIN_TEXT_TARGET_ID=101603979;
    public static final int VALUE_TEXT_TARGET_ID=70740890;
    public static final int VALUE_LABEL_TARGET_ID=64398879;
    // ExternalApps clone master (root level index 14), identical in Seat skins1/4/5.
    public static final int CHECK_TARGET_ID=19737792;
    public static final int CHECK_BUTTON_TARGET_ID=103710118;
    public static final int CHECK_TEXT_TARGET_ID=119782300;

    public static final class Binding {
        MibrScrollIndicator indicator;
        public final ViewModel view;
        public final ListItem plain;
        public final ListItem value;
        public final ListItem check;
        public final DropDownButton opener;
        public final DropDown popup;
        public final WidgetList mainList;
        public final TextArea title;
        public final Button close;
        public final WidgetList options;
        public final ListItem option;
        Binding(ViewModel v,ListItem p,ListItem x,ListItem k,DropDownButton b,DropDown d,
                WidgetList l,TextArea t,Button c,WidgetList o,ListItem i) {
            view=v; plain=p; value=x; check=k; opener=b; popup=d;
            mainList=l; title=t; close=c;
            options=o; option=i;
        }
    }

    static WidgetModel target(WidgetModel root,int id,Class type) {
        WidgetModel value=uniqueTarget(root,id,type,0);
        if(value==null)throw new IllegalStateException("MIBR_SSM_TARGET_MISSING "+id);
        return value;
    }

    private MibrOemSsmTemplate() { }

    private static WidgetModel unique(WidgetModel root,String name,Class type,int depth) {
        if(root==null || depth>15)return null;
        WidgetModel found=type.isInstance(root) && name.equals(root.get_name())?root:null;
        if(root instanceof ContainerModel) {
            WidgetModel[] children=((ContainerModel)root).getChildren();
            for(int i=0;children!=null && i<children.length;i++) {
                WidgetModel next=unique(children[i],name,type,depth+1);
                if(next!=null) {
                    if(found!=null) throw new IllegalStateException("MIBR_SSM_TEMPLATE_DUPLICATE "+name);
                    found=next;
                }
            }
        }
        return found;
    }

    // There are TWO native dropdowns in Ssm: type-only first() is ambiguous.
    private static WidgetModel uniqueTarget(WidgetModel root,int target,Class type,int depth) {
        if(root==null || depth>15)return null;
        WidgetModel found=type.isInstance(root) && root.get_targetId()==target?root:null;
        if(root instanceof ContainerModel) {
            WidgetModel[] children=((ContainerModel)root).getChildren();
            for(int i=0;children!=null && i<children.length;i++) {
                WidgetModel next=uniqueTarget(children[i],target,type,depth+1);
                if(next!=null) {
                    if(found!=null)throw new IllegalStateException("MIBR_SSM_DUPLICATE_TARGET "+target);
                    found=next;
                }
            }
        }
        return found;
    }

    public static final int SCROLLBAR_TARGET_ID=66092760;

    private static WidgetModel find(WidgetModel root,int target,int depth) {
        if(root==null || depth>15)return null;
        if(root.get_targetId()==target)return root;
        if(root instanceof ContainerModel) {
            WidgetModel[] children=((ContainerModel)root).getChildren();
            for(int i=0;children!=null && i<children.length;i++) {
                WidgetModel next=find(children[i],target,depth+1);
                if(next!=null)return next;
            }
        }
        return null;
    }

    /**
     * Keep the stock Ssm_5458 scrollbar bound to the ONE owned main WidgetList.
     * A full row replacement needs a detach/attach AFTER the list has finished
     * restoring selection and viewport. A data-only refresh must not briefly
     * detach the bar (the former white/green right-edge flicker).
     *
     * This is a source-level candidate until the exact installed OEM setter,
     * list viewport and paint ordering have been observed on the parked unit.
     * Never swallow a failed binding or invent another scrollbar widget.
     */
    public static boolean syncScrollbar(Binding b,boolean replaced) {
        try {
            // This target's live owned tree was observed without a native bar.
            // Restore the original project-owned indicator once per page binding.
            if(b.indicator==null)b.indicator=MibrScrollIndicator.attach(b.mainList,b.view);
            else b.indicator.update();
            if(b.indicator==null)return false;
            return true;
        }catch(Throwable failure){
            MibrSsmScrollbar.failure(failure);
            return false;
        }
    }

    static void diag(String value){MibrSsmScrollbar.record(value);}
    public static Binding inspect(ViewModel view) {
        if(view==null || !VIEW_NAME.equals(view.get_name()) ||
            view.get_targetId()!=ROOT_TARGET_ID) return null;
        ListItem plain=(ListItem)unique(view,ROW_PLAIN,ListItem.class,0);
        ListItem value=(ListItem)unique(view,ROW_VALUE,ListItem.class,0);
        ListItem check=(ListItem)unique(view,ROW_CHECK,ListItem.class,0);
        if(plain==null || value==null || check==null ||
            plain.get_targetId()!=PLAIN_TARGET_ID ||
            value.get_targetId()!=VALUE_TARGET_ID ||
            check.get_targetId()!=CHECK_TARGET_ID)return null;
        WidgetList list=(WidgetList)uniqueTarget(view,MAIN_LIST_TARGET_ID,WidgetList.class,0);
        DropDownButton opener=(DropDownButton)uniqueTarget(value,OPENER_TARGET_ID,DropDownButton.class,0);
        DropDown popup=(DropDown)uniqueTarget(view,POPUP_TARGET_ID,DropDown.class,0);
        TextArea title=(TextArea)uniqueTarget(view,TITLE_TARGET_ID,TextArea.class,0);
        Button close=(Button)uniqueTarget(view,CLOSE_TARGET_ID,Button.class,0);
        WidgetList options=(WidgetList)uniqueTarget(popup,OPTION_LIST_TARGET_ID,WidgetList.class,0);
        ListItem option=(ListItem)uniqueTarget(options,OPTION_TARGET_ID,ListItem.class,0);
        if(list==null || opener==null || popup==null || title==null || close==null ||
                options==null || option==null)return null;
        target(option,OPTION_TEXT_TARGET_ID,TextArea.class);
        target(plain,PLAIN_BUTTON_TARGET_ID,Button.class);
        target(plain,PLAIN_TEXT_TARGET_ID,TextArea.class);
        target(value,VALUE_LABEL_TARGET_ID,TextArea.class);
        target(value,VALUE_TEXT_TARGET_ID,TextArea.class);
        target(check,CHECK_BUTTON_TARGET_ID,Button.class);
        target(check,CHECK_TEXT_TARGET_ID,TextArea.class);
        return new Binding(view,plain,value,check,opener,popup,list,title,close,options,option);
    }
}
