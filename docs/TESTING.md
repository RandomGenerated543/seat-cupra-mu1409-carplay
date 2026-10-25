# Parked tester runbook

**HIGHLY EXPERIMENTAL. USE AT YOUR OWN RISK. NO WARRANTY.**
Read [DISCLAIMER](../DISCLAIMER.md), [prerequisites](PREREQUISITES.md) and
[recovery](RECOVERY.md). This is not a universal fresh-install package.

## Workstation first

Run scripts/audit_publication.py and scripts/test_host.py. Read BUILD.md.
Check source/component hashes, exact target identity and your baseline/recovery
before copying anything. Never infer compatibility from successful compilation.

## Guarded receiver upgrade on an already matching project stack

Copy deployment/receiver-upgrade as one complete folder to the medium root.
Unplug the phone. On the unit, use /bin/ksh and the actual folder path:

```sh
/bin/ksh /fs/sda0/receiver-upgrade/install.sh --check
```

Only after a clean preflight and an independently reviewed before-image:

```sh
/bin/ksh /fs/sda0/receiver-upgrade/install.sh --apply
```

Normally restart, reconnect wired CarPlay and use the same app/route/physical
cluster layout. Observe startup and map updates for at least two minutes.
Confirm main-screen CarPlay and stock vehicle information remain functional.

Read the receiver log for IOS_ZOOM_TEST and QUEUE_RECOVERY entries; those prove
advertisement/recovery events, not actual phone scaling or visual success.
A full queue should request a fresh IDR, retain the consumer generation and
resume. Repeated recovery/frozen/stale output is a failed test.

## Separate acceptance checkpoints

1. Original infotainment and OEM navigation baseline.
2. Wired map output and startup continuity; no OEM/Waze cycling.
3. SafeArea/card visibility in Wide; Full/Center remain candidates.
4. Roller rotation in both directions in Apple Maps and Google Maps.
   Record Waze separately; it did not visibly respond in the observed tests.
5. Menu Back/focus/scroll/re-entry and actual effect/readback of one setting.
6. Phone unplug: deliberate stock fallback; reconnect: fresh working projection.
7. Normal restart with persistent configuration and correct single-owner state.
8. Independently verify restoration; the receiver-only rollback is not OEM reset.

Record outcomes in RESULT_TEMPLATE.md. Redact credentials, phone identifiers
and personal route/location details before sharing. Photos are helpful but
should be deliberately selected for publication by their owner.
