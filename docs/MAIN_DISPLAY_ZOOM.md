# MHI2 centre-screen zoom factor

**Highly experimental, use at your own risk; no warranty.** This is separate from cockpit zoom and does not change cockpit firmware.

Download MU1409-main-display-zoom-v0.1 from ../downloads/README.md. Its original validation establishes compiled builds and host tests, not a guaranteed three-row icon layout. The main display receives numeric lowercase zoomFactor=70 while keeping its 800×480 canvas, physical/input metadata and touch coordinates. The phone may choose a different layout or ignore it. No software transcoding is used.

There is no centre-screen percentage menu in this v0.1 package. The cockpit menu offers 70–150% independently. This package recognizes the fixed-cockpit receiver and cockpit-menu receiver baselines; it selects the matching source-derived build. Unknown/mixed hashes are refused.

Extract the named folder to SD root. Disconnect the phone, leave the settings menu, then on the car:

```sh
/bin/ksh /fs/sda0/MU1409-main-display-zoom-v0.1/install.sh --check
/bin/ksh /fs/sda0/MU1409-main-display-zoom-v0.1/install.sh --apply
```

Only apply after the check passes. Normally restart and reconnect wired CarPlay. Photograph the icon rows and test touches at all corners, keyboard, Back, maps, cockpit output and wheel controls.

```sh
grep -F 'MAIN_ZOOM' /tmp/altscreen111.log
```

The log proves outgoing metadata, not phone acceptance. For restoration use the same install.sh with --restore-check, then --restore after PASS, then restart. Both receiver originals are backed up at `/mnt/app/root/altscreen-u2/backup/main-display-zoom-v01`. Do not use a generic receiver-only updater to undo a multi-layer configuration.

The release includes complete fixed/menu source variants, target ABI comparison, host tests and source/BUILD.md. The source index is ../src/main-display-zoom/README.md. No separate wireless CarPlay receiver or native MHI2 wireless activation is included.
