# Open issues and limits — 30 October 2026

**Experimental project, no warranty.** An installer PASS, phone acknowledgement or build marker does not establish visible output. The owner reports four adapter configurations working; this page records remaining limits rather than promising universal support.

| Issue | What is established | What remains / workaround |
|---|---|---|
| Waze wheel zoom | The target right-wheel roller bridge produced visible zoom in Apple Maps and Google Maps. | Waze did not visibly respond in prior tests. Use an app supporting the command; this is not claimed fixed. |
| Full/Center guidance and ETA | View switching now works and the three geometries are advertised. Waze information returns in Wide. | Reduced layouts can hide or overlap ETA/directions behind OEM gauges. SafeArea is a request to the app, not black padding or forced placement. Prefer Wide when information is missing. |
| Centre-screen zoom | A separate fixed 70% metadata candidate is compiled for two known receiver baselines. | Three icon rows, app/iOS response and touch alignment are not universally qualified. It is not a centre-screen percentage selector. Test all corners and restore if incorrect. |
| Cockpit zoom percentages | The menu stores 70–150% or omit; the receiver freezes the negotiated value for its process. | A unit restart and fresh CarPlay session are required. Percentage labels are numeric metadata, not a calibrated promise of equal physical size on every app. |
| VC media information | Project bridge supports title, artist, album and clearing on disconnect on the normal Audio/Media page. | Artwork, playback timer, shuffle, telephony and navigation import are not implemented. Wireless metadata depends on the adapter. Verify fields visibly and OEM radio/source return. |
| Native MHI2 wireless | Adapter-assisted wireless and a native receiver are different paths. | A production native wireless CarPlay stack for unmodified MHI2 is not provided. The prior qualification pilot was stopped, not completed. |
| Red menu scroll indicator | A project red indicator/source is included; target runtime native scrollbar discovery differed from firmware source assumptions. | Cold-start, Back/focus/scroll/re-entry and all skins are not comprehensively qualified. Preserve OEM navigation; do not install older diagnostic scrollbar kits. |
| Long-run reconnect/recovery | Raw-video queue recovery retains the consumer and re-primes from current codec data plus a fresh IDR. | Not every disconnect, long idle, phone sleep, app switch, power interruption or load condition has been exhaustively tested. Retain logs before restart/rollback when a failure occurs. |
| Dongle bench results | A bench can check upload, identity and retained build markers. | Functional acceptance requires the actual compatible car/head unit/cockpit. A bench head unit without its VC can give misleading black-screen/no-map results. |
| Pairing after a dongle flash | Stale phone-side pairing was observed during testing. | After completed flashing/restart, forget the old adapter Bluetooth/CarPlay connection and pair again. This does not make an incompatible firmware compatible. |
| Adapter hardware/firmware variants | Four specifically identified configurations are owner-reported working. | Shared housing/product_Model does not prove matching platform, vendor/custom, system or private ABI. Do not cross-flash HW301, AX1800 and AX1800M variants or remove guards. |
| Exact stock rollback | Each adapter package retains its stated stock fallback. | AX1800M October rollback is application-only, not original January or full flash. Mini5 fallback is March kernel/rootfs, not the original April image. Recovery depends on a reachable updater; no universal hardware rescue is established. |
| SEAT port scope | P4708/P4708_1 MU1409 inputs and exact preimages are checked; two firewall baseline variants are retained. | Other MU versions, brands, Java images, MHI2Q and unknown existing mods require qualification. A similar firmware name or past omonob success does not override failed hashes. |
| Layered car restoration | Each kit has its own backups and guarded restore. | Overlapping layers change receiver/startup preimages. Restore in reverse order and use the exact original kit; unknown changes or inaccessible SSH require independent recovery. |
| Rebuilding source | C/Java/shell project sources and build recipes are provided. | A licensed compatible QNX SDK/sysroot and exact locally supplied OEM API/hook inputs are not bundled. Source Download ZIP is not a universal compiled installer. |

## Corrections already included

- Fresh installation v0.2.1 creates the wp2 storage-anchor directory before activation, avoiding the previously observed storage-probe timeout. It does not enable a second retired settings service.
- Mini5 v0.2 corrects the 47 untranslated address literals and retains the exact-pointer guard. This is distinct from an ignored app zoom command.
- AX1800M/system202603120956CA independent v0.2 corrects the final initial-SETUP `enabledFeatures` lookup, not merely `/info` advertisement. The owner subsequently reports the adapter working.
- Original-H.264 queue recovery addresses the observed early stock/Waze switching caused by repeated consumer exits. It does not guarantee all future reconnect causes are eliminated.

## Reporting a failure

State the car model, exact firmware/MU, wired result, adapter platform/custom/model/system/protocol, package version, phone/iOS/app, and whether the centre screen or only cockpit maps fail. Capture status/logs before rebooting/rollback where possible. Do not post passwords, keys, VINs, device identifiers or complete personal log bundles publicly. Read the model-specific collection command in the adapter guide. A successful flash message alone is not a functional pass.
