package de.mibr.hmi;

import de.vw.mib.datapool.ASLDatapool;
import de.vw.mib.datapool.ASLDatapoolObserver;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.Vector;

/** Host integration of the genuine callback seam; no live Unit or OEM state writes. */
public final class MibrSpeedObserverTest {
    static void check(boolean value, String why) { if (!value) throw new AssertionError(why); }
    static final class Time implements MibrVdataBridge.Clock {
        long value = 10000;
        public long now() { return value; }
    }
    static final class Pool implements InvocationHandler {
        final Vector listeners = new Vector();
        int value, reads;
        boolean failRegister;
        final ASLDatapool api = (ASLDatapool)Proxy.newProxyInstance(
            ASLDatapool.class.getClassLoader(), new Class[] { ASLDatapool.class }, this);
        public Object invoke(Object proxy, Method method, Object[] args) {
            String name = method.getName();
            if ("registerObserver".equals(name)) {
                if (failRegister) throw new IllegalStateException("fixture unavailable");
                check(((Integer)args[0]).intValue() == 1595, "exact semantic id");
                listeners.addElement(args[1]); return null;
            }
            if ("unregisterObserver".equals(name)) { listeners.removeElement(args[1]); return null; }
            if ("getInteger".equals(name)) { reads++; return new Integer(value); }
            throw new AssertionError("Unexpected OEM operation " + name);
        }
        void event(int speed) {
            value = speed;
            Object[] copy = listeners.toArray();
            for (int i = 0; i < copy.length; i++) ((ASLDatapoolObserver)copy[i]).datapoolValueChanged(1595);
        }
    }
    public static void main(String[] args) {
        Time time = new Time(); Pool pool = new Pool();
        final int[] stockCalls = new int[1];
        ASLDatapoolObserver stock = new ASLDatapoolObserver() {
            public void datapoolValueChanged(int id) { stockCalls[0]++; }
        };
        pool.listeners.addElement(stock);
        MibrVdataBridge.Tap tap = new MibrVdataBridge.Tap(pool.api, time);
        tap.attach();
        check(pool.listeners.size() == 2, "stock observer preserved");
        check(pool.reads == 0 && tap.take() == null, "registration never validates initial zero cache");
        tap.datapoolValueChanged(1594);
        check(pool.reads == 0, "unrelated property ignored");
        pool.event(0);
        MibrVdataBridge.Sample zero = tap.take();
        check(zero != null && zero.kmh == 0 && zero.at == 10000, "genuine stationary event is valid");
        time.value += 500;
        check(tap.take() == null && tap.fresh().at == 10000, "poll cannot refresh event timestamp");
        pool.event(0);
        MibrVdataBridge.Sample repeat = tap.take();
        check(repeat != null && repeat.at == 10500 && repeat.sequence > zero.sequence,
              "same-value genuine notification refreshes freshness");
        time.value += 1001;
        check(tap.fresh() == null && tap.take() == null, "silence expires sample");
        pool.event(68);
        MibrVdataBridge.Sample moving = tap.take();
        check(moving.kmh == 68 && moving.at == time.value, "real changed value retained");
        time.value--;
        check(tap.fresh() == null, "clock reversal fails closed");
        time.value += 2;
        pool.event(-1);
        check(tap.fresh() == null, "invalid value clears sample");
        pool.event(361);
        check(tap.fresh() == null, "out of domain value clears sample");
        tap.close();
        check(pool.listeners.size() == 1 && pool.listeners.elementAt(0) == stock, "detach removes only owned observer");
        int reads = pool.reads;
        pool.event(50); tap.datapoolValueChanged(1595);
        check(pool.reads == reads && tap.take() == null, "late callbacks after detach cannot publish");
        tap.attach();
        check(tap.take() == null, "reattach requires a new genuine event");
        pool.event(50);
        check(tap.take().kmh == 50 && stockCalls[0] == 7, "stock and owned observer both receive genuine events");
        tap.close();
        Pool unavailable = new Pool(); unavailable.failRegister = true;
        MibrVdataBridge.Tap refused = new MibrVdataBridge.Tap(unavailable.api, time);
        try { refused.attach(); throw new AssertionError("register failure accepted"); }
        catch (IllegalStateException expected) { }
        refused.datapoolValueChanged(1595);
        check(refused.take() == null && unavailable.reads == 0, "failed attach stays unavailable");
        System.out.println("MIBR_SPEED_OBSERVER_HOST_PASS no_initial_sample same_value_event stale detach stock_preserved");
    }
}
