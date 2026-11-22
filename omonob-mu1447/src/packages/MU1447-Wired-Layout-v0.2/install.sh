#!/bin/ksh
case "$0" in */*) HERE=$(cd "${0%/*}" && pwd) ;; *) HERE=$PWD ;; esac
P=$HERE/payload
ROOT=/mnt/app/carplaymaps
CORE=$ROOT/core.so
BACKUP=/mnt/app/.mu1447-wired-layout-v02
CHECK=/ramdisk/mu1447-layout-check-$$
LOCK=/ramdisk/mu1447-wired-layout.lock
NEW=$CORE.layout-new
LOCKED=0
STAGED=0
ACTION=${1:---check}
fail() { echo "WIRED_LAYOUT=FAIL reason=$1"; exit 1; }
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
for F in core-layout.so core-display-v011.so core-eta-v01.so file-check wrapper-display.sh libmu1447-wired-display.so; do
    [ -s "$P/$F" ] || fail missing_payload_$F
done
cp "$P/file-check" "$CHECK" || fail stage_checker
chmod 755 "$CHECK" || fail checker_permissions
same() { "$CHECK" --same "$1" "$2" >/dev/null 2>&1; }
same "$P/core-layout.so" "$P/core-layout.so" || fail checker_not_executable
known_before() {
    same "$1" "$P/core-display-v011.so" || same "$1" "$P/core-eta-v01.so"
}
if known_before "$CORE"; then STATE=BEFORE;
elif same "$CORE" "$P/core-layout.so"; then STATE=CORRECTED;
else fail installed_core_mismatch; fi
same "$ROOT/dio_manager.wrapper.sh" "$P/wrapper-display.sh" || fail runtime_launcher_mismatch
same /mnt/app/eso/bin/apps/dio_manager "$P/wrapper-display.sh" || fail active_launcher_mismatch
same "$ROOT/libmu1447-wired-display.so" "$P/libmu1447-wired-display.so" || fail working_zoom_library_mismatch
if [ -d "$BACKUP" ]; then
    known_before "$BACKUP/core-before.so" || fail backup_mismatch
fi
case "$ACTION" in --check|--status)
    echo "WIRED_LAYOUT_CHECK=PASS state=$STATE persistent_writes=0"
    echo 'OFF=original_geometry ETA=yes maneuverLayout=no'
    echo 'CENTER=view3 safe=628x185@191,56 ETA=yes topAligned'
    echo 'LEFT=view1 safe=606x252@202,45 lower_edge_raised=20 ETA=yes leftAligned'
    echo 'ZOOM=70 retained=1'
    exit 0 ;;
esac
(umask 077; set -C; : > "$LOCK") 2>/dev/null || fail operation_lock_exists
LOCKED=1
[ ! -e /dev/ipod0 ] && [ ! -e /dev/shmem/wcp_cp_session ] || fail disconnect_carplay_first
if [ "$ACTION" = --restore ]; then
    [ -s "$BACKUP/core-before.so" ] || fail missing_backup
    SOURCE=$BACKUP/core-before.so
else
    [ "$STATE" = BEFORE ] || [ -s "$BACKUP/core-before.so" ] || fail corrected_core_without_backup
    SOURCE=$P/core-layout.so
fi
mount -uw /mnt/app || fail remount_app
if [ "$ACTION" = --apply ] && [ ! -d "$BACKUP" ]; then
    mkdir "$BACKUP" || fail create_backup
    cp -p "$CORE" "$BACKUP/core-before.so" || fail backup_copy
    known_before "$BACKUP/core-before.so" || fail backup_verify
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
    echo 'WIRED_LAYOUT=RESTORED restart_manually=1'
else
    echo 'WIRED_LAYOUT=INSTALLED off=ETA_only center=628x185@191,56 left_raised=20 zoom=70 restart_manually=1 visible=UNTESTED'
fi
