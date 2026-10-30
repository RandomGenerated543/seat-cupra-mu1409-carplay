# Cockpit views and SafeAreas

**Experimental. Use at your own risk.** All three views retain the 1010×376 outer canvas. SafeArea asks the phone/app to keep important content within an inner rectangle. It does not add black padding, rescale pixels or remove the cockpit's vignette.

| View | Foundation SafeArea | Origin x,y |
|---|---|---|
| Wide | 708×244 | 151,56 |
| Full | 482×244 | 264,56 |
| Center | 256×244 | 377,56 |

The optional MU1409-wide-safearea-v0.1 update changes **only Wide** to **628×220 at 191,56**. The left edge moves inward 40 source pixels and the bottom rises 24; the phone/app controls actual ETA and maneuver placement. Full/Center retain their values. Waze has previously hidden/obscured information in reduced views even when switching succeeded; do not promise every app fits.

Download/extract the complete folder, unplug the phone, leave the menu and run:

```sh
/bin/ksh /fs/sda0/MU1409-wide-safearea-v0.1/install.sh --check
/bin/ksh /fs/sda0/MU1409-wide-safearea-v0.1/install.sh --apply
```

Only apply after WIDE_SAFEAREA_CHECK=PASS. Restart normally, create a fresh CarPlay session, select Wide and photograph directions, ETA, arrow and boundaries.

```sh
grep -F 'SEAT_VIEW preset=0' /tmp/altscreen111.log | tail -3
/bin/ksh /fs/sda0/MU1409-wide-safearea-v0.1/install.sh --status
```

Expected updated geometry is safe=628x220@191,56. Restoration uses --restore-check, then --restore after PASS, then restart. It restores only Wide's geometry keys and preserves unrelated preferences. Do not blindly copy an old whole profile over subsequently edited settings.
