#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
set -u

MARK=/tmp/mibr-alt111-gen2-reacquire
rm -f "$MARK" 2>/dev/null || true
touch "$MARK" || { echo "GEN2_REACQUIRE=FAIL_TOUCH"; exit 2; }

echo "GEN2_REACQUIRE=REQUESTED"
i=0
while [ $i -lt 20 ]; do
  [ ! -e "$MARK" ] && break
  i=$((i+1))
  if command -v usleep >/dev/null 2>&1; then usleep 100000; else sleep 1; fi
done

if [ -e "$MARK" ]; then
  echo "GEN2_REACQUIRE=NOT_CONSUMED"
  exit 3
fi

echo "GEN2_REACQUIRE=CONSUMED"
cat /tmp/mibr-alt111-gen2.status 2>/dev/null || true
echo
tail -100 /tmp/altscreen111.log 2>/dev/null || true
