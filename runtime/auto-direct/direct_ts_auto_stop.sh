#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
. /mnt/app/root/altscreen-u2/scripts/common.sh
runtime_init || exit 3
touch /tmp/mibr-direct-stopping || exit 20
rm -f /tmp/mibr-carplay-autodirect.enabled || exit 21

stop_one(){
  NAME=$1
  PF=$2
  [ -r "$PF" ] || return 0
  P=$(cat "$PF" 2>/dev/null)
  case "$P" in ''|*[!0-9]*) echo "STOP=FAIL invalid_pid_file=$PF"; return 1 ;; esac
  [ "$P" -gt 1 ] || return 1
  if ! kill -0 "$P" 2>/dev/null; then rm -f "$PF"; return 0; fi
  pidin ar 2>/dev/null | awk -v p="$P" -v n="$NAME" '$1==p && index($0,n){found=1} END{exit !found}' || {
    echo "STOP=FAIL pid_identity=$P expected=$NAME"
    return 1
  }
  kill "$P" 2>/dev/null || return 1
  N=0
  while kill -0 "$P" 2>/dev/null && [ "$N" -lt 3 ]; do sleep 1; N=$((N+1)); done
  if kill -0 "$P" 2>/dev/null; then
    kill -9 "$P" 2>/dev/null || return 1
    sleep 1
  fi
  kill -0 "$P" 2>/dev/null && { echo "STOP=FAIL still_alive=$P"; return 1; }
  rm -f "$PF"
}
# Prevent new sessions, then stop controllers and the actual writer before stock.
FAIL=0
stop_one direct_ts_auto_supervisor.sh /tmp/mibr-direct-auto-supervisor.pid || FAIL=1
stop_one direct_ts_auto_watchdog.sh /tmp/mibr-direct-auto-watchdog.pid || FAIL=1
stop_one /altscreen-u2/bin/direct-ts-remux /tmp/mibr-direct-auto-bridge.pid || FAIL=1
[ "$FAIL" -eq 0 ] || { echo "AUTO_DIRECT_STOP=FAIL_QUIESCENCE"; exit 22; }
"$BASE/scripts/writev_gate.sh" stock || exit 23
rm -f /tmp/mibr-direct-auto.heartbeat /tmp/mibr-alt111-keyframe-policy.enabled
 echo stopped > /tmp/mibr-direct-auto.state
echo "AUTO_DIRECT_STOP=PASS writer_terminated=1"
# Native record lock also prevents overlap if another recovery path clears marker early.
exit 0
