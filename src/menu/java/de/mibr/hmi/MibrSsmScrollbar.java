package de.mibr.hmi;
import java.io.FileOutputStream;
import java.io.PrintStream;
final class MibrSsmScrollbar {
    private static int records;
    static void failure(Throwable failure){record("FAILED "+failure);}
    static synchronized void record(String value){
        if(records>=64)return;
        PrintStream out=null;
        try{
            out=new PrintStream(new FileOutputStream("/tmp/mibr-seat-scrollbar.log",records!=0));
            out.println("MENU_SCROLLBAR=v3 "+value);records++;
        }catch(Throwable failure){records++;System.err.println("SCROLL_LOG_FAILED "+failure);}
        finally{if(out!=null)out.close();}
    }
}
