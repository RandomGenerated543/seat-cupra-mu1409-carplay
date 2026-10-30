> **2026-10-30 publication:** Start with [the beginner guide](NEWBIE_INSTALL.md) and [versioned downloads](../downloads/README.md). Older filenames/hashes below describe the retained foundation build; do not mix them with newer feature payloads.

# Status — 25 October 2026

**Highly experimental; [use at your own risk](../DISCLAIMER.md).**

## Observed on one CUPRA Ateca MU1409 adaptation

Wired maps, autostart, effective CarPlay TCP6031 allowance, English menu,
arrival-time effect, and right-wheel semantic zoom with Apple Maps/Google Maps
were reported working. Numeric zoomFactor=70 improved visible map size without
software decode/resize/encode or padding. The guarded raw-Annex-B overflow
correction recovered with the same consumer generation and was visibly reported
to work in the observed test.

## Source snapshot identity

The exact receiver source is src/native/altscreen111-gen2. The supplied guarded
update targets an existing scaling-test receiver, or its own already-installed
result. It restores to the scaling-test receiver, retaining zoomFactor=70.
The gate, writer and native owner-protocol-2 helpers come from the earlier
qualified target stack. The source files do not constitute universal compatibility.

## Outstanding

The consolidated v0.2 fresh-install candidate is now assembled locally;
see CONSOLIDATED_INSTALL.md and INSTALL_VALIDATION.md. This adds an installation
route, not a new claim of vehicle acceptance.

- Repeated cold boot, phone reconnect, longer runs and independent restoration
  of the combined latest state.
- Red scrollbar appearance and repeated menu re-entry.
- Full/Center directions and ETA visibility with fitted OEM dial layouts.
- Different iPhone/iOS versions, other navigation apps and other vehicles.
- Fresh-install integration/qualification on a second unit.
- Locally provided OEM hooks/API inputs for a rebuilt menu; these are not public
  project-owned files and are deliberately not bundled.

The iPhone software version for the successful scaling observation was not
recorded. Physical metadata is an advertisement, not a measured panel size.
