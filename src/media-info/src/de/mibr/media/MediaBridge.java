package de.mibr.media;

import de.vw.mib.asl.framework.api.dsiproxy.*;
import de.vw.mib.asl.internal.carplay.target.HsmTarget;
import de.vw.mib.bap.mqbab2.audiosd.functions.CurrentStationInfo;
import de.vw.mib.bap.mqbab2.generated.audiosd.serializer.CurrentStationInfo_Status;
import de.vw.mib.genericevents.ThreadSwitchingTarget;
import java.io.File;
import java.io.FileOutputStream;
import org.dsi.ifc.carplay.*;
import org.dsi.ifc.global.ResourceLocator;

/** MU1409 DSI -> OEM AudioSD text. No audio, video, input or navigation setters. */
public final class MediaBridge implements DSICarplayListener {
    private static final MediaState state = new MediaState();
    private static MediaBridge listener;
    private static HsmTarget owner;
    private static DSIProxy proxy;
    private static DSICarplay service;
    private static CurrentStationInfo station;
    private static ThreadSwitchingTarget invoker;
    private static boolean queued;
    private static int epoch, updates, rendered;
    private final int generation;
    private MediaBridge(int generation) { this.generation=generation; }
    public static synchronized void attach(HsmTarget target) {
        try {
            if (owner==target && listener!=null) return;
            detach();
            proxy=DSIProxyFactory.getDSIProxyAPI().getDSIProxy();
            service=target.getDSICarPlay();
            if (proxy==null || service==null) { log("ATTACH_UNAVAILABLE"); return; }
            owner=target;
            MediaBridge next=new MediaBridge(++epoch);
            proxy.addResponseListener(target, DSICarplayListener.class, next);
            listener=next;
            service.setNotification(new int[]{DSICarplay.ATTR_NOWPLAYINGDATA}, next);
            log("ATTACHED metadata_attribute=3 video_setters=0");
        } catch(Throwable t) { detach(); log("ATTACH_FAILED "+t.getClass().getName()); }
    }
    public static synchronized void detach() {
        MediaBridge previous=listener;
        listener=null; epoch++; state.connection(false);
        try { if(previous!=null && service!=null) service.clearNotification(new int[]{3}, previous); }
        catch(Throwable t) { log("CLEAR_NOTIFICATION_FAILED"); }
        try { if(previous!=null && proxy!=null && owner!=null)
            proxy.removeResponseListener(owner, DSICarplayListener.class, previous); }
        catch(Throwable t) { log("REMOVE_LISTENER_FAILED"); }
        owner=null; service=null; proxy=null;
        refresh();
    }
    public static void connection(int value) {
        try {
            state.connection(value==3);
            synchronized(MediaBridge.class){
                if(value==3 && listener!=null && service!=null)
                    service.setNotification(new int[]{3},listener);
            }
            refresh(); log("CONNECTION state="+value);
        }
        catch(Throwable t) { log("CONNECTION_FAILED"); }
    }
    public static synchronized void stationReady(CurrentStationInfo value, ThreadSwitchingTarget task) {
        station=value; invoker=task; refresh(); log("BAP_BOUND task="+(task!=null?1:0));
    }
    public static synchronized void stationGone(CurrentStationInfo value) {
        if(station==value) { station=null; invoker=null; }
    }
    private static synchronized void refresh() {
        if(queued || station==null || invoker==null) return;
        final CurrentStationInfo expected=station;
        final ThreadSwitchingTarget task=invoker;
        queued=true;
        try { task.enqueue(new Runnable(){ public void run(){
            synchronized(MediaBridge.class){ queued=false; if(station!=expected || invoker!=task)return; }
            try { expected.process(-1); } catch(Throwable t){ log("BAP_REFRESH_FAILED"); }
        }}); } catch(Throwable t) { queued=false; log("BAP_ENQUEUE_FAILED"); }
    }
    public static void render(CurrentStationInfo_Status status, int connectionType) {
        try {
            if(connectionType!=2) return;
            String[] s=state.snapshot();
            if(s==null){
                status.secondaryInformation.setContent(""); status.si_Type=0;
                status.tertiaryInformation.setContent(""); status.ti_Type=0;
                status.quaternaryInformation.setContent(""); status.qi_Type=0;
                return;
            }
            status.primaryInformation.setContent(s[0]); status.pi_Type=72; status.pi_Id=0;
            status.secondaryInformation.setContent(s[1]); status.si_Type=s[1].length()>0?73:0;
            status.tertiaryInformation.setContent(s[2]); status.ti_Type=s[2].length()>0?74:0;
            status.quaternaryInformation.setContent(""); status.qi_Type=0;
            synchronized(MediaBridge.class){rendered++;}
            publish();
        } catch(Throwable t) { log("RENDER_FAILED "+t.getClass().getName()); }
    }
    public void updateNowPlayingData(TrackData data,int valid) {
        try {
            synchronized(MediaBridge.class){
                if(listener!=this || epoch!=generation)return;
                state.track(data==null?null:data.title,data==null?null:data.artist,
                            data==null?null:data.album,valid);
                updates++; refresh();
            }
            publish();
        }catch(Throwable t){log("METADATA_FAILED "+t.getClass().getName());}
    }
    private static synchronized void publish() {
        try {
            String s="revision=seat_media_v01\nattached="+(listener!=null?1:0)+
                "\nbap_bound="+(station!=null?1:0)+"\nupdates="+updates+
                "\nrendered="+rendered+"\nmetadata_ready="+(state.snapshot()!=null?1:0)+
                "\nvisible=OPERATOR_CHECK_REQUIRED\n";
            FileOutputStream out=new FileOutputStream("/tmp/mibr-seat-media.status");
            try{out.write(s.getBytes("US-ASCII"));}finally{out.close();}
        }catch(Throwable ignored){}
    }
    private static synchronized void log(String message) {
        try {
            File file=new File("/tmp/mibr-seat-media.log");
            FileOutputStream out=new FileOutputStream(file,file.length()<65536L);
            try{out.write((message+"\n").getBytes("US-ASCII"));}finally{out.close();}
        }catch(Throwable ignored){}
        publish();
    }
    public void asyncException(int code,String text,int request){log("DSI_EXCEPTION code="+code);}
    public void updateMode(Resource[] r,AppState[] a,int valid){}
    public void responseModeChange(Resource[] r,AppState[] a,int valid){}
    public void requestBTDeactivation(String a,int b){}
    public void updateDeviceInfo(DeviceInfo d,int valid){}
    public void updateCallState(CallState[] a,int valid){}
    public void updateTelephonyState(TelephonyState a,int valid){}
    public void updatePlaybackState(PlaybackInfo a,int valid){}
    public void updatePlayposition(int position,int valid){}
    public void updateCoverArtUrl(ResourceLocator a,int valid){}
    public void updateTextInputState(int a,int valid){}
    public void duckAudio(int a,double b){}
    public void unduckAudio(int a){}
    public void oemAppSelected(){}
    public void updateMainAudioType(int a,int valid){}
}
