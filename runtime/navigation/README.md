> Historical upstream/source reference. For this MU1409 handoff, start with ../../README.md and its target runbook; do not infer that older installation commands apply.

# Navigation / recovery runtime helpers

This directory contains the developer controls used by the current GEN2 line.

## Vehicle-tested helpers

- `gen2_keyframes.sh` — enables/disables the automatic D2 keyframe policy and reports counters.
- `gen2_resync.sh` — manual same-session D1 recovery control.
- `gen2_nav_config.sh` — live/persistent navigation surface and query controls.

These paths were exercised during the 2026-09-27 MU1440 vehicle run.

## Development helper

- `gen2_safearea.sh` — persistent SafeArea geometry configuration.

The SafeArea helper corresponds to newer build-confirmed source and has **not yet been vehicle
validated**.

Direct vehicle shell use remains developer-only. MU1440 is QNX; do not assume GNU/Linux utility
availability or option syntax.
