# Recovery

**Highly experimental; [read the disclaimer](../DISCLAIMER.md).**

The supplied receiver update saves the exact known scaled receiver before-image
under the project backup directory, verifies it, and installs its own recovery
script on the unit. Restoration is available without the removable medium:

```sh
/bin/ksh /mnt/app/root/altscreen-u2/queue-recovery/install.sh --restore
```

Then normally restart the unit and reconnect the phone. This returns to the
previous scaled receiver, retaining zoomFactor=70. It is not full OEM restoration.
Use this command only if this specific guarded update was installed successfully;
a missing recovery file is not permission to improvise another write.

For the pre-existing complete stack, retain and use its own per-unit backup and
uninstall/recovery procedure. No OEM backup from another car, firmware archive
preimage or downloaded startup file is a substitute for the actual live preimage.

Do not delete locks, disable ownership checks, kill displaymanager or replace
unknown native files to force a failed preflight. Collect the exact output first.
If SSH is unavailable, recover its ordinary connection independently; this
repository does not include credentials, a bypass or a guaranteed recovery path.
