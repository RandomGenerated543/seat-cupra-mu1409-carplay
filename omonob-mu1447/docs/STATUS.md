# Vehicle reports, local validation and open issues

Publication: **22 November 2026**. Highly experimental, exact-target installation only.

## Latest vehicle report on 23 November 2026

The owner reports that the car is **working perfectly, with no bugs currently observed**. This supersedes the earlier failure reports as the latest description of this car's operation. The successful configuration previously reported keeps the WLAN hotspot enabled and disables the Wi-Fi internet client and automatic search/join.

See the [full implementation review](IMPLEMENTATION-REVIEW.md) and the [dated operator report](../validation/OPERATOR-REPORT-2026-11-23.json). No new live-file receipt, measured test duration or individual scenario checklist accompanied this update; it is an owner report for the current car, not universal compatibility qualification. The historical test records and original archive hashes remain unchanged.

## What the operator reported

The operator used a SEAT/Cupra P4709 / MU1447 unit with a 790-family cockpit and stated that all current corrections were installed. The Runtime v0.1 preflight output showed a matching live receiver, a read-only session inspection and successful 10-class J9 linkage checking without activators.

Two complete wireless sessions ended during the first minute after startup. The receiver log contained `ECONNRESET` and timeout/connection errors. The receiver stayed alive under its original PID and later reported an active session. The capture also showed channel 11 changing to 9, the firewall source changing to the home-Wi-Fi variant and zero interface drops in the captured snapshot. A zero counter snapshot is not a radio packet-loss proof.

The operator disabled the car's internet-client/uplink function, kept the car hotspot enabled and tested a fresh startup. They then reported **no further disconnect and noticeably smoother interaction**. The duration was not recorded precisely. No personal captures, SSIDs, MAC addresses, public pairing identifier, VIN or credentials are published here.

This supports an uplink/hotspot startup interaction. It does not isolate channel migration from firewall/NAT reconfiguration or contention, nor establish reliable concurrent uplink and CarPlay operation. The recommended test configuration is **internet client off / hotspot on**.

## What the correction tests establish

Runtime tests reproduce and check camera/touch ownership ordering, deferred screen claims, bounded asynchronous touch forwarding, delayed readiness, registration retries/cleanup, real receiver-session versus main-video state and file transactions with rollback. Native lock/status/PID routines are host-tested and receiver fingerprints are checked across the three recognized receiver variants. The QNX read-only process inspection is additionally gated on the real unit.

Startup tests run the patched CP worker with simulated OEM/network boundaries: the older readiness wait was approximately one second; the screen-event wake removed that wait in the host test. Tests cover a notification arriving just before wait, retain the original idle wait, and rerun camera/touch/registration regressions. This is not an on-car touch-to-picture benchmark.

Original package build-time notes remain unchanged. Later operator reports supplement them; they do not rewrite all build-time `UNTESTED` fields into blanket acceptance. See [validation records](../validation).

## Scope still unqualified

- Concurrent home-Wi-Fi uplink and native CarPlay is not reliably qualified; the current successful configuration disables the uplink.
- Longer drives, recurring freeze/touch-loss diagnosis, repeated camera/reversing transitions, calls and overnight reconnect still need extended vehicle testing.
- No claim that every camera, touch or video freeze has the same cause or is eliminated.
- Wireless media metadata/artwork is not independently validated. Existing upstream media/artwork startup is preserved.
- Navigation-app rendering, ETA, directions, speed-limit defaults and app switching depend on the phone/app response. A requested safe area or `showETA=yes` is not an independent display acceptance.
- The requested 30 fps is a ceiling, not a guaranteed measured rate. There is no 60 fps qualification.
- Other firmware, clusters, hardware, iOS versions and phones are not established compatible by this report.
- Some local rebuild scripts require the retained exact donor/firmware and workspace dependencies; this is not a source release of opaque third-party receiver/OEM components.

The cockpit vignette investigation is outside this branch's feature/issue scope; there is no vignette-removal patch in these packages.
