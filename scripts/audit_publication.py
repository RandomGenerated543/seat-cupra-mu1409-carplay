#!/usr/bin/env python3
# Independent publication boundary: source, reviewed artwork, one exact receiver.
import pathlib,hashlib,re,sys,subprocess
r=pathlib.Path(__file__).resolve().parents[1]
expected="6165f72974b4ebea8f4a3e27a0354f20df98e29350b810b4e0ac4d5efcf7fce5"
errors=[]
for f in r.rglob("*"):
    if not f.is_file() or any(p in {".git","build","local-inputs","__pycache__"} for p in f.relative_to(r).parts):continue
    rel=str(f.relative_to(r));ext=f.suffix.lower()
    if f.name in {"startup.sh", "lsd.sh", "Activator.java", "WidgetFactoryImpl.java"}:errors.append("OEM integration input must remain local: "+rel)
    if ext in {".jxe",".ifs",".jar",".pem",".key",".secret",".core",".class"}:errors.append("forbidden public input/artifact: "+rel)
    if ext==".so":
        if rel!="deployment/receiver-upgrade/payload/libmibr_carplay111.so" or hashlib.sha256(f.read_bytes()).hexdigest()!=expected:errors.append("unreviewed native binary: "+rel)
    if ext==".java" and not re.search(rb"package\s+(?:de\.mibr\.hmi|mib\.mu1440\.vehiclespeed)\s*;",f.read_bytes()):errors.append("non-project Java package: "+rel)
    if ext in {".py",".c",".h",".inc",".java",".sh",".md",".json",".txt",".yml"}:
        data=f.read_bytes()
        if (b"/"+b"Users/") in data:errors.append("personal workspace path: "+rel)
        if b"-----BEGIN "+b"OPENSSH PRIVATE KEY-----" in data or b"-----BEGIN "+b"RSA PRIVATE KEY-----" in data:errors.append("private key: "+rel)
if errors:
    print("\n".join(errors));raise SystemExit(1)
print("PUBLICATION_BOUNDARY=PASS no_OEM_Java_firmware_SDK_credentials_or_unreviewed_binaries")
