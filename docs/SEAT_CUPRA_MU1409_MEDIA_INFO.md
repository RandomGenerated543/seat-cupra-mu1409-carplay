# SEAT/CUPRA MU1409 CarPlay song information — v0.1 candidate

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY. Compiled and host tested; not yet tested in a car.**

Adds CarPlay **song title, artist and album to the cockpit Audio/Media page**, replacing the generic Apple CarPlay label when valid metadata is available. It does not overlay song text on the cockpit map. Select the cockpit's normal Audio page while music plays through CarPlay.

This is an additive port for the existing project SEAT MHI2_ER_SEG11_P4708_1 / MU1409 EU stack. It is not the MST2 package and is not qualified for P4709/MU1447, another brand, or another Java firmware. Do not install xPaiiN's MST2 installer on MHI2.

Reference: https://github.com/xPaiiN/mst2-carplay-vc at `f1ac169d1ce40b291d9a2ab6a0d97fe53474754f`. The shared idea is CarPlay metadata -> OEM AudioSD fields. This candidate uses the exact MU1409 classes and its DSI callbacks. It does not use MST2 PPS polling or its native artwork tap.

## Included and excluded

- Included: title/artist/album updates, clearing on disconnect, invalid-data fallback, guarded source selection, task-thread refresh, status counters, reversible boot integration.
- Existing menu, receiver, SafeAreas, zoom factor, wheel zoom, firewall and MOST writer binaries are not replaced.
- Cover art, progress timer, shuffle, telephony and navigation import are **not implemented by this candidate**. Cover art requires a separately qualified MHI2 artwork bridge.
- A wireless adapter must forward the underlying now-playing metadata. Wireless support is not established merely by a successful wired test.

## Install

Keep the car parked and powered. Disconnect the phone. Extract the complete `MU1409-media-info-v0.1` folder onto the SD card. Keep the SD package available for recovery.

Connect from the Mac:

```sh
ssh -o ConnectTimeout=10 -o ControlPath=none -o HostKeyAlgorithms=+ssh-rsa root@192.168.50.242
```

Run on the unit:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --check
```

It hashes the exact OEM Java image and checks the existing startup script, payload integrity and target J9 loader. It does not attach to a running CarPlay session or change persistent files. Allow around one minute on the unit; timing is unmeasured. Stop on any failure and save the output.

After `MEDIA_J9_PROBE=PASS` and `MEDIA_PREFLIGHT=PASS`:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --apply
```

Expected: `MEDIA_INSTALL=PASS RESTART_REQUIRED=YES`. Normally restart the infotainment unit, then make a fresh wired CarPlay connection. Installation does not restart it automatically. No VC firmware is changed.

## Acceptance test

1. Confirm normal centre-screen CarPlay, audio and cockpit maps.
2. Play a known song in Apple Music or Spotify. Select the cockpit Audio page. Check title, artist and album against the phone.
3. Skip twice, pause/resume, and confirm the text follows the actual track. A progress timer is not included.
4. Switch to radio or another OEM media source. Confirm its normal information and controls.
5. Disconnect the phone. Confirm old song data disappears. Reconnect and play a different track.
6. Return to the map and check wheel zoom and the existing menu.

Diagnostic commands:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/control.sh --status
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/control.sh --log
```

`attached=1` means the listener was registered; `updates` counts metadata callbacks. `rendered` counts application to AudioSD data, **not independently confirmed visible output**. If `updates=0`, retain logs; do not infer that metadata transport works. Logs do not record song titles or phone identifiers.

## Restore

Disconnect the phone. Run:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --restore-check
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --restore
```

Normally restart the unit. The original startup script is restored byte for byte. The extra JAR remains on disk but is no longer loaded. Existing menu/video files and stored settings remain unchanged. Unknown startup changes are refused rather than overwritten. Backups are retained in `/mnt/app/root/altscreen-u2/backup/seat-media-v01`.

The package contains target-derived OEM class bytes and startup scripts for the owner's local test. The shareable source ZIP omits those inputs. Do not mistake this local candidate for an accepted public release.
