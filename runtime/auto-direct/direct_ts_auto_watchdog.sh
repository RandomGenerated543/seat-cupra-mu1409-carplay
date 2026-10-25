#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
. /mnt/app/root/altscreen-u2/scripts/common.sh
runtime_init || exit 3
PIDFILE=/tmp/mibr-direct-auto-watchdog.pid
[ -r "$PIDFILE" ] && { P=$(cat "$PIDFILE"); kill -0 "$P" 2>/dev/null && exit 0; }
echo "$$" > "$PIDFILE" || exit 4
trap 'rm -f "$PIDFILE"' 0
LAST=""
STALE=0
while [ -e /tmp/mibr-carplay-autodirect.enabled ] && [ ! -e /tmp/mibr-direct-stopping ]; do
  if [ -e /tmp/mibr-isotx2-gate.direct ]; then
    CUR=$(cat /tmp/mibr-direct-auto.heartbeat 2>/dev/null)
    if [ -n "$CUR" ] && [ "$CUR" != "$LAST" ]; then STALE=0; LAST=$CUR; else STALE=$((STALE+1)); fi
    if [ "$STALE" -ge 5 ]; then
      echo "WATCHDOG=STALE requesting writer termination" >> /tmp/mibr-direct-auto-watchdog.log
      "$BASE/scripts/direct_ts_auto_stop.sh"
      exit $?
    fi
  else
    STALE=0
  fi
  sleep 1
done
# Never resume stock here without the common stop/quiescence sequence.
exit 0
