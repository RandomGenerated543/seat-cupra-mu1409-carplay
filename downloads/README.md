# Downloads — experimental 2026-10-30

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY. Read [the disclaimer](../DISCLAIMER.md).**

Download the complete matching runtime ZIP from this versioned release. Keep its folder, manifests and rollback files together. GitHub source Download ZIP is not a compiled installer.

| File | Purpose / exact target |
|---|---|
| [HW301-CXZ521-app20260122129-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/HW301-CXZ521-app20260122129-v0.1.zip) | HW301 / CXZ521; original APP HW301_20250630126, system 20250320; candidate vendor v129 / HW301_20260122129 |
| [AX1800M-Suding-system202504180933CA-protocol20261008165747-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/AX1800M-Suding-system202504180933CA-protocol20261008165747-v0.2.zip) | AX1800M / suding / v851se-yunlian-cp; system 202504180933CA; protocol 20261008165747 |
| [Mini5Pro-AX1800-Yunlian-system202603120932CA-protocol20260109175612-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/Mini5Pro-AX1800-Yunlian-system202603120932CA-protocol20260109175612-v0.2.zip) | Mini 5 Pro / AX1800 / yunlian / v851se-yunlian-cp; original system 202504171406CA, protocol 20250415195209; full March base system 202603120932CA, protocol 20260109175612 |
| [AX1800M-Suding-system202603120956CA-protocol20261008165747-v0.2.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/AX1800M-Suding-system202603120956CA-protocol20261008165747-v0.2.zip) | AX1800M / suding / v851se-yunlian-cp; system 202603120956CA; original protocol 20260109175612, candidate October protocol 20261008165747 |
| [SEAT-MU1409-final-stack-v0.2.1-baseline-A.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/SEAT-MU1409-final-stack-v0.2.1-baseline-A.zip) | SEAT/Cupra P4708/P4708_1 MU1409; exact baseline A firewall hashes |
| [SEAT-MU1409-final-stack-v0.2.1-baseline-B.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/SEAT-MU1409-final-stack-v0.2.1-baseline-B.zip) | SEAT/Cupra P4708/P4708_1 MU1409; exact baseline B firewall hashes |
| [MU1409-menu-zoomfactor-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/MU1409-menu-zoomfactor-v0.1.zip) | Existing matching SEAT MU1409 project stack; cockpit menu zoom 70–150% plus omit |
| [MU1409-main-display-zoom-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/MU1409-main-display-zoom-v0.1.zip) | Existing matching SEAT MU1409 stack; centre-screen metadata zoom 70%; fixed/menu cockpit baselines |
| [MU1409-media-info-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/MU1409-media-info-v0.1.zip) | Existing matching SEAT MU1409 stack; VC Audio/Media title, artist, album |
| [MU1409-wide-safearea-v0.1.zip](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/MU1409-wide-safearea-v0.1.zip) | Existing matching three-view SEAT MU1409 profile; Wide 708x244@151,56 -> 628x220@191,56 |

## Integrity

Expected SHA-256 values are in [catalog.json](catalog.json) and the release SHA256SUMS.txt. On macOS: `shasum -a 256 FILE.zip`. On Windows PowerShell: `Get-FileHash .\FILE.zip -Algorithm SHA256`. The digest must match before extracting. Repacking changes ZIP checksums, so use this release catalogue; candidate/rollback image hashes inside IMAGES.json are retained.

Source: [SEAT port](../src), [adapter source archives](../adapters/source), and the versioned complete project source asset. Build dependencies and packing instructions are in [DEVELOPMENT_AND_PACKAGING.md](../docs/DEVELOPMENT_AND_PACKAGING.md).

[Complete latest SEAT/Cupra source snapshot](https://github.com/RandomGenerated543/seat-cupra-mu1409-carplay/releases/download/experimental-2026-10-30/SEAT-CUPRA-MU1409-source-2026-10-30.zip) includes the port, media, cockpit menu zoom, source variants and adapter source archives. Runtime assets are separate.
