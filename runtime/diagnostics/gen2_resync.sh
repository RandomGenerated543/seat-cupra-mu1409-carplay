#!/bin/ksh
set -u

ENABLE=/tmp/mibr-alt111-resync.enabled
ARM=/tmp/mibr-alt111-resync-arm
STATUS=/tmp/mibr-alt111-gen2.status

usage(){
  echo "usage: $0 status|on|off|arm"
  exit 2
}

cmd=${1:-status}
case "$cmd" in
  status)
    [ -e "$ENABLE" ] && echo "CANDIDATE_D_MANUAL=ENABLED" || echo "CANDIDATE_D_MANUAL=DISABLED"
    if [ -r "$STATUS" ]; then
      grep '^resync_' "$STATUS" 2>/dev/null || true
      grep '^mode_' "$STATUS" 2>/dev/null || true
    else
      echo "GEN2_CORE_STATUS=NOT_AVAILABLE"
    fi
    ;;
  on)
    touch "$ENABLE" || exit 1
    sync
    echo "CANDIDATE_D_MANUAL=ENABLED (volatile; resets on reboot)"
    echo "Auto-arm remains OFF. Use '$0 arm' only on the frozen/stale same-stream state."
    ;;
  off)
    rm -f "$ARM" "$ENABLE"
    sync
    echo "CANDIDATE_D_MANUAL=DISABLED"
    echo "Any active NEED_IDR state will be cancelled by the GEN2 worker."
    ;;
  arm)
    if [ ! -e "$ENABLE" ]; then
      echo "REFUSED: Candidate D manual feature is disabled. Run '$0 on' first."
      exit 1
    fi
    touch "$ARM" || exit 1
    sync
    echo "CANDIDATE_D_ARM=QUEUED"
    echo "GEN2 will request forceKeyFrame on the existing stream and complete only after a newer source IDR."
    ;;
  *)
    usage
    ;;
esac
