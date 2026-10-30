package de.mibr.media;

/** Atomic metadata snapshots; independent of OEM collectors and audio ownership. */
public final class MediaState {
    private boolean connected;
    private String[] track = new String[]{"", "", ""};
    private int revision;
    public synchronized void connection(boolean value) {
        if (!value) track = new String[]{"", "", ""};
        connected = value;
        revision++;
    }
    public synchronized void track(String title, String artist, String album, int valid) {
        if (!connected) return;
        track = valid == 1 ? new String[]{clean(title), clean(artist), clean(album)} :
                            new String[]{"", "", ""};
        revision++;
    }
    public synchronized String[] snapshot() {
        if (!connected || track[0].length() == 0) return null;
        return new String[]{track[0], track[1], track[2]};
    }
    public synchronized int revision() { return revision; }
    private static String clean(String value) {
        if (value == null) return "";
        StringBuffer out = new StringBuffer();
        int max = value.length() < 256 ? value.length() : 256;
        if (max > 0 && max < value.length() && value.charAt(max-1)>=0xD800 && value.charAt(max-1)<=0xDBFF) max--;
        for (int i=0; i<max; i++) {
            char c = value.charAt(i);
            out.append(c < 32 || c == 127 ? ' ' : c);
        }
        return out.toString().trim();
    }
}
