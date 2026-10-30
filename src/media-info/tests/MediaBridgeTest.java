import de.mibr.media.*;
import de.vw.mib.bap.mqbab2.audiosd.functions.CurrentStationInfo;
import de.vw.mib.bap.mqbab2.generated.audiosd.serializer.CurrentStationInfo_Status;
import de.vw.mib.genericevents.ThreadSwitchingTarget;
import java.lang.reflect.*;
import java.util.ArrayList;
import org.dsi.ifc.carplay.TrackData;

public final class MediaBridgeTest {
    static int checks;
    static void check(boolean value){checks++;if(!value)throw new AssertionError("bridge "+checks);}
    public static final class Station extends CurrentStationInfo {
        int calls;
        int connectionType=2;
        public void process(int n){calls++;}
        protected de.vw.mib.bap.mqbab2.common.api.smartphoneintegration.SmartphoneIntegrationService getSmartphoneIntegrationService(){
            return (de.vw.mib.bap.mqbab2.common.api.smartphoneintegration.SmartphoneIntegrationService)Proxy.newProxyInstance(
                MediaBridgeTest.class.getClassLoader(),new Class[]{de.vw.mib.bap.mqbab2.common.api.smartphoneintegration.SmartphoneIntegrationService.class},
                new InvocationHandler(){public Object invoke(Object p,Method m,Object[] a){
                    if(m.getName().equals("getSmarphoneIntegrationActiveConnectionType"))return Integer.valueOf(connectionType);
                    return null;
                }});
        }
    }
    public static void main(String[] args)throws Exception{
        final ArrayList<Runnable> queue=new ArrayList<Runnable>();
        ThreadSwitchingTarget invoker=(ThreadSwitchingTarget)Proxy.newProxyInstance(
            MediaBridgeTest.class.getClassLoader(),new Class[]{ThreadSwitchingTarget.class},
            new InvocationHandler(){public Object invoke(Object p,Method m,Object[] a){
                if(m.getName().equals("enqueue"))queue.add((Runnable)a[0]);
                return null;
            }});
        Station station=new Station();
        MediaBridge.stationReady(station,invoker);
        check(station.calls==0 && queue.size()==1);
        queue.remove(0).run();check(station.calls==1);
        Field epoch=MediaBridge.class.getDeclaredField("epoch");epoch.setAccessible(true);epoch.setInt(null,7);
        Constructor constructor=MediaBridge.class.getDeclaredConstructor(new Class[]{Integer.TYPE});constructor.setAccessible(true);
        MediaBridge listener=(MediaBridge)constructor.newInstance(new Object[]{Integer.valueOf(7)});
        Field f=MediaBridge.class.getDeclaredField("listener");f.setAccessible(true);f.set(null,listener);
        de.vw.mib.asl.internal.carplay.common.CarPlayGlobalProperies properties=
            new de.vw.mib.asl.internal.carplay.common.CarPlayGlobalProperies(null);
        properties.setConnectionState(3);queue.clear();
        // Flush the coalesced connection refresh, otherwise it deliberately suppresses the next enqueue.
        MediaBridge.stationGone(station);
        Field queued=MediaBridge.class.getDeclaredField("queued");queued.setAccessible(true);queued.setBoolean(null,false);
        MediaBridge.stationReady(station,invoker);queue.remove(0).run();
        listener.updateNowPlayingData(new TrackData("Title",100000,"Album","Artist","",""),1);
        check(queue.size()==1);int previous=station.calls;
        check(station.calls==previous);queue.remove(0).run();check(station.calls==previous+1);
        CurrentStationInfo_Status status=new CurrentStationInfo_Status();
        status.primaryInformation.setContent("radio");MediaBridge.render(status,1);
        check(status.primaryInformation.toString().indexOf("radio")>=0);
        MediaBridge.render(status,2);
        check(status.primaryInformation.toString().indexOf("Title")>=0 && status.pi_Type==72);
        check(status.secondaryInformation.toString().indexOf("Artist")>=0 && status.si_Type==73);
        check(status.tertiaryInformation.toString().indexOf("Album")>=0 && status.ti_Type==74);
        Method render=CurrentStationInfo.class.getDeclaredMethod("setStationInfoForMirrorLink",new Class[]{CurrentStationInfo_Status.class});
        render.setAccessible(true);render.invoke(station,new Object[]{status});
        check(status.primaryInformation.toString().indexOf("Title")>=0);
        station.connectionType=1;render.invoke(station,new Object[]{status});
        check(status.primaryInformation.toString().indexOf("MirrorLink")>=0);
        station.connectionType=2;
        properties.setConnectionState(0);
        listener.updateNowPlayingData(new TrackData("late",0,"","","",""),1);
        status.primaryInformation.setContent("Apple CarPlay");MediaBridge.render(status,2);
        check(status.primaryInformation.toString().indexOf("Apple CarPlay")>=0 && status.si_Type==0);
        render.invoke(station,new Object[]{status});
        check(status.primaryInformation.toString().indexOf("Apple CarPlay")>=0 && status.si_Type==0);
        MediaBridge.connection(3);epoch.setInt(null,8);
        listener.updateNowPlayingData(new TrackData("old generation",0,"","","",""),1);
        MediaBridge.render(status,2);check(status.primaryInformation.toString().indexOf("old generation")<0);
        MediaBridge.stationGone(station);
        int count=station.calls;while(!queue.isEmpty())queue.remove(0).run();check(count==station.calls);
        f.set(null,null);
        System.out.println("MEDIA_BRIDGE_TEST=PASS assertions="+checks+" actual_target_datatypes=1 task_dispatch=1");
    }
}
