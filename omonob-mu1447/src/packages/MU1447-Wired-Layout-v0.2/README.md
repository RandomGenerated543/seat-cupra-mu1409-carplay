# Wired MU1447 corrected menu layouts — experimental v0.2

Correction for the working MU1447 wired display add-on. **70% zoom is retained.**
This update understands omonob's actual Navigation Card menu mapping:

| Menu selection | Native view | This update |
|---|---|---|
| Off | 0 idle, 4 navigating | Restore original 606×329 @202,1; request ETA=yes, maneuverLayout=no |
| Center | 3 with or without a route | New 628×185 @191,56 safe area, ETA=yes, topAligned |
| Left | 0 idle, 1 navigating | Keep X=202,Y=45,width=606; height 272→252, raising the lower edge 20 pixels; ETA=yes,leftAligned |
| Right | 0 idle, 2 navigating | Original rectangles; ETA=yes,rightAligned |

The earlier patches incorrectly treated views 0/4 as “Wide” instead of tracing
Navigation Card selection. Those view rectangles are restored here. View 3 is
the actual Center selection; this is confirmed by both the rc.7 Java menu constants
and execution of the original native `cpmap_card_view_for` ARM instructions.

Off requests a map without the maneuver card but with ETA. Actual phone/app layout
still needs an in-car check. The geometry is an iOS layout hint, not a guaranteed
pixel translation of every element. Center uses the shortened 185-high rectangle
from the requested 35-pixel ETA lift. Left's top stays in place; only its lower
boundary is raised 20 pixels, so its top card does not move unnecessarily.

Highly experimental; use at your own risk, no warranty. These corrected placements
are locally verified but not yet accepted in a physical MU1447 vehicle.

## Compatibility

For the existing **working MU1447-Wired-Display-v0.1.1** installation, with or
without **MU1447-Wired-ETA-v0.1** applied. Install directly over either exact state;
you do not need to uninstall/restore them first. Unknown files are refused.

This update replaces **only `/mnt/app/carplaymaps/core.so`**. It checks but does not
change the working 70% zoom library or either launcher. No wireless components,
firmware, JAR/menu changes, networking changes or MU1409 components are included.

## Install

Extract the complete `MU1447-Wired-Layout-v0.2` folder onto the SD root.
Disconnect USB CarPlay, connect through SSH, then run:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Layout-v0.2/install.sh --check
```

If it reports `WIRED_LAYOUT_CHECK=PASS state=BEFORE`, run:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Layout-v0.2/install.sh --apply
```

Wait for `WIRED_LAYOUT=INSTALLED`, then manually restart the infotainment.
Reconnect by USB and use the existing **Navigation Card → Off / Center / Left**
settings. Start an actual route to check the navigating layout and ETA placement.
Keep power stable while writing. On FAIL save the output and stop.

## Undo

Disconnect USB CarPlay and run:

```sh
/bin/ksh /fs/sda0/MU1447-Wired-Layout-v0.2/install.sh --restore
```

Restart manually. This returns exactly to whichever supported core was present
before this update (v0.1.1 or the earlier ETA-lift variant). It keeps a backup at
`/mnt/app/.mu1447-wired-layout-v02/core-before.so`.
Restore this v0.2 update **before** restoring either older display/ETA add-on,
since those installers validate exact core bytes. Do not delete their backups.

## ETA URLs and scope

All four scene URLs now request `showETA=yes`. Original maneuver choices are
restored: Center=topAligned, Left=leftAligned, Off=no, Right=rightAligned.
The dedicated `/map` path is retained for Off. To fit the longer `yes` value into
the fixed Left string slot without moving code or pointers, that URL omits the
optional `showSpeedLimit=no` directive; Left therefore uses the app's default
speed-limit preference. Other scenes retain their explicit speed-limit directive.

Executable code, ELF layout, URL pointer offsets and all non-layout behavior are
unchanged. Sources and binary patch assertions are included in `source/patch.py`.
The original core is included as a build reference only, not an accepted input state.
The byte comparator is from the previous display add-on; its C source is included.

Local verification:
- Executed the actual ARM card-view selector at two load addresses, all four menu
  choices, both idle/navigating states. Center→3, Left active→1, Off→0/4 confirmed.
- Exact rectangle and URL/patch-boundary assertions; headers and code unchanged.
- Host installer fixtures for both accepted prior cores: check without persistent
  writes, repeated apply, byte-exact undo, other files unchanged, unknown core refused.

ARM mapping test requires Python `unicorn`. Installation requires only the existing
QNX shell/SSH and SD. No build tools or Python are needed on the car.

Base core: `918f81fb43f49dacfb5e52c304e24ee3f9d00a0b6d6f66f85d6d3d87de8feaed`
Candidate: `af791f8b63712a2986735d23d36b52a46b448789b3aa16717dcc450e469042b0`

Original core and menu semantics come from the supplied public omonob rc.7 package:
https://github.com/omonob/VW-MHI2-Wireless-Carplay-Maps . This add-on is separate and
experimental; it does not claim upstream endorsement. Preserve upstream licensing
and notices when redistributing.
