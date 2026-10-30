# MU1409 cockpit zoom-factor menu candidate

HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY. Vehicle effect UNTESTED.

This updates an exact existing SEAT MU1409 WP1/WP2/R13 stack. It is not a fresh
installer and not qualified for a Skoda firmware. Baseline mismatches stop.

Car HOME > CarPlay settings > Advanced > Cockpit zoom factor (restart).
Choices: 70%, 80%, 90%, 100%, 110%, 120%, 130%, 140%, 150%.
Default (omit) is a separate control value 0 that omits our property.
The existing SEAT default stays 70%. Percentage labels send the exact numeric
CarPlay zoomFactor value; a matching physical size change is app/iOS-dependent.

Selection is saved using the canonical native settings broker and durable
profile transaction. The new value is frozen when the receiver first builds its
display advertisement. Normal unit restart plus a fresh wired CarPlay session
is required. No automatic restart or live map manipulation is added.
SafeAreas, MOST owner, remuxer, wheel zoom, firewall and boot hooks are unchanged.

## Installation

Unplug the phone, leave the settings menu and keep the car parked/powered.
Extract this complete folder to the SD root. Keep KIT.sha256 and payload intact.
Run in the unit SSH terminal:

```sh
/bin/ksh /fs/sda0/MU1409-menu-zoomfactor-v0.1/install.sh --check
```

Stop on any failure. After ZOOM_MENU_CHECK=PASS:

```sh
/bin/ksh /fs/sda0/MU1409-menu-zoomfactor-v0.1/install.sh --apply
```

Expected: ZOOM_MENU_INSTALL=PASS RESTART_REQUIRED=YES. Normally restart the unit.
Fresh wired session: check center-screen CarPlay, cockpit maps, menu, wheel zoom.
First confirm existing 70% behaviour; then select one other value, wait for the
save to finish, restart normally, reconnect and compare in the same app/layout.

Read-only negotiated-property diagnostic:

```sh
grep -F 'SEAT_ZOOM_FACTOR' /tmp/altscreen111.log
```

This reports the advertised numeric value, not phone/cockpit visible acceptance.

## Recovery

Keep this complete package and the verified originals under
altscreen-u2/backup/menu-zoomfactor-v1. Disconnect phone, leave menu, run:

```sh
/bin/ksh /fs/sda0/MU1409-menu-zoomfactor-v0.1/install.sh --restore-check
```

Only after PASS, run the same command with --restore, then normally restart.
Restore removes only the added zoom-factor key from the current and last-good
profiles, preserving other preferences, before restoring the original binaries.
Do not use an older receiver-only updater to undo this multi-component change.

## Qualification

QNX ARM receiver/service/tools compiled. Java class format 46 compiled; host menu
test passed. Canonical bounds/default and 45-to-46-row profile migration/edit
tests passed. Read-only downgrade conversion preserved all old profile bytes.
The update installer, J9 runtime probe, persistence after reboot and visible
effect still require actual target testing. No vehicle was accessed by builder.
