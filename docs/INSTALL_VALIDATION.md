# Consolidated v0.2 validation — 2026-10-25

The final-stack candidate was assembled locally from pinned retained inputs.
It does not install the old sequence of intermediate receivers. No vehicle was
accessed or modified while preparing this installer.

Host checks passed:

- Read-only preflight leaves mock original files unchanged and creates no
  production backup/runtime directory.
- A wrong immutable native hash rejects apply before any original-file change.
- Apply and repeat apply preserve the verified original backups.
- Restore returns all five activation/configuration files to the original bytes
  and retains edited user preferences inert.
- The persistent recovery copy works in the fixture after the SD kit is removed.
- A corrupted original backup refuses restoration before changing original files.
- An injected activation-file rename failure restores all five original files.
- Package file hashes, menu class format 46, selected ELF32/ARM artifacts and
  final receiver identity were checked.
- The fresh three-view settings profile validates against the actual project
  settings implementation on the host.
- The installer passes the retained static target-shell gate.
- Receiver queue/view tests and menu-indicator host tests continue to pass.

Mount operations, PF/J9 execution and process probes were mocked in the host
installer tests. The on-unit `--check` runs the real firmware hash checks,
PF parser and J9 probe. Neither host success nor target preflight establishes
visible video/menu behavior, real power-loss recovery or second-unit acceptance.

The complete fresh installer and restore remain **VEHICLE UNTESTED**. Existing
component observations are recorded separately in STATUS.md. Do not describe
the newly consolidated installer as an already vehicle-tested release.

Local SD ZIP SHA256:
`4f568c12cf9a7396efa0814c7bd5994bddead556773c446825895a9dffab7e06`

This hash identifies the locally generated candidate, not a public release asset
or a promise of compatibility with a differing baseline.
