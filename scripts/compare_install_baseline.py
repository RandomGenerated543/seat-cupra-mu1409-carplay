#!/usr/bin/env python3
"""Compare a private collection with the recorded P4708_1 baseline; no writes."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("report", type=Path)
    args = a.parse_args()
    r = Path(__file__).resolve().parents[1]
    ref = json.loads((r / "deployment/full-install/reference-baseline.json").read_text())
    report = json.loads(args.report.read_text())
    if not report.get("complete"):
        raise SystemExit("COLLECTION_INCOMPLETE: recollect before comparing")
    matches = missing = differing = 0
    for name, expected in ref["files"].items():
        p = args.report.parent / name
        if not p.is_file():
            state = "MISSING"; missing += 1
        elif hashlib.sha256(p.read_bytes()).hexdigest() == expected:
            state = "MATCH"; matches += 1
        else:
            state = "DIFFERS"; differing += 1
        print(state + " " + name)
    print("SUMMARY matches=%d differs=%d missing=%d" % (matches, differing, missing))
    print("INSTALLATION_APPROVED=NO comparison_only=1")
    print("P4709 requires file/ABI/Java/startup review; matching files are evidence, not a bypass.")


if __name__ == "__main__":
    main()
