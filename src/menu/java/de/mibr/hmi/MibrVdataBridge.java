package de.mibr.hmi;

import de.vw.mib.asl.framework.api.dsiproxy.DSIProxy;
import de.vw.mib.asl.framework.api.dsiproxy.DSIProxyFactory;
import de.vw.mib.asl.internal.system.SystemAccessor;
import de.vw.mib.genericevents.Target;
import de.vw.mib.datapool.ASLDatapool;
import de.vw.mib.datapool.ASLDatapoolObserver;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Vector;
import mib.mu1440.vehiclespeed.DsiVehicleSpeedAdapter;
import mib.mu1440.vehiclespeed.Mu1440CarBCSpeedDecoder;
import org.dsi.ifc.global.CarBCSpeed;

/**
 * HMI-side vehicle speed source for the CarPlay vehicle-data module (CaneTLOTW/M.I.B._Research#116).
 * Default OFF: nothing is attached unless /mnt/app/root/altscreen-u2/config/vdata.mode says shadow or send.
 * It observes existing ASL CURRENT_VELOCITY publications and writes fresh genuine events as
 * MVS1 records into a small ring file that the native module (inside dio_manager) reads. It never
 * touches OEM state, never blocks an OEM thread and swallows every failure.
 */
public final class MibrVdataBridge {
    private static final String MODE = "/mnt/app/root/altscreen-u2/config/vdata.mode";
    private static final String RING = "/tmp/mibr-vdata-speed.ring";
    private static final String STATUS = "/tmp/mibr-vdata-source.status";
    private static final int RING_RECORDS = 8;
    private static volatile boolean wanted;
    private static Thread worker;

    private MibrVdataBridge() { }

    /** Called once from the activator; returns at once, all work runs in one daemon thread. */
    public static synchronized void start() {
        wanted = true;
        if (worker != null) return;
        worker = new Thread(new Runnable() { public void run() {
            try { loop(); }
            finally { synchronized (MibrVdataBridge.class) {
                worker = null;
                if (wanted) start();
            } }
        } }, "MibrVdata");
        worker.setDaemon(true);
        worker.start();
    }

    /** Bundle teardown owns its additive observer and worker. No OEM subscription is changed. */
    public static synchronized void stop() {
        wanted = false;
        if (worker != null) worker.interrupt();
    }

    interface Clock { long now(); }
    static final Clock CLOCK = new Clock() { public long now() { return System.currentTimeMillis(); } };
    static final int CURRENT_VELOCITY = 1595;
    static final long MAX_SAMPLE_AGE_MS = 1000L;

    static final class Sample {
        final int kmh;
        final long at, sequence;
        Sample(int value, long timestamp, long seq) { kmh = value; at = timestamp; sequence = seq; }
    }

    /** Callback records only genuine OEM publications; no initial cache read or file IO. */
    static final class Tap implements ASLDatapoolObserver {
        private final ASLDatapool pool;
        private final Clock clock;
        private boolean active;
        private Sample sample;
        private long sequence, consumed;
        Tap(ASLDatapool source, Clock time) { pool = source; clock = time; }
        synchronized void attach() {
            if (active) return;
            active = true;
            try { pool.registerObserver(CURRENT_VELOCITY, this); }
            catch (Throwable t) { active = false; sample = null; throw new IllegalStateException("SPEED_OBSERVER_UNAVAILABLE"); }
        }
        public synchronized void datapoolValueChanged(int id) {
            if (!active || id != CURRENT_VELOCITY) return;
            try {
                int value = pool.getInteger(CURRENT_VELOCITY);
                long at = clock.now();
                sample = value < 0 || value > 360 || at < 0 ? null : new Sample(value, at, ++sequence);
            } catch (Throwable t) { sample = null; }
        }
        synchronized Sample fresh() {
            if (!active || sample == null) return null;
            long age = clock.now() - sample.at;
            return age >= 0 && age <= MAX_SAMPLE_AGE_MS ? sample : null;
        }
        synchronized Sample take() {
            Sample next = fresh();
            if (next == null || next.sequence == consumed) return null;
            consumed = next.sequence;
            return next;
        }
        synchronized void close() {
            active = false;
            sample = null;
            pool.unregisterObserver(CURRENT_VELOCITY, this);
        }
    }

    private static boolean enabled() {
        FileInputStream in = null;
        try {
            byte[] b = new byte[16];
            in = new FileInputStream(MODE);
            int n = in.read(b);
            if (n < 4) return false;
            String s = new String(b, 0, n, "US-ASCII");
            return s.startsWith("shadow") || s.startsWith("send");
        } catch (Throwable t) {
            return false;
        } finally {
            if (in != null) try { in.close(); } catch (Throwable ignored) { }
        }
    }

    private static final class Ring implements DsiVehicleSpeedAdapter.Policy {
        private final Vector records = new Vector();
        long offers, failures, lastMmps = -1L, sampleTime;

        public boolean ready() { return true; }
        public int toMillimetresPerSecond(CarBCSpeed speed) {
            return Mu1440CarBCSpeedDecoder.toMillimetresPerSecond(speed);
        }
        /** Relative time only: the native side re-bases the newest record to the file age. */
        public long monotonicMillis() { return sampleTime; }
        public synchronized boolean offer(byte[] mvs1) {
            if (mvs1 == null || mvs1.length != 24) return false;
            offers++;
            lastMmps = (mvs1[16] & 0xffL) | ((mvs1[17] & 0xffL) << 8) | ((mvs1[18] & 0xffL) << 16) | ((mvs1[19] & 0xffL) << 24);
            records.addElement(mvs1);
            while (records.size() > RING_RECORDS) records.removeElementAt(0);
            return flush();
        }
        private boolean flush() {
            FileOutputStream out = null;
            try {
                /* File.renameTo fails on this QNX/J9 (127 of 127 in the first run): write the final file directly,
                   as one buffer in one write; the native reader validates every record. */
                byte[] all = new byte[records.size() * 24];
                for (int i = 0; i < records.size(); i++) System.arraycopy((byte[]) records.elementAt(i), 0, all, i * 24, 24);
                out = new FileOutputStream(RING);
                out.write(all);
                out.close();
                out = null;
                return true;
            } catch (Throwable t) {
                failures++;
                return false;
            } finally {
                if (out != null) try { out.close(); } catch (Throwable ignored) { }
            }
        }
        synchronized void clearFile() { records.removeAllElements(); try { new File(RING).delete(); } catch (Throwable ignored) { } }
    }

    private static void status(String state, Ring ring, int attempts) {
        FileOutputStream out = null;
        try {
            String text = "state=" + state + "\nattempts=" + attempts +
                "\noffers=" + (ring == null ? 0L : ring.offers) +
                "\nwrite_failures=" + (ring == null ? 0L : ring.failures) +
                "\nlast_speed_mmps=" + (ring == null ? -1L : ring.lastMmps) + "\n";
            out = new FileOutputStream(STATUS);
            out.write(text.getBytes("US-ASCII"));
        } catch (Throwable ignored) {
        } finally {
            if (out != null) try { out.close(); } catch (Throwable ignored) { }
        }
    }

    /** Resolve the existing ASL property manager's actual datapool; never replace the manager. */
    private static ASLDatapool stockPool() {
        Object manager = de.vw.mib.asl.framework.internal.framework.ServiceManager.aslPropertyManager;
        for (Class c = manager == null ? null : manager.getClass(); c != null; c = c.getSuperclass()) {
            try {
                java.lang.reflect.Field f = c.getDeclaredField("datapool");
                f.setAccessible(true);
                Object value = f.get(manager);
                return value instanceof ASLDatapool ? (ASLDatapool)value : null;
            } catch (NoSuchFieldException e) {
            } catch (Throwable t) { return null; }
        }
        return null;
    }

    private static void loop() {
        Ring ring = new Ring();
        DsiVehicleSpeedAdapter adapter = null;
        Tap tap = null;
        ASLDatapool attachedPool = null;
        int attempts = 0;
        String last = "";
        try { while (wanted && !Thread.currentThread().isInterrupted()) {
            try {
                boolean on = enabled();
                String state;
                if (!on) {
                    if (tap != null) { tap.close(); tap = null; attachedPool = null; }
                    if (adapter != null) { adapter.close(); adapter = null; }
                    ring.clearFile();
                    state = "off";
                } else {
                    ASLDatapool pool = stockPool();
                    if (tap != null && pool != attachedPool) {
                        tap.close(); tap = null; attachedPool = null; ring.clearFile();
                    }
                    if (pool == null) state = "waiting_for_asl";
                    else {
                        if (adapter == null) {
                            adapter = DsiVehicleSpeedAdapter.offline(ring);
                            adapter.beginCarPlaySession(1L);
                        }
                        if (tap == null) {
                            attempts++;
                            tap = new Tap(pool, CLOCK);
                            try { tap.attach(); attachedPool = pool; }
                            catch (Throwable t) { try { tap.close(); } catch (Throwable ignored) { } tap = null; throw t; }
                        }
                        Sample sample = tap.take();
                        if (sample != null) {
                            org.dsi.ifc.carvehiclestates.DynamicVehicleInfoHighFrequent hf =
                                new org.dsi.ifc.carvehiclestates.DynamicVehicleInfoHighFrequent();
                            hf.vehicleSpeed = new CarBCSpeed(org.dsi.ifc.global.CarConstants.BCVALUESTATE_VALID,
                                (float) sample.kmh, org.dsi.ifc.global.CarConstants.SPEEDUNIT_KMPH);
                            ring.sampleTime = sample.at;
                            adapter.updateDynamicVehicleInfoHighFrequent(hf, 1);
                        }
                        Sample live = tap.fresh();
                        if (live == null) { ring.clearFile(); state = "waiting_for_fresh_speed"; }
                        else state = "tap_kmh=" + live.kmh;
                    }
                }
                if (!state.equals(last) || adapter != null) status(state, ring, attempts);
                last = state;
                Thread.sleep(adapter != null ? 200L : 5000L);
            } catch (InterruptedException e) {
                return;
            } catch (Throwable t) {
                ring.clearFile();
                status("error_" + t.getClass().getName(), ring, attempts);
                try { Thread.sleep(10000L); } catch (InterruptedException e) { return; }
            }
        } } finally {
            if (tap != null) try { tap.close(); } catch (Throwable ignored) { }
            if (adapter != null) try { adapter.close(); } catch (Throwable ignored) { }
            ring.clearFile();
            status("off", ring, attempts);
        }
    }
}
