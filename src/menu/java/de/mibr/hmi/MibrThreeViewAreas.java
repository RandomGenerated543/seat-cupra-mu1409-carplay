package de.mibr.hmi;

/**
 * Presentation-only plan for the three future AID10 safe-area layouts.
 *
 * IMPORTANT: this is NOT the Classic111 registry, a source of geometry, or
 * evidence that a current session has advertised three areas. Existing
 * R10/R11 target binaries accept only indices 0 and 1. The labels below
 * must be used for live readback only after the native controller proves a
 * three-area registry AND the stream's three-area advertisement.
 *
 * The outer CarPlay frame stays 0,0,1010,376 for every view; the proposed
 * safe rectangles belong in the canonical native registry, not in Java.
 * See design/REQ_VIEW_AREAS_VOLL_CENTER_WIDE_2026-10-20.md.
 */
public final class MibrThreeViewAreas {
    public static final int COUNT=3;
    public static final int CENTER=0;
    public static final int VOLL=1;
    public static final int WIDE=2;
    private MibrThreeViewAreas() { }

    public static String[] proposedWireValues() {
        return new String[]{"0","1","2"};
    }

    public static boolean isProposedWireValue(String wire) {
        return "0".equals(wire)||"1".equals(wire)||"2".equals(wire);
    }

    public static String qualifiedLabel(String wire) {
        if("0".equals(wire))return "Center";
        if("1".equals(wire))return MibrI18n.pick("Voll","Full");
        if("2".equals(wire))return "Wide";
        return null;
    }

    /**
     * Never infer this from a saved index, a Java menu choice or a successful
     * TCP response. Caller must provide independent native registry and
     * current-session advertisement evidence before changing displayed labels.
     */
    public static boolean canDisplayQualifiedLabels(int nativeCount,
            int advertisedCount,boolean currentSessionConfirmed) {
        return nativeCount==COUNT && advertisedCount==COUNT &&
                currentSessionConfirmed;
    }
}
