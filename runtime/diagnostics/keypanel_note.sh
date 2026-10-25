#!/bin/ksh
# Second-SSH annotation console for keypanel_capture.sh.
set -u

POINTER=/tmp/mibr-keypanel-current

stamp(){
  S=$(date '+%Y-%m-%dT%H:%M:%S' 2>/dev/null)
  [ -n "$S" ] || S=$(date 2>/dev/null)
  [ -n "$S" ] || S=NO_DATE
  echo "$S"
}

if [ ! -r "$POINTER" ]; then
  echo "ERROR no active keypanel capture pointer: $POINTER"
  echo "Start keypanel_capture.sh in the first SSH session."
  exit 2
fi

SESSION=$(cat "$POINTER" 2>/dev/null)
LOG="$SESSION/keypanel.log"

if [ -z "$SESSION" ] || [ ! -f "$LOG" ]; then
  echo "ERROR active capture session is not readable."
  exit 2
fi

add_note(){
  TS=$(stamp)
  echo "$TS NOTE $*" >> "$LOG"
  echo "$TS NOTE $*"
}

if [ "$#" -gt 0 ]; then
  add_note "$*"
  exit 0
fi

echo "=== MU1440 KEYPANEL ANNOTATION CONSOLE ==="
echo "session=$SESSION"
echo
echo "Enter one physical action per line BEFORE you perform it."
echo "Examples:"
echo "  VIEW kurz"
echo "  VIEW lang bis OEM-Menue"
echo "  VIEW sehr lang"
echo "  Assistenz kurz"
echo "  rechtes Rad +1"
echo "  rechtes Rad Druck"
echo
echo "Type /quit to leave this annotation console."
echo

while IFS= read -r LINE
do
  case "$LINE" in
    /quit|quit|exit) break ;;
    "") continue ;;
    *) add_note "$LINE" ;;
  esac
done
