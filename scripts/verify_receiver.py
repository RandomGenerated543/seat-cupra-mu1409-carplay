#!/usr/bin/env python3
import hashlib,pathlib,sys
EXPECTED="6165f72974b4ebea8f4a3e27a0354f20df98e29350b810b4e0ac4d5efcf7fce5"
p=pathlib.Path(sys.argv[1]);digest=hashlib.sha256(p.read_bytes()).hexdigest()
print("receiver_sha256="+digest)
if digest!=EXPECTED:
    raise SystemExit("RECEIVER_IDENTITY=MISMATCH do_not_substitute_into_guarded_update")
print("RECEIVER_IDENTITY=EXACT_TESTED_BUILD")
