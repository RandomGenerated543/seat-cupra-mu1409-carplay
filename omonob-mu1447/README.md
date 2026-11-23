# SEAT / CUPRA MU1447 — omonob adaptation

**HIGHLY EXPERIMENTAL. INSTALL AND USE AT YOUR OWN RISK.** Supplied AS IS, without warranty. Authors and contributors accept no liability to the extent permitted by law. Interruptions or failed changes can disable infotainment/cockpit functions and require specialist recovery. There is no promise of bug-free operation or successful recovery. Use stable power, retain backups and perform interaction tests while parked.

For **MHI2_ER_SEG11_P4709 / MU1447 with a 790-family cockpit**, on top of the exact supported omonob wired installation. This is the separate **`omonob-mu1447` branch**. The older Harman-based MU1409 implementation remains on [`main`](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/tree/main). Only this folder belongs to this adaptation; inherited files elsewhere in this branch describe the earlier stack.

This is an unofficial port/patch collection, not an upstream-endorsed release or a complete firmware source release. MU1409, MU1367, MU1440, MHI2.5 and 791 clusters are not interchangeable targets.

## Start here

1. Read [installation and prerequisites](docs/INSTALL.md).
2. Select and download the [versioned SD ZIPs](downloads/README.md). GitHub **Code → Download ZIP** is a source checkout, not a ready SD installer.
3. Follow the documented order, one package at a time. Keep every package and its original backup.
4. Read [restore order](docs/RECOVERY.md) before installation.
5. Read [tested configuration and open issues](docs/STATUS.md), especially the **hotspot-on / internet-client-off workaround**.

For the full technical account, read the [implementation review](docs/IMPLEMENTATION-REVIEW.md): MU1447 compatibility, Bluetooth bootstrap, networking, camera/touch ownership, startup, session tracking, cockpit layout, installer corrections and validation, with links to the published source.

## What is included

- The MU1447 wired display add-on: fixed **70% cockpit zoom**, `showETA=yes`, and navigation-card safe areas. No extra zoom menu is added.
- The corrected native **Off / Left / Right / Center** mapping and final Center-down adjustment.
- The native wireless rc1.3 installer, MU1447 native-input checks, Bluetooth compatibility shim, 30 fps requests, cockpit integration and automatic startup.
- The separate runtime firewall/QoS add-on and wireless layout add-on.
- Runtime v0.1: camera ownership and touch handoff corrections, asynchronous bounded touch sender, startup retries, session-health observation and serialized startup.
- Startup v0.1: event-driven touch-readiness wake-up with the original idle wait retained.
- Patch/build sources, tests, checksums, original package instructions, provenance and restore commands.

The existing omonob media/artwork launcher path is preserved. **Wireless media/artwork was not independently qualified.** The earlier MU1409 media bridge and MHI2 main-screen zoom candidate are separate implementations and are not transplanted into this branch. Cockpit display scaling is also separate from steering-wheel map zoom buttons.

## Current vehicle report

**23 November 2026:** the owner reports that the car is working perfectly, with no bugs currently observed. This is the latest vehicle report; see the [implementation review](docs/IMPLEMENTATION-REVIEW.md) and [dated report](validation/OPERATOR-REPORT-2026-11-23.json). The successful configuration previously reported keeps the hotspot enabled and the internet client/search disabled. The latest report does not establish every other vehicle, phone or simultaneous-uplink configuration.

On 21 November 2026 the operator reported installing the current corrections. Two whole-session drops occurred during startup while the hotspot channel moved and the car joined its Wi-Fi internet uplink. The receiver remained alive. After disabling the car's internet-client connection, **while leaving its hotspot enabled**, the operator reported no further disconnect and smoother interaction in that test. Duration was not recorded precisely. This is a useful workaround report, not a long-term stability certificate or proof that the channel change alone caused the problem.

Original SD ZIPs retain their original build-time “untested” notes. The later operator report is recorded separately in [status](docs/STATUS.md) and [validation](validation/OPERATOR-REPORT-2026-11-21.json); package hashes have not been changed to rewrite history.

## Source, dependencies and rights

- [Source map and rebuild limitations](docs/BUILD.md)
- [Source tree](src)
- [Package identity manifest](downloads/PACKAGES.json)
- [Provenance](SOURCE_PROVENANCE.json), [notices](NOTICE.md), [upstream credits](CREDITS.upstream.md), [upstream GPL text](LICENSE.upstream)

Upstream foundations: [omonob wired CarPlay Maps](https://github.com/omonob/VW-MHI2-Carplay-Maps), [omonob native wireless CarPlay Maps](https://github.com/omonob/VW-MHI2-Wireless-Carplay-Maps). Third-party rights remain with their owners. New patch code does not relicense OEM, Apple, QNX or opaque receiver dependencies. Full firmware images, SDKs, private authentication material, SSH keys, phone pairing stores and raw personal diagnostic logs are excluded.
