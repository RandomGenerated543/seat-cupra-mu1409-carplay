#!/usr/bin/env python3
"""Parse stock MU1440 keypanel trace lines.

Expected stock logger line:
  HK Received: KBD[4] KEY[50] KST[1]

This tool runs off-unit. It does not modify the MHI2.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

RX = re.compile(r"HK Received:\s*KBD\[(\d+)\]\s*KEY\[(\d+)\]\s*KST\[(\d+)\]")

KBD = {
    4: "KBD_MFW",
}

KEY = {
    35: "KEY_MFW_MENU",
    36: "KEY_MFW_ARROW_RIGHT",
    37: "KEY_MFW_ARROW_LEFT",
    38: "KEY_MFW_UP",
    39: "KEY_MFW_DOWN",
    40: "KEY_MFW_ROLLER_LEFT",
    41: "KEY_MFW_CANCEL",
    42: "KEY_MFW_VOLUME_UP",
    43: "KEY_MFW_VOLUME_DOWN",
    44: "KEY_MFW_ROLLER_RIGHT",
    45: "KEY_MFW_AUDIOSOURCE",
    46: "KEY_MFW_ARROW_A_UP",
    47: "KEY_MFW_ARROW_A_DOWN",
    48: "KEY_MFW_ARROW_B_UP",
    49: "KEY_MFW_ARROW_B_DOWN",
    50: "KEY_MFW_PTT_ON",
    51: "KEY_MFW_PTT_CANCEL",
    52: "KEY_MFW_INFO",
    53: "KEY_MFW_HOOK",
    54: "KEY_MFW_HANGUP",
    55: "KEY_MFW_OFFHOOK",
    56: "KEY_MFW_LIGHT",
    57: "KEY_MFW_MUTE",
    58: "KEY_MFW_JOKER1",
    59: "KEY_MFW_JOKER2",
    60: "KEY_MFW_INIT",
    99: "KEY_MFW_SIDEMENULEFT",
    100: "KEY_MFW_SIDEMENURIGHT",
    114: "KEY_SMARTPHONE",
    116: "KEY_HOME",
}

KST = {
    0: "KST_RELEASED",
    1: "KST_PRESSED",
    2: "KST_DOUBLEPRESSED",
    3: "KST_LONGPRESSED",
    4: "KST_LONGPRESSED2",
    5: "KST_LONGPRESSED3",
    6: "KST_APPROACHED",
    7: "KST_ABANDONED",
    8: "KST_MOVED",
}

NOTE_RX = re.compile(r"(?:^|\s)NOTE\s+(.*)$")


def lines_for(path: str | None):
    if path in (None, "-"):
        yield from sys.stdin
        return
    with Path(path).open("r", errors="replace") as f:
        yield from f


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("trace", nargs="?", default="-", help="trace file or - for stdin")
    ap.add_argument("--csv", action="store_true", help="emit CSV")
    ap.add_argument("--summary", action="store_true", help="summarize unique raw keys and state counts")
    ap.add_argument(
        "--gestures",
        action="store_true",
        help="reconstruct PRESS/SHORT/DOUBLE/LONG stages and preserve NOTE markers",
    )
    args = ap.parse_args()

    rows = []
    items = []
    for line_no, line in enumerate(lines_for(args.trace), 1):
        note = NOTE_RX.search(line)
        if note:
            items.append({"type": "note", "line": line_no, "text": note.group(1).strip()})
            continue
        m = RX.search(line)
        if not m:
            continue
        kbd, key, kst = map(int, m.groups())
        row = {
            "line": line_no,
            "kbd": kbd,
            "kbd_name": KBD.get(kbd, "KBD_UNKNOWN"),
            "key": key,
            "key_name": KEY.get(key, "KEY_UNKNOWN"),
            "kst": kst,
            "state_name": KST.get(kst, "KST_UNKNOWN"),
        }
        rows.append(row)
        items.append({"type": "event", **row})

    if args.gestures:
        active: dict[tuple[int, int], dict[str, bool]] = {}
        emitted = 0
        for item in items:
            if item["type"] == "note":
                print(f"{item['line']:6d} NOTE {item['text']}")
                emitted += 1
                continue

            k = (item["kbd"], item["key"])
            kst = item["kst"]
            gesture = None

            if kst == 1:
                active[k] = {"long": False, "double": False}
                gesture = "PRESS"
            elif kst == 2:
                active.setdefault(k, {"long": False, "double": False})["double"] = True
                gesture = "DOUBLE"
            elif kst in (3, 4, 5):
                active.setdefault(k, {"long": False, "double": False})["long"] = True
                gesture = {3: "LONG", 4: "LONG2", 5: "LONG3"}[kst]
            elif kst == 0:
                state = active.pop(k, None)
                if state is None:
                    gesture = "RELEASE"
                elif state["long"]:
                    gesture = "LONG_RELEASE"
                elif state["double"]:
                    gesture = "DOUBLE_RELEASE"
                else:
                    gesture = "SHORT"
            elif kst == 6:
                gesture = "APPROACHED"
            elif kst == 7:
                gesture = "ABANDONED"
            elif kst == 8:
                gesture = "MOVED"
            else:
                gesture = item["state_name"]

            print(
                f"{item['line']:6d} GESTURE={gesture:<14} "
                f"KBD={item['kbd']:3d} {item['kbd_name']:<12} "
                f"KEY={item['key']:3d} {item['key_name']:<24} "
                f"KST={item['kst']:2d} {item['state_name']}"
            )
            emitted += 1

        if not emitted:
            print("No keypanel events or NOTE markers found.", file=sys.stderr)
            return 1
        return 0

    if args.summary:
        grouped: dict[tuple[int, int], dict[int, int]] = {}
        names: dict[tuple[int, int], tuple[str, str]] = {}
        for r in rows:
            k = (r["kbd"], r["key"])
            grouped.setdefault(k, {})
            grouped[k][r["kst"]] = grouped[k].get(r["kst"], 0) + 1
            names[k] = (r["kbd_name"], r["key_name"])
        for kbd, key in sorted(grouped):
            kbd_name, key_name = names[(kbd, key)]
            states = ", ".join(
                f"{KST.get(state, 'KST_UNKNOWN')}={count}"
                for state, count in sorted(grouped[(kbd, key)].items())
            )
            print(
                f"KBD={kbd:3d} {kbd_name:<12} "
                f"KEY={key:3d} {key_name:<24} "
                f"events={sum(grouped[(kbd, key)].values()):4d} "
                f"{states}"
            )
    elif args.csv:
        w = csv.DictWriter(
            sys.stdout,
            fieldnames=["line", "kbd", "kbd_name", "key", "key_name", "kst", "state_name"],
        )
        w.writeheader()
        w.writerows(rows)
    else:
        for r in rows:
            print(
                f"{r['line']:6d} "
                f"KBD={r['kbd']:3d} {r['kbd_name']:<12} "
                f"KEY={r['key']:3d} {r['key_name']:<24} "
                f"KST={r['kst']:2d} {r['state_name']}"
            )

    if not rows:
        print("No 'HK Received: KBD[...] KEY[...] KST[...]' lines found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
