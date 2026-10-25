#!/bin/ksh
# Live, read-only MU1440 stock keypanel capture.
#
# Session 1:
#   ksh keypanel_capture.sh --auto
#
# If no supported stock reader is auto-detected:
#   <proven-stock-reader-command> | ksh keypanel_capture.sh --stdin
#
# Session 2:
#   ksh keypanel_note.sh
#
# Writes only to /tmp by default. Override with MIBR_KEYPANEL_OUT=/writable/path.
set -u

MODE=${1:---auto}
BASE=${MIBR_KEYPANEL_OUT:-/tmp}
SESSION="$BASE/mibr-keypanel-$$"
POINTER=/tmp/mibr-keypanel-current
LOG="$SESSION/keypanel.log"
META="$SESSION/meta.txt"

stamp(){
  S=$(date '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
  [ -n "$S" ] || S=$(date 2>/dev/null)
  [ -n "$S" ] || S=NO_DATE
  echo "$S"
}

key_name(){
  case "$1" in
    35) echo KEY_MFW_MENU ;;
    36) echo KEY_MFW_ARROW_RIGHT ;;
    37) echo KEY_MFW_ARROW_LEFT ;;
    38) echo KEY_MFW_UP ;;
    39) echo KEY_MFW_DOWN ;;
    40) echo KEY_MFW_ROLLER_LEFT ;;
    41) echo KEY_MFW_CANCEL ;;
    42) echo KEY_MFW_VOLUME_UP ;;
    43) echo KEY_MFW_VOLUME_DOWN ;;
    44) echo KEY_MFW_ROLLER_RIGHT ;;
    45) echo KEY_MFW_AUDIOSOURCE ;;
    46) echo KEY_MFW_ARROW_A_UP ;;
    47) echo KEY_MFW_ARROW_A_DOWN ;;
    48) echo KEY_MFW_ARROW_B_UP ;;
    49) echo KEY_MFW_ARROW_B_DOWN ;;
    50) echo KEY_MFW_PTT_ON ;;
    51) echo KEY_MFW_PTT_CANCEL ;;
    52) echo KEY_MFW_INFO ;;
    53) echo KEY_MFW_HOOK ;;
    54) echo KEY_MFW_HANGUP ;;
    55) echo KEY_MFW_OFFHOOK ;;
    56) echo KEY_MFW_LIGHT ;;
    57) echo KEY_MFW_MUTE ;;
    58) echo KEY_MFW_JOKER1 ;;
    59) echo KEY_MFW_JOKER2 ;;
    60) echo KEY_MFW_INIT ;;
    99) echo KEY_MFW_SIDEMENULEFT ;;
    100) echo KEY_MFW_SIDEMENURIGHT ;;
    114) echo KEY_SMARTPHONE ;;
    116) echo KEY_HOME ;;
    *) echo KEY_UNKNOWN ;;
  esac
}

state_name(){
  case "$1" in
    0) echo RELEASED ;;
    1) echo PRESSED ;;
    2) echo DOUBLEPRESSED ;;
    3) echo LONGPRESSED ;;
    4) echo LONGPRESSED2 ;;
    5) echo LONGPRESSED3 ;;
    6) echo APPROACHED ;;
    7) echo ABANDONED ;;
    8) echo MOVED ;;
    *) echo STATE_UNKNOWN ;;
  esac
}

cleanup(){
  if [ -r "$POINTER" ]; then
    CUR=$(cat "$POINTER" 2>/dev/null)
    [ "$CUR" = "$SESSION" ] && rm -f "$POINTER" 2>/dev/null
  fi
  echo
  echo "KEYPANEL_CAPTURE=STOPPED"
  echo "session=$SESSION"
  echo "log=$LOG"
}
trap cleanup 0
trap 'exit 129' 1
trap 'exit 130' 2
trap 'exit 143' 15

mkdir -p "$SESSION" || {
  echo "ERROR cannot create session directory: $SESSION"
  exit 2
}
: > "$LOG" || {
  echo "ERROR cannot create log: $LOG"
  exit 2
}
echo "$SESSION" > "$POINTER" || {
  echo "ERROR cannot publish current session pointer: $POINTER"
  exit 2
}

{
  echo "mode=$MODE"
  echo "session=$SESSION"
  echo "started=$(stamp)"
  echo "target=MU1440_STOCK_KEYPANEL_LOG"
  echo "writes=SESSION_OUTPUT_ONLY"
} > "$META"

echo "=== MU1440 LIVE KEYPANEL CAPTURE ==="
echo "session=$SESSION"
echo "log=$LOG"
echo "pointer=$POINTER"
echo
echo "Open a second SSH session and run:"
echo "  ksh runtime/diagnostics/keypanel_note.sh"
echo
echo "Type the physical action there BEFORE pressing it, for example:"
echo "  VIEW kurz"
echo "  VIEW lang bis Auswahlmenue"
echo "  Assistenz kurz"
echo "  rechtes Rad Druck"
echo
echo "Ctrl+C stops capture."
echo

filter_loop(){
  while IFS= read -r LINE
  do
    case "$LINE" in
      *"HK Received:"*)
        PAYLOAD=${LINE#*HK Received: }
        set -- $(echo "$PAYLOAD" | awk -F'[][]' '{print $2, $4, $6}')
        [ "$#" -ge 3 ] || continue
        KBD=$1
        KEY=$2
        KST=$3
        case "$KBD:$KEY:$KST" in
          *[!0-9:]*|::*|*::*) continue ;;
        esac
        TS=$(stamp)
        KN=$(key_name "$KEY")
        SN=$(state_name "$KST")
        echo "$TS $LINE" >> "$LOG"
        echo "$TS EVENT KBD[$KBD] KEY[$KEY] $KN KST[$KST] $SN"
        ;;
    esac
  done
}

pick_sloginfo(){
  for P in /proc/boot/sloginfo /bin/sloginfo /usr/bin/sloginfo /sbin/sloginfo
  do
    if [ -x "$P" ]; then
      echo "$P"
      return 0
    fi
  done
  return 1
}

case "$MODE" in
  --stdin)
    echo "source=stdin" >> "$META"
    filter_loop
    ;;
  --auto|--sloginfo)
    SLOG=$(pick_sloginfo)
    if [ -z "$SLOG" ]; then
      echo "ERROR no sloginfo reader found in known paths."
      echo "Run runtime/diagnostics/keypanel_trace_discovery.sh and use:"
      echo "  <proven-reader-command> | ksh runtime/diagnostics/keypanel_capture.sh --stdin"
      exit 3
    fi
    echo "source=$SLOG -w" >> "$META"
    echo "source=$SLOG -w"
    "$SLOG" -w 2>/dev/null | filter_loop
    ;;
  --help|-h)
    echo "usage:"
    echo "  ksh keypanel_capture.sh --auto"
    echo "  <reader> | ksh keypanel_capture.sh --stdin"
    exit 0
    ;;
  *)
    echo "ERROR unknown mode: $MODE"
    echo "Use --auto, --sloginfo or --stdin."
    exit 2
    ;;
esac
