# SEAT / CUPRA MU1409 Apple CarPlay and wireless adapters

> **HIGHLY EXPERIMENTAL — INSTALL AND USE AT YOUR OWN RISK.**
> Provided AS IS, without warranty. The maintainers, authors and contributors accept no liability to the extent permitted by applicable law. A failed modification can disable infotainment or cockpit functions, damage an adapter, lose pairing/settings or require specialist recovery. No compatibility or successful recovery is guaranteed. Read [DISCLAIMER.md](DISCLAIMER.md). Test only while parked, with stable power and verified backups.

Unofficial project for the SEAT/Cupra **MHI2_ER_SEG11_P4708 / P4708_1, MU1409** port and separately matched wireless adapters. This is not an Apple, SEAT, CUPRA, Volkswagen, Harman or adapter-vendor-supported product. A similar model name does not establish compatibility.

## New here? Follow this order

1. [Choose your package and read the compatibility limits](docs/START_HERE.md).
2. [Download ZIPs and verify their checksums](downloads/README.md). **GitHub Code → Download ZIP is source, not an SD installer.**
3. For the car: [beginner installation, prerequisites and recovery](docs/NEWBIE_INSTALL.md).
4. For a wireless adapter: [model/firmware selector and flashing instructions](adapters/README.md). First get cockpit maps working over a direct USB cable.
5. For developers: [source map, dependencies and packaging](docs/DEVELOPMENT_AND_PACKAGING.md).

## Included features

| Feature | Where to read |
|---|---|
| SEAT port: wired cockpit maps, guarded MOST ownership, original H.264 forwarding, firewall and automatic startup | [Full-stack installation](docs/CONSOLIDATED_INSTALL.md), [source](src/native) |
| English native car HOME menu, settings persistence, dropdowns and red scroll indicator | [Menu source](src/menu), [known limitations](docs/STATUS.md) |
| Right steering-wheel roller zoom, measured for this target | [Wheel zoom](docs/SEAT_CUPRA_MU1409_WHEEL_ZOOM.md) |
| **Cockpit zoom-factor menu: 70%–150%**, plus Default/omit; restart required | [Cockpit zoom factor](docs/ZOOM_FACTOR_MENU.md) |
| **MHI2 centre-screen zoom**, separate optional 70% metadata candidate | [Centre-screen zoom](docs/MAIN_DISPLAY_ZOOM.md) |
| Three cockpit views and Wide SafeArea adjustment to **628×220 at 191,56** | [SafeAreas](docs/SAFEAREAS.md) |
| **VC Audio/Media song title, artist and album**, clearing on disconnect | [Media in the cockpit](docs/MEDIA_IN_VC.md), [source](src/media-info) |
| Bounded video queue recovery without repeatedly handing the display back to stock | [Scaling and recovery](docs/SEAT_CUPRA_MU1409_SCALING_AND_RECOVERY.md) |
| Four separate wireless-adapter packages, source and stock fallback | [Adapter selector](adapters/README.md) |

The owner reports all four adapter configurations working as of **30 October 2026**. This is an operator report, not independent acceptance of every iOS/app/hardware combination. Original package validation notes retain their build-time status. Centre-screen icon-row count, every setting, touch alignment, reduced-view placement and long-term reliability are not universally qualified. See [release notes](docs/RELEASE_2026-10-30.md).

## Source and firmware boundaries

The repository includes the SEAT-specific C/Java/shell port, latest cockpit menu zoom/settings changes, media bridge source, installer/build tools, tests, source archives and documentation. [The release](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/tag/experimental-2026-10-30) provides complete versioned runtime ZIPs with their own guarded installers/uploaders and rollback inputs. Source and runtime downloads serve different purposes.

No QNX SDK/sysroot, full car/cockpit firmware extraction, MFi certificates/private keys, live credentials, personal captures or tester backups are published. Target-bound runtime bundles include compiled hooks derived from the supplied target inputs and vendor adapter binaries; their original rights apply. The project license does not relicense third-party binaries. See [provenance](THIRD_PARTY_NOTICES.md).

Upstream foundations: [harman-f/mhi2_altscreen_carplay](https://github.com/harman-f/mhi2_altscreen_carplay), [OMKE wireless adapter work](https://github.com/OMKE/wireless-carplay-virtual-cockpit), [kamgurgul HW301 work](https://github.com/kamgurgul/mib2q-carplay), and the [MST2 media reference](https://github.com/xPaiiN/mst2-carplay-vc). The SEAT media implementation uses target-specific MHI2 classes; do not install an MST2 package on MHI2.
