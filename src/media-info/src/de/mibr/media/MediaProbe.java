package de.mibr.media;
/** Target loader check only: does not attach listeners or instantiate OEM targets. */
public final class MediaProbe {
    public static void main(String[] args)throws Exception {
        Class.forName("de.mibr.media.MediaBridge");
        Class.forName("de.vw.mib.asl.internal.carplay.target.HsmTarget");
        Class.forName("de.vw.mib.asl.internal.carplay.common.CarPlayGlobalProperies");
        Class.forName("de.vw.mib.bap.mqbab2.audiosd.functions.CurrentStationInfo");
        MediaState state=new MediaState();state.connection(true);state.track("probe","artist","album",1);
        if(!"probe".equals(state.snapshot()[0]))throw new Exception("model");
        System.out.println("MEDIA_J9_PROBE=PASS controls_invoked=0 visible_effect=UNTESTED");
    }
}
