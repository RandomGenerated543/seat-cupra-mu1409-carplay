#!/bin/ksh
set -u
case "${1:---status}" in
 --status)
  for F in /tmp/mibr-seat-r13-boot.log /tmp/mibr-seat-r13-service.log /tmp/mibr-hmi-activation.status /tmp/mibr-seat-settings.status /tmp/mibr-seat-views.status /tmp/mibr-seat-zoom.status;do
   echo "=== $F ===";if [ -r "$F" ];then tail -80 "$F";else echo MISSING;fi
  done
  echo '=== CONTROL LISTENERS ==='
  /usr/sbin/netstat -an | awk '/19831|28743/ && /LISTEN/'
  echo VISIBLE_OUTPUT=OPERATOR_CHECK_REQUIRED
  ;;
 --restore) /bin/ksh /mnt/app/root/altscreen-u2/harman-r13/install.sh --restore ;;
 *) echo 'Usage: control.sh --status|--restore';exit 2 ;;
esac
