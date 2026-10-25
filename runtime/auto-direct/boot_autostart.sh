#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
# MMX MU1409 only. Background normal-boot worker, never blocks OEM startup.
# Dependencies: installed common.sh, ksh builtins, cat/awk/grep/pidin/sleep,
# installed hash helper, pfctl -sr, existing audited start/stop/owner protocol.
# No mount, persistent writes, firewall reload, or direct device writes here.
. /mnt/app/root/altscreen-u2/scripts/common.sh || exit 2
runtime_init || exit 3
N=0
while [ "$N" -lt 180 ]; do
 [ -e "$BASE/config/autostart.enabled" ] || { echo "AUTOSTART=DISABLED"; exit 0; }
 [ ! -e /tmp/mibr-direct-stopping ] || { echo "AUTOSTART=CANCELLED_BY_STOP"; exit 0; }
 if [ -d /fs/tmpfs ] && [ -r /tmp/mibr-isotx2-gate.stats ] &&
    grep -q '^loaded=1$' /tmp/mibr-isotx2-gate.stats &&
    grep -q '^owner_protocol=2$' /tmp/mibr-isotx2-gate.stats &&
    grep -q '^owner_lock_ready=1$' /tmp/mibr-isotx2-gate.stats &&
    /armle/sbin/pfctl -sr | grep -F 'carplay0' | grep -Fq '6031'; then
  if navignore_active && carplay_stack_health; then
   echo "AUTOSTART=STARTING attempt=$N"
   # One attempt only: stop/watchdog failures must not create an automatic loop.
   /bin/ksh "$BASE/scripts/direct_ts_auto_start.sh"
   RC=$?
   echo "AUTOSTART=FINISHED rc=$RC"
   exit "$RC"
  fi
 fi
 N=$((N+1))
 sleep 1
done
echo "AUTOSTART=TIMEOUT stock_preserved=1"
exit 4
