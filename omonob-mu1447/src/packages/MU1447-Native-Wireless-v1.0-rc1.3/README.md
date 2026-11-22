# SEAT / Cupra MU1447 integrated native wireless CarPlay

**Version: v1.0-rc1.3 — highly experimental, car validation pending.**

This is one persistent SD/SSH installer for **MHI2_ER_SEG11_P4709 / MU1447, 790-family cockpit**, on top of the exact currently working wired public rc.7 installation and our display adjustments. It includes normal startup, centre-screen touch integration and a cockpit map path. It does not require a separate pilot installation.

Use entirely at your own risk. There is no warranty or promise of uninterrupted operation. The author accepts no liability to the extent permitted by law. Local tests passed; this exact combined build has **not been tested on a vehicle**. “Installed” verifies files, not functionality or an absence of bugs.

## Installer corrections in rc1.2

rc1.2 also compares free-space numbers with decimal-aware `awk`, avoiding signed 32-bit shell overflow on volumes with more than 2 GiB free. The reported 3,123,281,920 bytes on `/mnt/ota` is sufficient.

The original installer required 30 MB free on a RAM disk whose total capacity is 20 MB. This revision calculates actual staging bytes (including JAR duplicates and configuration growth) and adds an 8 MiB reserve. It prints required and available bytes. Runtime payload binaries are unchanged. No cleanup or restart is needed for a failed rc1 space check.

## Recover the failed rc1.2 backup seal before retrying

If rc1.2 reported `FAIL reason=baseline_seal`, runtime replacement had not started. Its unfinished backup must be verified and preserved before retrying:

```sh
cd /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3
/bin/ksh ./install.sh --recover-backup
```

Require `MU1447_BACKUP_RECOVERY=PASS live_baseline_verified=1 old_backup_preserved=1`. This normalizes only the legacy single-space checksum separator in a RAM verification copy, invokes the native verifier, confirms all41 saved baseline rows match the current live files, and renames the unfinished backup to `/mnt/app/.mu1447-native-wireless-v1-backup.preseal-rc12`. It does not delete or reseal the original saved data, enable wireless or touch runtime files. It refuses if a completion marker exists, a live tracked file differs, a saved hash fails or that preserved-backup name already exists.

After recovery, run `--check` and then `--apply` as below. No restart is needed between the failed seal, recovery and retry. rc1.3 writes the required standard two-space checksum separator. All wireless runtime payloads remain identical to rc1.

## What it carries forward

- Your wired core, wired launcher, 70% cockpit zoom library and media/artwork startup remain unchanged.
- Wireless cockpit zoom is fixed at **70%**; there is no extra zoom menu.
- Wireless safe areas match the latest requested layout, including Center moved down 20 pixels.
- ETA is requested with `showETA=yes`. Native navigation-card choices select Center, Left, Right or Off. Off requests ETA without a maneuver card. Actual Waze placement and content remain app-controlled.
- Both wireless displays request **30 fps**. This is a requested ceiling, not guaranteed measured frame rate. No 60 fps mode is included.
- Parking and other OEM screens keep their screen-ownership handoff separate from an underlying visible CarPlay canvas. This correction passed local Java tests; camera behavior still needs vehicle acceptance.
- Bluetooth starts the receiver automatically after a normal unit restart. The channel watcher continues after the first four minutes and permits one watcher instance.
- Runtime firewall rules permit the required CarPlay ports on the car hotspot. The existing OEM NAT/uplink choice is detected rather than forcing the house-Wi-Fi firewall file. A watcher reapplies those rules after OEM reloads. Persistent `pf.conf` files are not edited.

## Exact prerequisites

1. P4709 / MU1447 firmware and a 790-family cockpit; do not use on MU1409, MU1367, MHI2.5 or a 791 cockpit.
2. The public wired rc.7 installation already working, with our `MU1447-Wired-Display-v0.1.1` and corrected navigation-card layout. The checker accepts the known v0.2 layout or subsequent Center-down core. Wireless uses the latest Center-down geometry. It does not silently update a different wired layout.
3. Working root SSH access and the car's own WLAN hotspot. The installer preserves SSH credentials and does not create SSH access.
4. An SD card readable by the unit, the extracted package folder, and about 10 MB available on `/ramdisk` (calculated from actual staged files plus an 8 MiB reserve), and at least 30 MB on each checked application volume.
5. No other active wireless modification. Restore an earlier wireless installation first, restart normally, and confirm wired CarPlay still works.

The installer identifies the exact stock JXE, Bluetooth executable, connection manager and AirPlay library by SHA-256. These native inputs are **not replaced**. If any check fails, save the output and stop; do not bypass it or substitute another firmware's binaries.

## Install from SD

1. Extract the ZIP on your computer. Copy the **whole `MU1447-Native-Wireless-v1.0-rc1.3` folder** to the SD root. Avoid nesting that folder inside another copy.
2. Park the car and keep power stable. Unplug the iPhone's USB cable and disconnect any wireless CarPlay session. Turn the phone's Bluetooth off during installation if it keeps reconnecting.
3. Connect the computer to the same network as the car. Example for the existing SSH key on this Mac:

```sh
ssh -i ~/.ssh/mqb_car -o IdentitiesOnly=yes \
  -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa \
  root@192.168.50.242
```

Use the car's current IP if different. When connected directly to its hotspot, the established address is `10.173.189.1`. Other computers must use their own working key or normal password login; the package includes no credentials.

4. In the car's SSH terminal:

```sh
cd /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3
/bin/ksh ./install.sh --check
```

Proceed only when the output ends with `MU1447_WIRELESS_CHECK=PASS`. This check stages files in RAM and links Java classes without invoking the activators. It does not change persistent files or enable wireless.

5. Install:

```sh
/bin/ksh ./install.sh --apply
```

Wait for `MU1447_WIRELESS=INSTALLED persistent=1 manual_restart_required=1`. No automatic reboot is performed. If installation reports failure, retain the SD card and the complete output. A failure during copying triggers an attempted automatic rollback, whose result is printed separately.

6. Perform a normal infotainment restart. Enable the car's WLAN hotspot in its normal menu. Turn phone Bluetooth/Wi-Fi back on. Pair with the car and accept the iPhone's CarPlay permission. Keep USB disconnected to confirm this is wireless.

If an old wireless pairing remains stuck, forget the old car entry in iPhone **Settings → General → CarPlay** and the corresponding Bluetooth pairing, then pair again. Do not delete the unit's pairing-store files. The installer does not factory-reset either device.

The SD card is no longer needed for autostart after installation. Keep it and the backup available for rollback.

## Navigation cards and safe areas

Use the existing native CarPlay/navigation-card settings; no extra custom menu is installed. Coordinates below are **x, y, width, height** in the 1010 × 376 cockpit surface.

| Card choice | Native view | Safe area | Maneuver card |
|---|---:|---|---|
| Off / non-navigation | 0 or 4 | 202, 1, 606, 329 | Off; ETA requested |
| Left, active navigation | 1 | 202, 45, 606, 252 | Left aligned |
| Right, active navigation | 2 | 202, 45, 606, 272 | Right aligned |
| Center | 3 | 191, 76, 628, 185 | Top aligned |

These are wireless settings. The two supported wired core variants are left byte-for-byte unchanged, so a previously installed wired Center-down update remains in place.

## Verify and restore

File installation status:

```sh
/bin/ksh /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3/install.sh --status
```

Optional read-only runtime snapshot:

```sh
/bin/ksh /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3/status.sh
```

A valid file receipt alone is not an operational pass. Before relying on the build, check centre-screen video/touch/audio, cockpit map and ETA, map-app switching, a phone call, parking-screen touch and return, and reconnect after a full vehicle sleep. Remain parked for interaction tests.

To return to the wired setup saved at this installation:

```sh
# First disconnect CarPlay and unplug USB.
cd /fs/sda0/MU1447-Native-Wireless-v1.0-rc1.3
/bin/ksh ./install.sh --restore
```

Wait for `MU1447_WIRELESS=RESTORED wired_baseline_verified=1`, then restart normally. The backup is `/mnt/app/.mu1447-native-wireless-v1-backup`. Keep it. The restore checks file identities and refuses to overwrite unexpected later edits. The receiver's pairing store is retained. A backup/restore cannot guarantee recovery from loss of SSH access or a separate hardware/firmware failure.

After a successful restore, reapplying this same transaction is deliberately refused while its saved backup exists. Do not delete the backup just to bypass that refusal; review the saved state first.

## Known limitations

- No on-car acceptance yet for this combined build. Disconnects, lag, camera touch, calls, overnight reconnect, app-switch recovery and cockpit resets are not certified fixed.
- The fifteen native Bluetooth entry-point fingerprints match MU1447. That is a static compatibility result, not proof of every internal object layout or RF/session behavior.
- Wired media/artwork startup and original public menu classes are preserved. Wireless media metadata/artwork is not independently validated.
- ETA/card appearance depends on the navigation app. The request and geometry are verified locally, not the resulting on-car rendering.
- Car Wi-Fi uplink and hotspot share a radio. Continued channel monitoring and preservation of OEM NAT address identified failure paths; they do not establish performance under every Wi-Fi condition.
- No native firmware upgrade, Bluetooth binary replacement, WLAN mode/driver patch, security-key modification or SSH reconfiguration is included.

See `VALIDATION.md`, `BUILD.json`, `source/` and `NOTICE.md` for scope and provenance. All package files are covered by `SHA256SUMS.txt`; it detects changes but is not a publisher signature.
