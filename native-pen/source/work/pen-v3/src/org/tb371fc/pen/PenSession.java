package org.tb371fc.pen;

import java.util.Locale;

/** Hardware session state. NVT registration, names and a bond alone are not a connection. */
public final class PenSession {
    public interface Sink { void stateChanged(Snapshot state); }
    public static final class Snapshot {
        public final long generation;
        public final boolean connected;
        public final String address, name;
        public final int battery;
        public Snapshot(long g, boolean c, String a, String n, int b) {
            generation=g; connected=c; address=a; name=n; battery=b;
        }
    }
    private final Sink sink;
    private long generation;
    private String address="", name="";
    private boolean connected;
    private int battery=-1;
    public PenSession(Sink s) { sink=s; }

    public static boolean officialName(String name) {
        if(name==null) return false;
        String s=name.trim().toLowerCase(Locale.ROOT);
        return s.equals("lenovo precision pen 3") || s.equals("lenovo precision pen3")
            || s.equals("小新触控笔二代") || s.equals("小新触控笔(第二代)")
            || s.equals("小新触控笔（第二代）") || s.equals("xiaoxin stylus 2");
    }
    public static boolean validAddress(String a) {
        return a!=null && a.matches("(?i)[0-9a-f]{2}(:[0-9a-f]{2}){5}")
            && !a.equalsIgnoreCase("00:00:00:00:00:00")
            && !a.equalsIgnoreCase("02:00:00:00:00:00");
    }
    public synchronized long begin(String a,String n,boolean bonded) {
        return beginHardware(a,n,bonded,false);
    }
    public synchronized long beginHardware(String a,String n,boolean bonded,boolean hardwareIdentity) {
        disconnect();
        if(!bonded || (!officialName(n)&&!hardwareIdentity) || !validAddress(a)) return -1;
        address=a.toUpperCase(Locale.ROOT); name=n==null||n.trim().isEmpty()?"手写笔":n.trim();
        return generation;
    }
    /** A callback is accepted only for this exact GATT session and confirmed pen capabilities. */
    public synchronized boolean ready(long g,String a,boolean gattConnected,boolean penServices) {
        if(g!=generation || !address.equalsIgnoreCase(a) || !gattConnected || !penServices) return false;
        if(!connected) { connected=true; publish(); }
        return true;
    }
    public synchronized boolean battery(long g,byte[] value) {
        if(g!=generation || !connected || value==null || value.length!=1) return false;
        int b=value[0]&255;
        if(b>100) return false;
        if(b!=battery) { battery=b; publish(); }
        return true;
    }
    public synchronized void disconnect() {
        generation++;
        boolean hadState=connected || battery!=-1;
        connected=false; battery=-1; address=""; name="";
        if(hadState) publish();
    }
    public synchronized Snapshot snapshot() { return new Snapshot(generation,connected,address,name,battery); }
    private void publish() { sink.stateChanged(snapshot()); }
}
