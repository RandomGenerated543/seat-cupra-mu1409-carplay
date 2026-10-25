#!/bin/ksh
# SPDX-License-Identifier: GPL-3.0-or-later
. /mnt/app/root/altscreen-u2/scripts/common.sh
runtime_init || exit 3
runtime_require_cmds on pidin awk cat sleep mkdir rm touch || exit 4
LOCK=/fs/tmpfs/mibr-direct-start.lock
[ -x "$BASE/bin/owner-unlock" ] || { echo "START=FAIL_UNLOCK_HELPER"; exit 19; }
mkdir "$LOCK" 2>/dev/null || { echo "START=BUSY"; exit 20; }
trap '"$BASE/bin/owner-unlock"' 0
if [ -r /tmp/mibr-direct-auto-supervisor.pid ]; then
 P=$(cat /tmp/mibr-direct-auto-supervisor.pid)
 case "$P" in ''|*[!0-9]*) ;; *) kill -0 "$P" 2>/dev/null && { echo "START=ALREADY_RUNNING"; exit 0; } ;; esac
fi
"$BASE/bin/owner-probe" || { echo "START=FAIL_OWNER_PROTOCOL"; exit 21; }
navignore_active || { echo "START=FAIL_NAVIGATION_PREREQUISITE"; exit 22; }
"$BASE/scripts/writev_gate.sh" stock || exit 23
rm -f /tmp/mibr-direct-stopping
# D2 recovery is session-only; do not alter persistent M.I.B. or Java state.
touch /tmp/mibr-alt111-keyframe-policy.enabled /tmp/mibr-carplay-autodirect.enabled || exit 24
on -d -f mmx /bin/ksh "$BASE/scripts/direct_ts_auto_watchdog.sh" > /tmp/mibr-direct-auto-watchdog-launch.log 2>&1 || exit 25
on -d -f mmx /bin/ksh "$BASE/scripts/direct_ts_auto_supervisor.sh" > /tmp/mibr-direct-auto-supervisor-launch.log 2>&1 || exit 26
echo "AUTO_DIRECT_START=REQUESTED"
echo "Use status and visible output to confirm actual DIRECT operation."
exit 0
