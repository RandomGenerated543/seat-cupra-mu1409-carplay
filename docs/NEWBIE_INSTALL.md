# Beginner car installation and optional features

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY. Read ../DISCLAIMER.md.**

## What you need

- Exact compatible SEAT/Cupra MHI2 P4708/P4708_1 MU1409 and the qualified 790-family cockpit. The firmware's actual file hashes must pass; the name alone is insufficient.
- Working original centre-screen wired CarPlay, navigation/infotainment and existing authorized SSH access. This repository does not unlock a unit, activate CarPlay/SWaP or install M.I.B. for you.
- The matching M.I.B. NavActiveIgnore prerequisite retained from the known baseline; exact files/startup are checked.
- A computer with an SSH client. macOS Terminal and Windows PowerShell OpenSSH work. Python 3 is needed for host collectors/build tools, not for the compiled car installers.
- An SD card the unit can read, a way to copy/extract files onto it, stable vehicle power, off-unit backups and an independently accessible recovery route. Use a freshly charged/powered parked vehicle; do not install during driving.
- Remove any previous omonob/other cockpit-map mod using **its own matching uninstaller**. Restart and verify stock CarPlay/navigation before proceeding. No such uninstaller is bundled.

## Download and unpack

Use the versioned runtime ZIPs from ../downloads/README.md. Extract whole named folders to the SD root. Do not flatten payloads into the root, rename files inside a kit or combine different installers' payloads. Keep each KIT.sha256, TARGETS/IMMUTABLES where supplied, payload and installer together. Keep a copy of the exact ZIP used and its backups.

Baseline A and B contain different known original firewall files. They are not choices of display style. Both have strict checks. Use the package whose exact originals match; do not edit hashes to bypass a failure. If neither passes, obtain a read-only inventory with scripts/collect_install_baseline.py and stop for review. Rejected prerequisites are not fixed by trying every package with --apply.

## Connect to the car

Join the network on which your unit's SSH service is reachable. Substitute the real unit address; 192.168.50.242 is the retained example, not a guaranteed address. Paste this into **Mac Terminal or Windows PowerShell**:

```sh
ssh -o ConnectTimeout=10 -o ConnectionAttempts=1 -o ControlPath=none -o HostKeyAlgorithms=+ssh-rsa root@192.168.50.242
```

Enter the unit's own password when prompted. Password typing is normally invisible. Do not publish it. A `root@mmx:...>` prompt means you are now on the unit. `Host is down` means resolve connectivity/power/address first; an installer will not fix SSH connectivity.

## Fresh installation only

Disconnect the phone, leave the custom menu and insert the SD. The example below is baseline A; replace only the folder name with baseline B if that is your verified match:

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-v0.2.1-baseline-A/install.sh --check
```

Continue only after `FULL_PREFLIGHT=PASS`. If the SD is read-only and the installer needs its backup directory, remount the **SD only** and repeat the check:

```sh
mount -uw /net/mmx/fs/sda0
```

Do not substitute /mnt/app or /mnt/system into that command. The installer manages its target mounts. If your SD is mounted elsewhere, use its actual path consistently.

```sh
/bin/ksh /fs/sda0/SEAT-MU1409-final-stack-v0.2.1-baseline-A/install.sh --apply
```

Expect `FULL_INSTALL=FINAL_STACK_FILES_VERIFIED RESTART_REQUIRED=YES`. Save the full output. Normally restart the infotainment unit using its normal controls; the installer does not reboot it. Reconnect SSH with the same command, then make a **fresh wired** CarPlay connection. Copy `original-backup/` off the SD and retain it.

Verify centre-screen CarPlay/audio, cockpit maps, automatic startup after another restart, car HOME → CarPlay settings, OEM Back/navigation and stock return on phone disconnect. The v0.2.1 installer includes the wp2 storage-anchor directory correction; do not run an old manual startup fix as an additional service.

```sh
/bin/ksh /mnt/app/root/altscreen-u2/harman-r13/control.sh --status
/bin/ksh /mnt/app/root/altscreen-u2/scripts/direct_ts_auto_status.sh
```

`harman-r13` is an existing internal runtime path retained for compatibility, not the name of a tester-specific adapter package. Logs/acknowledgements are not proof of visible output.

## Existing-stack feature updates

Install and verify one layer at a time. Every --check must pass before --apply. The recommended order for a fresh stack is:

1. **Cockpit zoom menu**: MU1409-menu-zoomfactor-v0.1. Select 70–150% or omit from the car HOME menu. Restart + fresh CarPlay session after changing this value. See ZOOM_FACTOR_MENU.md.
2. **Optional MHI2 centre-screen zoom**: MU1409-main-display-zoom-v0.1, installed after the cockpit menu update. This is a separate fixed 70% metadata candidate, not a centre-screen percentage selector. Check icon rows and touch alignment. See MAIN_DISPLAY_ZOOM.md.
3. **VC song metadata**: MU1409-media-info-v0.1. Title/artist/album appear on the cockpit Audio/Media page. See MEDIA_IN_VC.md.
4. **Optional smaller Wide SafeArea**: MU1409-wide-safearea-v0.1. See SAFEAREAS.md.

For each named folder the car command pattern is:

```sh
/bin/ksh /fs/sda0/FOLDER/install.sh --check
/bin/ksh /fs/sda0/FOLDER/install.sh --apply
```

Replace FOLDER with one exact name above; do not paste FOLDER literally. Normally restart whenever the kit reports RESTART_REQUIRED=YES. Existing centre-screen zoom changes receiver hashes: a later older zoom/menu installer can deliberately refuse that baseline. Do not bypass this or downgrade one library alone.

## Undo and recovery

Disconnect the phone. Use **the same kit that installed the layer** and read its recovery instructions. Typical feature recovery is:

```sh
/bin/ksh /fs/sda0/FOLDER/install.sh --restore-check
/bin/ksh /fs/sda0/FOLDER/install.sh --restore
```

Restore overlapping layers in reverse order, verifying each preflight; follow any kit-specific differences. Full-stack restore is documented in CONSOLIDATED_INSTALL.md and retained internally at `/mnt/app/root/seat-full-install-v02-backup/kit/install.sh`. Restore only when its backups and current-state checks pass. Keep the original kit; a newer kit is not a substitute for its recovery manifests. A factory reset is not a substitute for restoring patched files. If SSH or backups are unavailable, use your independent recovery route rather than blind writes.
