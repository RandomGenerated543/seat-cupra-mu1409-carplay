#!/bin/ksh
# Separate SSH session. Appends NOTE to active native capture, one append per entry.
set -u
SELF=./mibr-keypanel-native
if [ ! -x "$SELF" ]; then
  echo "ERROR: mibr-keypanel-native missing; cd into installed logger directory first."
  exit 2
fi
if [ ! -r ./mibr-keypanel-native-current ]; then
  echo "ERROR: no native capture is active. Start shell 1 first."
  exit 2
fi
echo "=== MIBR KEY PANEL / COMMENT CONSOLE ==="
echo "Use your numbered steering wheel reference; type BEFORE pressing."
echo "Examples: 6 kurz; 6 lang; 7 Rad rechts +1; 8 drücken"
echo "Also record the OEM effect: 6 OEM-Auswahlmenue sichtbar"
echo "Type /quit to end just this comment console."
while IFS= read -r LINE
do
  case "$LINE" in
    /quit|exit|quit) break ;;
    "") continue ;;
    *) "$SELF" --note "$LINE" ;;
  esac
done