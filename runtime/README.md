> Historical upstream/source reference. For this MU1409 handoff, start with ../../README.md and its target runbook; do not infer that older installation commands apply.

# Runtime reference

This directory contains project-owned **reference runtime logic and diagnostic helpers**.

It is not itself a packaged installer. The guarded exact-target developer orchestration lives under
`deployment/mu1440/`; it stages and invokes these lower-level runtime components.

## `auto-direct/`

Vehicle-tested reference state-machine logic for automatic takeover/recovery:

- common runtime helpers;
- write-gate control;
- supervisor;
- independent watchdog;
- start/stop/status;
- enable/disable reference logic;
- ScreenAlt configuration.

Read first:

- `docs/architecture/AUTO_DIRECT_RUNTIME.md`
- `docs/architecture/RUNTIME_CONTRACT.md`

Some scripts reflect the exact first MU1440 environment and are published so the real tested logic is
visible. Treat target paths as compatibility evidence, not universal MHI2 APIs.

## `diagnostics/`

Generic SSH-oriented helpers:

- `gen2_prereq.sh` — compatibility/hash preflight;
- `gen2_status.sh` — current Type-111/control/runtime state;
- `gen2_collect_logs.sh` — collect useful evidence without an SD layout;
- `gen2_reacquire.sh` — bounded same-session reacquire request;
- `gen2_resync.sh` — manual Candidate-D-style resync experiment.

These are intended to make external vehicle reports comparable.

## `isotx2-gate/`

Reference operator controls for the DisplayManager `writev()` interposer.

The project-owned native source lives at:

```text
src/native/isotx2-gate/
```

## `experimental/`

Experimental controls such as ViewArea feature toggles. Presence here does not imply a promoted
feature or a stable cross-platform interface.

## Developer deployment

The project does not require SD deployment as its architecture or runtime interface. For convenience,
`tools/prepare_mu1440_sd.sh` can assemble the exact-target developer payload into an SD directory.

The project still assumes existing SSH/recovery access. This is not a general end-user installation
promise or cross-firmware compatibility claim.
