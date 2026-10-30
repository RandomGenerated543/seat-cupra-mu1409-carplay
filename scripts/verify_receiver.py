#!/usr/bin/env python3
import argparse,hashlib,pathlib
parser=argparse.ArgumentParser(description="Verify one exact versioned receiver; never substitute across broker/menu versions")
parser.add_argument("file",type=pathlib.Path)
parser.add_argument("--profile",choices=["foundation","menu-zoom"],default="foundation")
args=parser.parse_args()
EXPECTED={"foundation":"6165f72974b4ebea8f4a3e27a0354f20df98e29350b810b4e0ac4d5efcf7fce5",
          "menu-zoom":"d14ce7650e2e9eded14883b3af60c3209af772fefb17e61b58eab3a4a2bfedd8"}[args.profile]
p=args.file;digest=hashlib.sha256(p.read_bytes()).hexdigest()
print("receiver_sha256="+digest)
if digest!=EXPECTED:
    raise SystemExit("RECEIVER_IDENTITY=MISMATCH do_not_substitute_into_guarded_update")
print("RECEIVER_IDENTITY=EXACT_PINNED_BUILD profile="+args.profile+" visible_effect=OPERATOR_CHECK_REQUIRED")
