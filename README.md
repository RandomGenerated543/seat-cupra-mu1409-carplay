# SEAT/CUPRA MU1409 CarPlay — experimental tester/source handoff

> **HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY.**
> The maintainer/authors/contributors exclude liability to the extent permitted
> by applicable law. This may disrupt or disable infotainment/cockpit functions.
> **Parked testing only; verified backups and independent recovery required.**
> Read [the full disclaimer](DISCLAIMER.md) before continuing.

This repository preserves the latest target-adapted project source used during
the CUPRA Ateca MU1409 tests, plus its build dependencies, settings/control source,
menu changes, tests and documentation. It builds on
[harman-f/mhi2_altscreen_carplay](https://github.com/harman-f/mhi2_altscreen_carplay).
It is an unofficial contribution, not a Harman/Apple/SEAT/CUPRA-supported product.

## Start here

1. [Status and known limitations](docs/STATUS.md).
2. [Exact-target prerequisites](docs/PREREQUISITES.md).
3. [Build from source](docs/BUILD.md).
4. [Tester runbook and acceptance checklist](docs/TESTING.md).
5. [Recovery](docs/RECOVERY.md).

**This is a developer handoff, not a universal SD-card installer.** A guarded
receiver update is supplied only for the already-installed exact compatible
project stack. Do not copy it over omonob, stock firmware or an unknown profile.
Fresh installation/control-menu binding needs per-unit integration and locally
supplied OEM inputs. Do not bypass a rejected hash or compatibility check.

## Preserved tested configuration

- Target: CUPRA Ateca, MHI2_ER_SEG11_P4708_1 / MU1409, fitted Continental 790 family.
- Wired authenticated CarPlay -> Type-111 H.264 -> TS remux -> one guarded MOST
  writer, /dev/mlb/isoTX2, 64 x 188-byte blocks.
- Outer advertisement 1010 x 376, physical metadata 200 x 74.
- Numeric lowercase zoomFactor=70 on the auxiliary display only.
- Bounded raw-Annex-B queue recovery keeps the consumer connected and resumes
  from current SPS/PPS plus a fresh IDR after dropping only unsent backlog.
- Working target wheel bridge uses measured keyboard 4 / encoder 40 correlated
  rotation. Apple Maps/Google Maps visibly responded; Waze did not.
- Wide SafeArea 708 x 244 @151,56; Full 482 x 244 @264,56;
  Center 256 x 244 @377,56. Reduced-layout information placement is unresolved.
- R13 project-owned English menu/control source with the later dropdown and
  red-scrollbar source overlays. The red indicator's vehicle appearance/re-entry
  still needs explicit confirmation.

## Evidence boundaries

The operator reported improved map sizing and working recovery. A logged
overflow at 51.310 s was followed by keyframe request at 51.316 and re-priming at
51.457, with consumer generation 3 unchanged. This is receiver-log timing,
not a measured end-to-end display latency. Repeated cold starts/reconnect,
long-run reliability and every fallback path were not fully qualified.

No OEM firmware/JXE/IFS files, recovered vendor Java, QNX SDK/sysroot,
credentials or raw personal captures are included. Project-owned Harman R13
source is included with publication permission confirmed by the repository owner.
Locally rebuilt menu artifacts can include OEM-derived hooks and must remain
local unless their separate redistribution rights are established.

## Upstream work

Related focused contributions:
[menu/dropdown #68](https://github.com/harman-f/mhi2_altscreen_carplay/pull/68),
[scaling/recovery #69](https://github.com/harman-f/mhi2_altscreen_carplay/pull/69),
[scrollbar #70](https://github.com/harman-f/mhi2_altscreen_carplay/pull/70),
[view calibration #71](https://github.com/harman-f/mhi2_altscreen_carplay/pull/71),
[wheel zoom #72](https://github.com/harman-f/mhi2_altscreen_carplay/pull/72).
Those newer public integrations are separate from this older exact tested
receiver snapshot; do not mix their ABI/transport sources piecemeal.

Source/component origins and hashes are in SOURCE_PROVENANCE.json.
See [licenses and attribution](THIRD_PARTY_NOTICES.md).
