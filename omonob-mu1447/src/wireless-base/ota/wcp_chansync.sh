#!/bin/sh
# Wireless CarPlay Maps. Maintainer: omonob. Source date: 2026-08-29.
# wcp_chansync.sh -- keep /tmp/uaputl.cfg's Channel equal to uap0's REAL running channel,
# and tell btwcp when that channel has settled.
#
# Why: uap0 is single-radio and follows the uplink (mlan0). Its static Channel in
# uaputl.cfg is often stale (e.g. Channel=11 while the AP actually runs on 9). btwcp
# reads that Channel at 0x4301/0x5703 time and tells the phone the wrong channel, so the
# phone scans the wrong channel, never joins the hotspot, and wireless CarPlay stalls
# right after CarPlayStart. This re-syncs the FILE only -- it never runs uaputl and never
# touches the WLAN driver. The hotspot password line is never read aloud or logged.
#
# Settled channel (2026-08-29): the AP channel also MOVES once mlan0 associates with its
# network (bench: 11 -> 9 about 15 s after the phone had already been sent 0x4301 on 11).
# The phone then drops out of the hotspot, and forcing a re-handshake (dropping the phone's
# ACL) makes the iPhone refuse the car for minutes (0x13). So btwcp now waits, before an
# outbound reconnect, for /dev/shmem/wcp_chan_stable, written here when:
#   the uap0 channel has not changed for STABLE_TICKS x 2 s, AND
#   mlan0 is associated ("status: active"), or mlan0 is not running at all (no uplink that
#   could still pull the AP), or the AP has been up for SETTLE_MAX_TICKS x 2 s (an mlan0
#   that is up but never associates -- no saved network in range -- must not block forever).
# If the channel changes after that, the file is removed until it settles again.
# btwcp has its own upper bound on the wait, so a dead watcher never blocks reconnects.
#
# Usage:
#   wcp_chansync.sh once     # sync a single time, print result
#   wcp_chansync.sh watch    # background-friendly loop (~240s), re-sync every 2s
CFG=/tmp/uaputl.cfg
LOG=${WCP_CHANSYNC_LOG:-/dev/shmem/wcp_chansync.log}
STABLE=${WCP_CHAN_STABLE:-/dev/shmem/wcp_chan_stable}
STABLE_TICKS=${WCP_CHAN_STABLE_TICKS:-5}          # 10 s unchanged
SETTLE_MAX_TICKS=${WCP_CHAN_SETTLE_MAX_TICKS:-23} # ~46 s after the AP channel first showed up
IFCONFIG=${WCP_IFCONFIG:-ifconfig}
NAP=${WCP_CHANSYNC_NAP:-2}

_live_chan() {
    $IFCONFIG uap0 2>/dev/null | sed -n 's/.*chan \([0-9][0-9]*\).*/\1/p' | head -1
}

_sync_once() {
    [ -f "$CFG" ] || return 1
    _rc=`_live_chan`
    [ -n "$_rc" ] || return 1
    _cc=`sed -n 's/.*Channel=\([0-9][0-9]*\).*/\1/p' "$CFG" | head -1`
    [ -n "$_cc" ] || return 1
    if [ "$_rc" != "$_cc" ]; then
        sed "s/Channel=$_cc/Channel=$_rc/" "$CFG" > "$CFG.n" 2>/dev/null && mv -f "$CFG.n" "$CFG" 2>/dev/null
        echo "[chansync] $_cc -> $_rc" >> $LOG
        echo "synced $_cc -> $_rc"
        return 0
    fi
    echo "already $_rc"
    return 0
}

# uplink state: active = associated; down = mlan0 not running (cannot pull the AP); idle = up, not associated
_uplink() {
    _m=`$IFCONFIG mlan0 2>/dev/null`
    case "$_m" in
        *"status: active"*) echo active ;;
        *RUNNING*)          echo idle ;;
        *)                  echo down ;;
    esac
}

case "${1:-once}" in
  once)  _sync_once ;;
  watch)
    PID=/dev/shmem/mu1447-wcp-chansync.pid
    if [ -f "$PID" ]; then
      OLD=$(cat "$PID" 2>/dev/null)
      case "$OLD" in ''|*[!0-9]*) OLD= ;; esac
      if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null && pidin -p "$OLD" ar 2>/dev/null | grep -q '[w]cp_chansync.sh'; then
        exit 0
      fi
      rm -f "$PID"
    fi
    (umask 077;set -C;echo $$ > "$PID") 2>/dev/null || exit 1
    trap 'rm -f "$PID"' 0
    trap 'exit 0' 1 2 15
    rm -f "$STABLE"
    _n=0; _seen=0; _same=0; _last=
    while :; do
        [ -f /mnt/persist/btwcp_off ] && break
        [ -f /mnt/persist/wcp_autostart ] || break
        _sync_once >/dev/null 2>&1
        _c=`_live_chan`
        if [ -n "$_c" ]; then
            _seen=$((_seen+1))
            if [ "$_c" = "$_last" ]; then _same=$((_same+1)); else
                if [ -n "$_last" ] && [ -f "$STABLE" ]; then
                    rm -f "$STABLE"
                    echo "[chansync] channel moved $_last -> $_c after settle: unsettled again" >> $LOG
                fi
                _same=0; _last=$_c
            fi
            if [ ! -f "$STABLE" ] && [ $_same -ge $STABLE_TICKS ]; then
                _u=`_uplink`
                if [ "$_u" != idle ] || [ $_seen -ge $SETTLE_MAX_TICKS ]; then
                    echo "$_c" > "$STABLE"
                    echo "[chansync] settled on $_c (uplink $_u, $((_seen*NAP))s after AP up)" >> $LOG
                fi
            fi
        fi
        sleep $NAP
        _n=$((_n+1))
    done ;;
esac
exit 0
