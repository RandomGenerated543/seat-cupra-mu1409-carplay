#!/usr/bin/env python3
"""Package the public project source and original remux dependencies locally."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import zipfile


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--ffmpeg-tar", type=Path, required=True)
    a.add_argument("--wp1-project-source", type=Path, required=True)
    args = a.parse_args(); root = Path(__file__).resolve().parents[1]
    assert sha(args.ffmpeg_tar) == "b8c8e926b948c14df1264cd0beac1c773df9170ac9cac97bdf1275cd3d385902"
    assert sha(args.wp1_project_source) == "435bc24d134099f7ec88e4c64419aafab19bff35826465076f77e2eb033eec7e"
    subprocess.run(["python3", str(root / "scripts/audit_publication.py")], check=True)
    dest = root / "build/SEAT-MU1409-final-stack-sources-v0.2.zip"
    if dest.exists(): raise SystemExit("Source companion already exists")
    with zipfile.ZipFile(dest, "x", zipfile.ZIP_DEFLATED) as z:
        z.write(args.ffmpeg_tar, "dependencies/ffmpeg-6.1.5.tar.gz")
        z.write(args.wp1_project_source, "dependencies/historical-wp1-project-source.zip")
        for p in sorted(root.rglob("*")):
            if p.is_file() and not any(x in {".git", "build", "local-inputs", "__pycache__"} for x in p.relative_to(root).parts):
                z.write(p, "project-source/" + str(p.relative_to(root)))
        z.writestr("README.txt", "Corresponding-source companion for the local MU1409 final-stack candidate.\nContains project source/build recipes, original WP1/remux source snapshot,\nand the pinned FFmpeg 6.1.5 source. Retain LICENSE/LICENSES/per-file notices.\nBuild requires a separately obtained compatible QNX toolchain and local OEM\nmenu inputs; SDKs and vendor hooks/firmware are not supplied as public source.\nNo car scripts are automatically executed by opening this archive.\n")
    print("SOURCE_COMPANION=READY bytes=" + str(dest.stat().st_size))
