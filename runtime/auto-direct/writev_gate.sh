#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
. /mnt/app/root/altscreen-u2/scripts/common.sh

MARKER=/tmp/mibr-isotx2-gate.direct
RESET=/tmp/mibr-isotx2-gate.reset
STATS=/tmp/mibr-isotx2-gate.stats
LOGFILE=/tmp/mibr-isotx2-gate.log

case "${1:-status}" in
  direct)
    [ -r "$STATS" ] || {
      echo "FAIL gate stats absent; DisplayManager interposer not proven loaded"
      exit 20
    }
    grep -q '^loaded=1$' "$STATS" || {
      echo "FAIL gate stats do not report loaded=1"
      exit 21
    }
    grep -q '^owner_protocol=2$' "$STATS" || exit 24
    grep -q '^owner_lock_ready=1$' "$STATS" || exit 25
    GP=$(awk -F= '$1=="gate_pid"{print $2}' "$STATS")
    case "$GP" in ''|*[!0-9]*) exit 26 ;; esac
    [ "$GP" -gt 1 ] && kill -0 "$GP" 2>/dev/null || exit 27
    pidin ar 2>/dev/null | awk -v p="$GP" '$1==p {e=$2;sub(/^.*\//,"",e);if(e=="displaymanager")found=1} END{exit !found}' || exit 28
    TF=$(awk -F= '$1=="tracked_fds"{print $2}' "$STATS")
    case "$TF" in ''|*[!0-9]*) exit 29 ;; esac
    [ "$TF" -gt 0 ] || exit 30
    touch "$MARKER" || exit 22
    echo "isoTX2 gate: DIRECT requested"
    ;;
  stock)
    rm -f "$MARKER" 2>/dev/null || true
    echo "isoTX2 gate: STOCK requested"
    ;;
  reset)
    touch "$RESET" || exit 23
    echo "isoTX2 gate: counter reset requested"
    ;;
  status)
    ;;
  *)
    echo "Usage: $0 {direct|stock|reset|status}"
    exit 2
    ;;
esac

[ -e "$MARKER" ] && echo "requested_mode=DIRECT" || echo "requested_mode=STOCK"
if [ -r "$STATS" ]; then
  echo "--- gate stats ---"
  cat "$STATS"
else
  echo "gate_stats=absent"
fi
if [ -r "$LOGFILE" ]; then
  echo "--- gate log tail ---"
  tail -20 "$LOGFILE" 2>/dev/null || cat "$LOGFILE"
fi
