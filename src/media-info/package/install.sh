#!/bin/ksh
set -u
case "$0" in */*) ROOT=${0%/*};; *) ROOT=.;; esac
ROOT=$(cd "$ROOT" && pwd) || exit 2
. "$ROOT/hashes.sh" || exit 2
MODE=${1:---check}
BASE=/mnt/app/root/altscreen-u2
TARGET=/mnt/app/eso/hmi/lsd/lsd.sh
JAR=$BASE/seat-media/seat-media.jar
BACK=$BASE/backup/seat-media-v01
SHA=$BASE/bin/sha256sum
RW=0
fail(){ echo "MEDIA_INSTALL=FAIL $*";exit 20; }
digest(){ LINE=$("$SHA" "$1") || return 1;echo "$LINE" | awk '{print $1}'; }
verify(){ [ -f "$1" ] && [ ! -L "$1" ] && [ "$(digest "$1")" = "$2" ] || fail "unexpected_bytes=$1"; }
finish(){ RC=$?;trap - 0;if [ "$RW" -eq 1 ];then sync;mount -ur /mnt/app || { echo MEDIA_INSTALL=FAIL app_readonly;RC=35; };fi;exit "$RC"; }
trap finish 0
trap 'exit 130' 1 2 15
case "$MODE" in --check|--apply|--restore-check|--restore) ;; *) fail usage;;esac
for C in awk cat cp chmod mv mkdir mount sync;do command -v "$C" >/dev/null 2>&1 || fail "missing_command=$C";done
[ -x "$SHA" ] || fail sha_missing
verify /ifs/lsd.jxe "$OEM_JXE_SHA"
verify "$ROOT/payload/seat-media.jar" "$MEDIA_JAR_SHA"
verify "$ROOT/payload/startup-before.sh" "$STARTUP_BEFORE_SHA"
verify "$ROOT/payload/startup-after.sh" "$STARTUP_AFTER_SHA"
[ -f "$TARGET" ] && [ ! -L "$TARGET" ] || fail startup_not_regular
CURRENT=$(digest "$TARGET") || fail startup_unreadable
case "$CURRENT" in "$STARTUP_BEFORE_SHA"|"$STARTUP_AFTER_SHA") ;; *) fail unknown_startup_preserved;;esac
[ ! -L "$BASE/seat-media" ] && [ ! -L "$BACK" ] || fail symlink_preserved
if [ -e "$BACK" ];then verify "$BACK/lsd.sh" "$STARTUP_BEFORE_SHA";fi
if [ -e "$JAR" ] || [ -L "$JAR" ];then verify "$JAR" "$MEDIA_JAR_SHA";fi
case "$MODE" in
 --check|--apply)
  (unset LD_PRELOAD
   export LD_LIBRARY_PATH=/ifs/jre/bin:/mnt/app/root/lib-target:/mnt/app/armle/lib:/mnt/app/armle/usr/lib:/mnt/app/armle/lib/dll:/mnt/app/eso/lib:/navigation:/navigation/lib
   /ifs/jre/bin/j9 -jcl:foun11 -verify -Xmx12m -Xbootclasspath/a:/ifs/lsd.jxe -Xbootclasspath/p:"$ROOT/payload/seat-media.jar" de.mibr.media.MediaProbe) || fail target_j9_probe
  SOURCE=$ROOT/payload/startup-after.sh; EXPECTED=$STARTUP_AFTER_SHA;;
 *) SOURCE=$ROOT/payload/startup-before.sh; EXPECTED=$STARTUP_BEFORE_SHA;;
esac
case "$MODE" in --check|--restore-check) echo "MEDIA_PREFLIGHT=PASS persistent_writes=0 visible_effect=UNTESTED";exit 0;;esac
if [ "$CURRENT" = "$EXPECTED" ];then
 if [ "$MODE" = --apply ];then verify "$JAR" "$MEDIA_JAR_SHA";fi
 echo "MEDIA_INSTALL=ALREADY_SELECTED RESTART_REQUIRED=YES";exit 0
fi
[ ! -e "$TARGET.media-new" ] && [ ! -L "$TARGET.media-new" ] || fail partial_stage_preserved
[ ! -e "$JAR.new" ] && [ ! -L "$JAR.new" ] || fail partial_jar_preserved
[ ! -e "$BACK.preparing" ] && [ ! -L "$BACK.preparing" ] || fail partial_backup_preserved
if [ "$MODE" = --restore ];then verify "$BACK/lsd.sh" "$STARTUP_BEFORE_SHA";fi
mount -uw /mnt/app || fail mount_writable
RW=1
if [ "$MODE" = --apply ];then
 if [ ! -e "$BACK" ];then
  mkdir -p "$BASE/backup" || fail backup_parent
  mkdir "$BACK.preparing" || fail backup_directory
  cp "$TARGET" "$BACK.preparing/lsd.sh" || fail backup_copy
  verify "$BACK.preparing/lsd.sh" "$STARTUP_BEFORE_SHA"
  sync;mv "$BACK.preparing" "$BACK" || fail backup_commit
 fi
 mkdir -p "$BASE/seat-media" || fail payload_directory
 cp "$ROOT/payload/seat-media.jar" "$JAR.new" || fail jar_copy
 chmod 644 "$JAR.new" || fail jar_permissions
 verify "$JAR.new" "$MEDIA_JAR_SHA"
 sync;mv "$JAR.new" "$JAR" || fail jar_commit
fi
cp "$SOURCE" "$TARGET.media-new" || fail startup_copy
chmod 755 "$TARGET.media-new" || fail startup_permissions
verify "$TARGET.media-new" "$EXPECTED"
sync;mv "$TARGET.media-new" "$TARGET" || fail startup_commit
sync;verify "$TARGET" "$EXPECTED"
echo "MEDIA_INSTALL=PASS RESTART_REQUIRED=YES mode=$MODE video_owner_unchanged=1 visible_effect=UNTESTED"
