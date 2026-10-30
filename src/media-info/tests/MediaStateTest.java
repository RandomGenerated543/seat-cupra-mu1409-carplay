import de.mibr.media.MediaState;
public final class MediaStateTest {
    static int checks;
    static void check(boolean value){checks++;if(!value)throw new AssertionError("check "+checks);}
    public static void main(String[] args){
        MediaState s=new MediaState();
        s.track("stale","","",1);check(s.snapshot()==null);
        s.connection(true);check(s.snapshot()==null);
        s.track("Song","Artist","Album",1);check("Song".equals(s.snapshot()[0]));
        String[] snapshot=s.snapshot();snapshot[0]="tamper";check("Song".equals(s.snapshot()[0]));
        s.track("Next",null,"",1);check(s.snapshot()[1].equals(""));
        s.track("ignored","","",0);check(s.snapshot()==null);
        s.track("x\n y\u0000",null,null,1);check("x  y".equals(s.snapshot()[0]));
        s.connection(false);check(s.snapshot()==null);
        s.track("late old callback","","",1);s.connection(true);check(s.snapshot()==null);
        s.track(null,"Artist","Album",1);check(s.snapshot()==null);
        StringBuffer b=new StringBuffer();for(int i=0;i<255;i++)b.append('x');b.append("\uD83D\uDE00");
        s.track(b.toString(),"","",1);check(s.snapshot()[0].length()==255);
        s.track("Școala — 歌", "Björk", "",1);check(s.snapshot()[0].equals("Școala — 歌"));
        System.out.println("MEDIA_STATE_TEST=PASS assertions="+checks);
    }
}
