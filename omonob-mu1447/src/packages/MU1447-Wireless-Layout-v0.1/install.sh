#!/bin/ksh
# Layout-only transaction: no network, Java, touch or paired-device state changes.
case "$0" in */*) KIT=$(cd "${0%/*}" && pwd);; *) KIT=$PWD;;esac
ACTION=${1:---check}
B=/mnt/app/.mu1447-wireless-layout-v01
S=/ramdisk/mu1447-layout-$$
LOCK=/ramdisk/mu1447-layout.lock
LOCKED=0;STAGED=0;WRITING=0;variant=
cleanup(){ [ "$STAGED" = 0 ] || rm -rf "$S";[ "$LOCKED" = 0 ] || rm -f "$LOCK";:; }
trap cleanup 0
file_hash(){ "$S/file-check" --hash "$1"; }
same(){ a=$(file_hash "$1") && b=$(file_hash "$2") && [ "$a" = "$b" ]; }
select_target(){
 case "$1" in
 receiver) TARGET=/mnt/ota/wcp_receiver;SOURCE=$KIT/payload/receiver-$variant;;
 guard) TARGET=/mnt/app/carplaymaps/wireless-receiver-exec;SOURCE=$KIT/payload/guard-$variant;;
 *)return 1;;esac
}
rollback(){
 for name in receiver guard;do
  select_target "$name" || return 1
  cp -p "$B/$name" "$TARGET.mu1447-layout-restore" &&
  same "$B/$name" "$TARGET.mu1447-layout-restore" &&
  mv -f "$TARGET.mu1447-layout-restore" "$TARGET" || return 1
  same "$B/$name" "$TARGET" || return 1
 done
 sync
}
fail(){
 echo "MU1447_LAYOUT=FAIL reason=$1"
 if [ "$WRITING" = 1 ];then
  WRITING=0
  if rollback;then echo 'MU1447_LAYOUT_AUTO_ROLLBACK=PASS restart_manually=1';else echo 'MU1447_LAYOUT_AUTO_ROLLBACK=FAIL retain_backup';fi
 fi
 exit 1
}
trap 'fail interrupted' 1 2 15
[ "$#" -le 1 ] || fail arguments
case "$ACTION" in --check|--apply|--restore|--status);;*)fail use_check_apply_restore_status;;esac
for cmd in cp mkdir chmod rm mv cat mount sync awk;do command -v "$cmd" >/dev/null 2>&1 || fail missing_command_$cmd;done
[ ! -e "$S" ] && mkdir "$S" || fail ram_stage
STAGED=1
cp "$KIT/file-check" "$S/file-check" && chmod 755 "$S/file-check" || fail checker_stage
"$S/file-check" --self-test && "$S/file-check" --manifest "$KIT" "$KIT/SHA256SUMS.txt" || fail package_integrity
(umask 077;set -C;: > "$LOCK") 2>/dev/null || fail management_lock
LOCKED=1
for p in "$B" /mnt/ota/wcp_receiver /mnt/app/carplaymaps/wireless-receiver-exec;do [ ! -L "$p" ] || fail symlink_target;done
if [ -d "$B" ];then
 [ -f "$B/complete" ] && "$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail incomplete_or_changed_backup
 variant=$(cat "$B/variant")
 case "$variant" in 56|76);;*) fail backup_variant;;esac
fi
if [ "$ACTION" = --restore ];then
 [ -d "$B" ] || fail no_backup
 for name in receiver guard;do
  select_target "$name" || fail backup_target
  same "$TARGET" "$SOURCE" || same "$TARGET" "$B/$name" || fail later_edit_$name
 done
 mount -uw /mnt/app && mount -uw /mnt/ota || fail writable_volumes
 rollback || fail restore
 echo 'MU1447_LAYOUT=RESTORED restart_manually=1'
 exit 0
fi
if [ -d "$B" ];then
 matched=1
 for name in receiver guard;do select_target "$name";same "$TARGET" "$SOURCE" || matched=0;done
 if [ "$matched" = 1 ];then echo "MU1447_LAYOUT=ALREADY_INSTALLED center_y=$variant visible=OPERATOR_CHECK_REQUIRED";exit 0;fi
 fail retained_backup_requires_review
fi
if [ "$ACTION" = --status ];then echo 'MU1447_LAYOUT=NOT_INSTALLED_BY_THIS_PACKAGE';exit 0;fi
[ "$(cat /mnt/app/carplaymaps/PROFILE)" = MU1447/790 ] || fail wrong_profile
CORE=$(file_hash /mnt/app/carplaymaps/core.so) || fail wired_core_missing
variant=$(awk -v h="$CORE" '$1==h {print $2}' "$KIT/WIRED-CORES.tsv")
case "$variant" in 56|76);;*)fail wired_layout_not_recognized;;esac
[ "$(file_hash /mnt/app/carplaymaps/libomonob-wireless-maps.so)" = "$(cat "$KIT/HELPER.sha256")" ] || fail map_helper_changed
while read -r wanted name;do
 select_target "$name" || fail unexpected_target
 [ "$(file_hash "$TARGET")" = "$wanted" ] || fail installed_binary_mismatch_$name
done < "$KIT/BASELINE.sha256"
echo "MU1447_LAYOUT_MATCH=PASS wired_center=628x185@191,$variant zoom=70 initial_view=follows_saved_card"
if [ "$ACTION" = --check ];then echo 'MU1447_LAYOUT_CHECK=PASS persistent_writes=0 visible=UNTESTED';exit 0;fi
mount -uw /mnt/app && mount -uw /mnt/ota || fail writable_volumes
mkdir "$B" || fail backup_create
: > "$B/SEAL.sha256"
for name in receiver guard;do
 select_target "$name" || fail backup_target
 cp -p "$TARGET" "$B/$name" && same "$TARGET" "$B/$name" || fail backup_copy_$name
 echo "$(file_hash "$B/$name")  $name" >> "$B/SEAL.sha256"
done
echo "$variant" > "$B/variant"
echo "$(file_hash "$B/variant")  variant" >> "$B/SEAL.sha256"
"$S/file-check" --manifest "$B" "$B/SEAL.sha256" || fail backup_integrity
: > "$B/complete"
sync
WRITING=1
for name in receiver guard;do
 select_target "$name" || fail install_target
 [ ! -e "$TARGET.mu1447-layout-new" ] || fail existing_stage_$name
 cp "$SOURCE" "$TARGET.mu1447-layout-new" &&
 chmod 755 "$TARGET.mu1447-layout-new" &&
 same "$SOURCE" "$TARGET.mu1447-layout-new" &&
 mv -f "$TARGET.mu1447-layout-new" "$TARGET" || fail install_$name
 same "$SOURCE" "$TARGET" || fail final_readback_$name
done
WRITING=0
sync
echo "MU1447_LAYOUT=INSTALLED center_y=$variant zoom=70 manual_restart_required=1"
echo 'Existing network correction retained. No runtime session was restarted.'
