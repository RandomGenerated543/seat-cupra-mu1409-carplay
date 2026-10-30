#!/bin/ksh
case "${1:---status}" in
 --status)
  if [ -r /tmp/mibr-seat-media.status ];then cat /tmp/mibr-seat-media.status;else echo MEDIA_STATUS=NOT_OBSERVED_AFTER_BOOT;fi;;
 --log)
  if [ -r /tmp/mibr-seat-media.log ];then cat /tmp/mibr-seat-media.log;else echo MEDIA_LOG=MISSING;fi;;
 *) echo 'Usage: control.sh --status | --log';exit 2;;
esac
