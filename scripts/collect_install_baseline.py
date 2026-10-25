#!/usr/bin/env python3
"""Host-only, read-only collection over one SSH connection. Never installs.

Keep the output private: it contains OEM files and may contain unit identifiers.
The SSH client handles password entry directly; this program never requests it.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

FILES = {
    "libairplay.so": "/mnt/app/eso/lib/libairplay.so",
    "dio_manager": "/mnt/app/eso/bin/apps/dio_manager",
    "displaymanager": "/eso/bin/apps/displaymanager",
    "smartphone_integrator": "/mnt/app/eso/bin/apps/smartphone_integrator",
    "startup.sh": "/mnt/system/etc/boot/startup.sh",
    "smartphone_integrator.json": "/mnt/system/etc/eso/production/smartphone_integrator.json",
    "lsd.sh": "/mnt/app/eso/hmi/lsd/lsd.sh",
    "NavActiveIgnore.jar": "/mnt/app/eso/hmi/lsd/jars/NavActiveIgnore.jar",
    "pf.conf": "/mnt/system/etc/pf.conf",
    "pf.mlan0.conf": "/mnt/system/etc/pf.mlan0.conf",
    "displaymanager.json": "/etc/eso/production/displaymanager.json",
}
MAX_FILE_BYTES = 128 * 1024 * 1024


def read_exact(stream, size):
    chunks = []
    while size:
        block = stream.read(min(size, 65536))
        if not block:
            raise ValueError("Interrupted transfer; preserve partial folder and collect into a new folder")
        chunks.append(block)
        size -= len(block)
    return b"".join(chunks)


def receive(stream, directory, files):
    result = {}
    for name, remote in files.items():
        header = stream.readline(256).decode("ascii").strip().split()
        if header == ["MISSING", name]:
            result[name] = {"remote": remote, "status": "MISSING"}
            continue
        if len(header) != 3 or header[:2] != ["FILE", name] or not header[2].isdigit():
            raise ValueError("Unexpected SSH framing: " + repr(header))
        size = int(header[2])
        if not 0 <= size <= MAX_FILE_BYTES:
            raise ValueError("Invalid file length")
        data = read_exact(stream, size)
        delimiter = ("\nEND " + name + "\n").encode()
        if read_exact(stream, len(delimiter)) != delimiter:
            raise ValueError("Remote file changed/truncated during copy: " + name)
        p = directory / name
        with p.open("xb") as f:
            f.write(data)
        p.chmod(0o600)
        result[name] = {"remote": remote, "status": "COPIED", "bytes": size,
                        "sha256": hashlib.sha256(data).hexdigest()}
        print("READ_ONLY_COPY " + name + " bytes=" + str(size), flush=True)
    if stream.readline(256) != b"RUNTIME\n":
        raise ValueError("Missing runtime frame")
    # Bound the diagnostic tail too. Never interpret it as instructions.
    runtime = stream.read(2 * 1024 * 1024 + 1)
    if len(runtime) > 2 * 1024 * 1024:
        raise ValueError("Unexpected diagnostic size")
    (directory / "runtime-private.txt").write_bytes(runtime)
    return result


def remote_command(files):
    lines = ["set -u"]
    for name, path in files.items():
        lines += ["F=" + shlex.quote(path),
                  'if [ -f "$F" ] && [ -r "$F" ]; then',
                  ' N=$(wc -c < "$F") || exit 21',
                  " printf 'FILE %s %s\\n' " + shlex.quote(name) + ' "$N"',
                  ' cat "$F" || exit 22',
                  " printf '\\nEND %s\\n' " + shlex.quote(name),
                  "else printf 'MISSING %s\\n' " + shlex.quote(name) + "; fi"]
    lines += ["printf 'RUNTIME\\n'", "uname -a", "pidin ar",
              "ls -ld /mnt/app/root/altscreen-u2 /mnt/app/eso/lib/libmibr_carplay111.so /dev/mlb/isoTX2 2>&1",
              "/armle/sbin/pfctl -sr 2>&1", "exit 0"]
    return "/bin/ksh -c " + shlex.quote("\n".join(lines))


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--host", required=True, help="Example: root@192.168.50.242; use this unit's address")
    a.add_argument("--firmware", required=True, help="Full version from the unit, not only P4709")
    a.add_argument("--state", choices=["omonob-installed", "post-uninstall-reboot"], required=True)
    a.add_argument("--out", type=Path, required=True, help="New private local folder; never upload to GitHub")
    a.add_argument("--include-jxe", action="store_true", help="Also copy lsd.jxe for Java comparison; larger transfer")
    args = a.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+", args.host) or args.host.startswith("-"):
        a.error("Use user@hostname or user@IPv4")
    files = dict(FILES)
    if args.include_jxe:
        files["lsd.jxe"] = "/ifs/lsd.jxe"
    # Restrict local permissions before collecting any OEM/user-specific input.
    os.umask(0o077)
    args.out.mkdir(parents=True, exist_ok=False)
    report = {"format": 1, "declared_firmware": args.firmware, "declared_state": args.state,
              "vehicle_writes": 0, "installation_approved": False, "complete": False}
    proc = None
    try:
        proc = subprocess.Popen(["ssh", "-T", "-o", "ControlPath=none", "-o",
            "HostKeyAlgorithms=+ssh-rsa", "-o", "ServerAliveInterval=15", "-o",
            "ServerAliveCountMax=2", args.host, remote_command(files)], stdout=subprocess.PIPE)
        report["files"] = receive(proc.stdout, args.out, files)
        rc = proc.wait()
        if rc:
            raise ValueError("SSH failed rc=" + str(rc))
        report["complete"] = True
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            proc.wait()
        (args.out / "REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    print("COLLECTION=COMPLETE vehicle_writes=0 installation_approved=0 keep_output_private=1")


if __name__ == "__main__":
    main()
