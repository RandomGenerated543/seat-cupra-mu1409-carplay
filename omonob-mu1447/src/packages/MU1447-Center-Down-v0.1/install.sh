#!/bin/ksh
case "$0" in */*) HERE=$(cd "${0%/*}" && pwd) ;; *) HERE=$PWD ;; esac
P=$HERE/payload
CORE=/mnt/app/carplaymaps/core.so
BACKUP=/mnt/app/.mu1447-center-down-v01
CHECK=/ramdisk/mu1447-center-check-$$
LOCK=/ramdisk/mu1447-center-down.lock
NEW=$CORE.center-new
LOCKED=0
STAGED=0
ACTION=${1:---check}
fail() { echo "WIRED_CENTER=FAIL reason=$1"; exit 1; }
cleanup() {
    rm -f "$CHECK"
    [ "$STAGED" = 0 ] || rm -f "$NEW"
    [ "$LOCKED" = 0 ] || rm -f "$LOCK"
    :
}
trap cleanup 0
trap 'exit 1' 1 2 15
[ "$#" -le 1 ] || fail too_many_arguments
case "$ACTION" in --check|--status|--apply|--restore) ;; *) fail invalid_action ;; esac
for F in core-before.so core-center.so file-check; do [ -s "$P/$F" ] || fail missing_payload_$F; done
cp "$P/file-check" "$CHECK" || fail stage_checker
chmod 755 "$CHECK" || fail checker_permissions
same() { "$CHECK" --same "$1" "$2" >/dev/null 2>&1; }
same "$P/core-before.so" "$P/core-before.so" || fail checker_not_executable
if same "$CORE" "$P/core-before.so"; then STATE=BEFORE;
elif same "$CORE" "$P/core-center.so"; then STATE=LOWERED;
else fail installed_core_mismatch; fi
if [ -d "$BACKUP" ]; then
    same "$BACKUP/core-before.so" "$P/core-before.so" || fail backup_mismatch
fi
case "$ACTION" in --check|--status)
    echo "WIRED_CENTER_CHECK=PASS state=$STATE persistent_writes=0"
    exit 0 ;;
esac
(umask 077; set -C; : > "$LOCK") 2>/dev/null || fail operation_lock_exists
LOCKED=1
[ ! -e /dev/ipod0 ] && [ ! -e /dev/shmem/wcp_cp_session ] || fail disconnect_carplay_first
if [ "$ACTION" = --restore ]; then
    [ -s "$BACKUP/core-before.so" ] || fail missing_backup
    SOURCE=$BACKUP/core-before.so
else
    [ "$STATE" = BEFORE ] || [ -s "$BACKUP/core-before.so" ] || fail lowered_core_without_backup
    SOURCE=$P/core-center.so
fi
mount -uw /mnt/app || fail remount_app
if [ "$ACTION" = --apply ] && [ ! -d "$BACKUP" ]; then
    mkdir "$BACKUP" || fail create_backup
    cp -p "$CORE" "$BACKUP/core-before.so" || fail backup_copy
    same "$BACKUP/core-before.so" "$P/core-before.so" || fail backup_verify
    sync
fi
[ ! -e "$NEW" ] || fail pending_stage_exists
STAGED=1
cp "$SOURCE" "$NEW" || fail stage_core
chmod 644 "$NEW" || fail stage_permissions
same "$SOURCE" "$NEW" || fail stage_verify
mv -f "$NEW" "$CORE" || fail activate_core
same "$SOURCE" "$CORE" || fail final_verify
sync
if [ "$ACTION" = --restore ]; then
    echo 'WIRED_CENTER=RESTORED center=628x185@191,56 restart_manually=1'
else
    echo 'WIRED_CENTER=INSTALLED center=628x185@191,76 moved_down=20 restart_manually=1 visible=UNTESTED'
fi
