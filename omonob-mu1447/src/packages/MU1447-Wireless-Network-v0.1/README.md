# MU1447 wireless network classification correction v0.1

**Experimental candidate. Disconnect prevention is not yet vehicle-validated.**

For the installed MU1447 native wireless rc1–rc1.3 build only. This updates two scripts and no receiver/Java/layout/driver binaries. It restores explicit use of the existing OEM hotspot control, audio and video ALTQ queues; both video ports6030/6031 are included. Time-sync traffic leaving UDP6020 is assigned to the control queue. The watchdog checks a stable rule label rather than relying on a particular rendering of dynamic interface addresses.

Why: the installed MU1447 scripts allowed CarPlay ports but did not classify them into the factory priority queues. The reported connection timeouts, ENOBUFS sends, hotspot drops and degradation during SSH make scheduling a useful correction to evaluate. They do not prove this omission explains every disconnect. Drops while joining/leaving home Wi-Fi may also involve shared-radio channel transitions or an OEM policy reload. Drop totals are cumulative, and an mbuf sample after stopping CarPlay does not establish earlier global exhaustion.

The correction is relevant with or without a home Wi-Fi uplink. It does not disable or change the home connection, hotspot, radio mode, credentials, queue definitions, bitrate, frame rate, SSH configuration or saved CarPlay pairing. Every original line of the selected OEM firewall source is preserved. The generated active firewall policy is still loaded at runtime; persistent `/etc/pf*.conf` files are not changed.

Use at your own risk, without warranty. The safe-area work remains separate and is not included. The parking-return issue that clears after a touch is not changed here.

## Install

Extract `MU1447-Wireless-Network-v0.1` to the SD root. In the car's SSH terminal:

```sh
cd /fs/sda0/MU1447-Wireless-Network-v0.1
/bin/ksh ./install.sh --check
```

Require `MU1447_NETWORK_CHECK=PASS native_pf_syntax=PASS`. This validates the exact two installed scripts, selects the current OEM NAT profile, requires the expected factory queues, generates an isolated RAM candidate and asks the unit's native `pfctl -n` to parse it. It does not load rules, alter the current session or change persistent files. If this fails, save the output and do not apply.

Then:

```sh
/bin/ksh ./install.sh --apply
```

Require `MU1447_NETWORK=INSTALLED manual_restart_required=1`, then restart normally. The current active session is not modified before restart. The new connection after restart receives the new state/queue classification; no global state flush is performed. Leave the Wi-Fi configuration unchanged while checking reconnect behavior, so deliberate network transitions do not confound the result.

No benefit is claimed until the car remains connected through the conditions that previously triggered drops, including an SSH session. If drops continue, preserve the fresh receiver log and queue statistics; do not repeatedly switch radio modes or stack other packages.

## Restore

To undo just this correction:

```sh
cd /fs/sda0/MU1447-Wireless-Network-v0.1
/bin/ksh ./install.sh --restore
```

Require `MU1447_NETWORK=RESTORED`, then restart normally. Backup: `/mnt/app/.mu1447-wireless-network-v01`. Keep it. Reapplying after restoration is deliberately refused until the retained backup is reviewed.

**Before uninstalling the whole wireless build with its original rc1.3 installer, restore this network correction first.** The base installer verifies its original script hashes and will otherwise refuse the changed files. This package does not rewrite the original wireless backup/receipt.

## Validation

Host fixtures passed for all four exact extracted MU1447 policy profiles: original NAT/SSH/filter lines preserved, required queue classification added, missing queues refused, preflight and native-parser rejection produce no persistent changes, installation is idempotent, backup seal verification and byte-exact restoration succeed. The host test stubs `pfctl`, mount and the native file-check tool. Actual PF syntax is an explicit mandatory gate on the car; RF behavior, session stability and live queue performance are not established by host tests.

Source scripts and test fixture are included. Based on the supplied omonob network scripts and the existing SEAT-port queue-classification approach. Existing upstream notices are retained. The public project GPL notice does not relicense OEM inputs. No firmware image, private keys or credentials are bundled.
