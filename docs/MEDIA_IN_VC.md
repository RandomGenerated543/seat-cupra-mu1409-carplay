# CarPlay songs in the Virtual Cockpit

**HIGHLY EXPERIMENTAL. Use at your own risk. No warranty.** The package is SEAT MHI2 MU1409-specific, not the MST2 installer.

MU1409-media-info-v0.1 forwards **title, artist and album** to the cockpit's normal **Audio/Media page**. It clears stale values on disconnect and preserves OEM source selection. It does not put song text over the map. Artwork, a progress timer, shuffle, telephone translation and navigation import are not included.

Download the complete runtime ZIP from ../downloads/README.md. It adds a separate target-bound Java hook; it does not replace the existing menu, receiver, wheel, MOST owner or SafeAreas. A wireless adapter must also forward now-playing metadata. Test wired first so adapter behaviour is not confused with the unit bridge.

Unplug the phone, park/power the car, extract the full folder to SD root and run on the unit:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --check
```

Only after MEDIA_J9_PROBE=PASS and MEDIA_PREFLIGHT=PASS:

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/install.sh --apply
```

Expect MEDIA_INSTALL=PASS RESTART_REQUIRED=YES. Restart normally and reconnect wired CarPlay. Play a known song, select cockpit Audio/Media, verify the three fields, skip twice, switch to radio, disconnect and reconnect with a different song. Then verify maps and wheel controls. A successful listener attachment or rendered counter does not independently prove the screen's visible text.

```sh
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/control.sh --status
/bin/ksh /fs/sda0/MU1409-media-info-v0.1/control.sh --log
```

Restore with the same install.sh --restore-check then --restore after PASS; restart. The original startup is restored byte-for-byte. Backups are under `/mnt/app/root/altscreen-u2/backup/seat-media-v01`. Unknown intervening startup changes are refused.

[Project source](../src/media-info) includes the state model, target bridge, original-bytecode hook transformer, build/package scripts and tests. Building requires the exact local target API/original class inputs and ECJ/JDK; the runtime ZIP is already compiled. The reference is xPaiiN/mst2-carplay-vc, but these are independently adapted MHI2 classes, not MST2 polling or artwork code.
