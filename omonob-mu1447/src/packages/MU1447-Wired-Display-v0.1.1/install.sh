#!/bin/ksh
# Wired MU1447 only. No wireless payload or activation changes.
case "$0" in */*) HERE=$(cd "${0%/*}" && pwd) ;; *) HERE=$PWD ;; esac
P=$HERE/payload
ROOT=/mnt/app/carplaymaps
CORE=$ROOT/core.so
WRAPPER=$ROOT/dio_manager.wrapper.sh
DIO=/mnt/app/eso/bin/apps/dio_manager
ADDON=$ROOT/libmu1447-wired-display.so
BACKUP=/mnt/app/.mu1447-wired-display-v011
CHECK=/ramdisk/mu1447-wired-check-$$
LOAD=/ramdisk/mu1447-wired-load-$$.so
LOCK=/ramdisk/mu1447-wired-display.lock
LOCKED=0
STAGED_FILES=""
ACTION=${1:---status}
fail() { echo "WIRED_DISPLAY=FAIL reason=$1"; exit 1; }
cleanup() {
    rm -f "$CHECK" "$LOAD"
    for STAGED_FILE in $STAGED_FILES; do rm -f "$STAGED_FILE"; done
    [ "$LOCKED" = 0 ] || rm -f "$LOCK"
    :
}
trap cleanup 0
trap 'exit 1' 1 2 15
[ "$#" -le 1 ] || fail too_many_arguments
case "$ACTION" in --check|--status|--apply|--restore) ;; *) fail use_check_status_apply_restore ;; esac
for TOOL in cp chmod ls mount mkdir mv rm sync; do
    command -v "$TOOL" >/dev/null 2>&1 || fail missing_command_$TOOL
done
echo 'WIRED_DISPLAY=CHECKING_FIRMWARE'
set -- $(ls -ln /ifs/lsd.jxe 2>/dev/null)
[ "$5" = 55712574 ] || fail unsupported_firmware
IFS= read -r PROFILE < "$ROOT/PROFILE" || fail missing_wired_profile
[ "$PROFILE" = MU1447/790 ] || fail wrong_wired_profile
[ -x "$ROOT/stock_first/dio_manager.real" ] || fail wired_installation_not_present
for F in file-check core-original.so core-display.so wrapper-original.sh wrapper-display.sh libmu1447-wired-display.so; do
    [ -s "$P/$F" ] || fail missing_payload_$F
done
cp "$P/file-check" "$CHECK" || fail stage_checker
chmod 755 "$CHECK" || fail checker_permissions
same() { "$CHECK" --same "$1" "$2" >/dev/null 2>&1; }
same "$P/core-original.so" "$P/core-original.so" || fail checker_not_executable
classify() {
    if same "$1" "$2"; then echo ORIGINAL;
    elif same "$1" "$3"; then echo PATCHED;
    else echo UNKNOWN; fi
}
CS=$(classify "$CORE" "$P/core-original.so" "$P/core-display.so")
WS=$(classify "$WRAPPER" "$P/wrapper-original.sh" "$P/wrapper-display.sh")
DS=$(classify "$DIO" "$P/wrapper-original.sh" "$P/wrapper-display.sh")
echo "WIRED_DISPLAY_FILES core=$CS runtime_launcher=$WS active_launcher=$DS"
case "$CS:$WS:$DS" in
    UNKNOWN:*) fail unsupported_wired_core ;;
    *:UNKNOWN:*) fail unsupported_runtime_launcher ;;
    *:UNKNOWN) fail unsupported_active_launcher ;;
esac
if [ -e "$ADDON" ]; then
    same "$ADDON" "$P/libmu1447-wired-display.so" || fail unknown_existing_addon
fi
if [ -d "$BACKUP" ]; then
    [ -f "$BACKUP/complete" ] || fail incomplete_backup_keep_files
    same "$BACKUP/core.so" "$P/core-original.so" || fail backup_core_mismatch
    same "$BACKUP/wrapper.sh" "$P/wrapper-original.sh" || fail backup_wrapper_mismatch
    same "$BACKUP/dio_manager" "$P/wrapper-original.sh" || fail backup_dio_mismatch
    [ -f "$BACKUP/addon-was-missing" ] || fail backup_state_missing
fi
case "$CS:$WS:$DS" in
    ORIGINAL:ORIGINAL:ORIGINAL) STATE=ORIGINAL ;;
    PATCHED:PATCHED:PATCHED)
        if [ -f "$BACKUP/complete" ] && [ -s "$ADDON" ]; then STATE=PATCHED;
        else STATE=PARTIAL_RESTORE_REQUIRED; fi ;;
    *) STATE=PARTIAL_RESTORE_REQUIRED ;;
esac
case "$ACTION" in
    --check|--status)
        if [ "$ACTION" = --check ]; then
            cp "$P/libmu1447-wired-display.so" "$LOAD" || fail stage_load_check
            chmod 755 "$LOAD" || fail load_check_permissions
            "$CHECK" --load "$LOAD" || fail addon_cannot_load
        fi
        echo "WIRED_DISPLAY_CHECK=PASS state=$STATE persistent_writes=0"
        echo 'SETTINGS zoom=70 safe=628x220@191,56 views=0,4 showETA=yes maneuverLayout=automatic'
        echo 'VISIBLE_OUTPUT=UNTESTED_BY_SCRIPT'
        exit 0 ;;
esac
(umask 077; set -C; : > "$LOCK") 2>/dev/null || fail operation_lock_exists
LOCKED=1
[ ! -e /dev/ipod0 ] && [ ! -e /dev/shmem/wcp_cp_session ] || fail disconnect_carplay_first
if [ "$ACTION" = --apply ]; then
    [ "$STATE" != PARTIAL_RESTORE_REQUIRED ] || fail restore_partial_install_first
    if [ ! -d "$BACKUP" ] && [ -e "$ADDON" ]; then fail addon_present_without_our_backup; fi
    cp "$P/libmu1447-wired-display.so" "$LOAD" || fail stage_load_check
    chmod 755 "$LOAD" || fail load_check_permissions
    "$CHECK" --load "$LOAD" || fail addon_cannot_load
else
    [ -f "$BACKUP/complete" ] || fail no_backup
fi
mount -uw /mnt/app || fail remount_app
if [ "$ACTION" = --apply ] && [ ! -d "$BACKUP" ]; then
    mkdir "$BACKUP" || fail create_backup
    cp -p "$CORE" "$BACKUP/core.so" || fail backup_core
    cp -p "$WRAPPER" "$BACKUP/wrapper.sh" || fail backup_wrapper
    cp -p "$DIO" "$BACKUP/dio_manager" || fail backup_dio
    same "$BACKUP/core.so" "$P/core-original.so" || fail verify_backup_core
    same "$BACKUP/wrapper.sh" "$P/wrapper-original.sh" || fail verify_backup_wrapper
    same "$BACKUP/dio_manager" "$P/wrapper-original.sh" || fail verify_backup_dio
    : > "$BACKUP/addon-was-missing" || fail backup_addon_marker
    : > "$BACKUP/complete" || fail backup_completion_marker
    sync
fi
stage() {
    [ ! -e "$2.wired-new" ] || fail pending_stage_file_$2
    STAGED_FILES="$STAGED_FILES $2.wired-new"
    cp "$1" "$2.wired-new" || fail stage_copy_$2
    chmod "$3" "$2.wired-new" || fail stage_permissions_$2
    same "$1" "$2.wired-new" || fail stage_compare_$2
}
if [ "$ACTION" = --restore ]; then
    # Disable preload references before removing the add-on.
    stage "$BACKUP/dio_manager" "$DIO" 755
    stage "$BACKUP/wrapper.sh" "$WRAPPER" 755
    stage "$BACKUP/core.so" "$CORE" 644
    mv -f "$DIO.wired-new" "$DIO" || fail restore_dio
    mv -f "$WRAPPER.wired-new" "$WRAPPER" || fail restore_wrapper
    mv -f "$CORE.wired-new" "$CORE" || fail restore_core
    rm -f "$ADDON" || fail remove_addon
    same "$CORE" "$P/core-original.so" && same "$DIO" "$P/wrapper-original.sh" && same "$WRAPPER" "$P/wrapper-original.sh" || fail restore_final_check
    sync
    echo 'WIRED_DISPLAY=RESTORED restart_manually=1 backup_retained=1'
    exit 0
fi
# Stage and compare every file before activating any new file.
stage "$P/libmu1447-wired-display.so" "$ADDON" 755
stage "$P/core-display.so" "$CORE" 644
stage "$P/wrapper-display.sh" "$WRAPPER" 755
stage "$P/wrapper-display.sh" "$DIO" 755
mv -f "$ADDON.wired-new" "$ADDON" || fail activate_addon
mv -f "$CORE.wired-new" "$CORE" || fail activate_core
mv -f "$WRAPPER.wired-new" "$WRAPPER" || fail activate_wrapper
mv -f "$DIO.wired-new" "$DIO" || fail activate_dio
same "$ADDON" "$P/libmu1447-wired-display.so" && same "$CORE" "$P/core-display.so" && same "$DIO" "$P/wrapper-display.sh" && same "$WRAPPER" "$P/wrapper-display.sh" || fail final_compare
sync
echo 'WIRED_DISPLAY=INSTALLED zoom=70 safe=628x220@191,56 showETA=yes restart_manually=1 visible=UNTESTED'
