#!/usr/bin/env python3
"""Host-only final-stack assembly. Generated OEM-derived payload stays local."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def assemble(inputs, baseline, out, root):
    spec = json.loads((root / "deployment/full-install/inputs.json").read_text())
    reference = json.loads((root / "deployment/full-install/reference-baseline.json").read_text())["files"]
    if out.exists() or Path(str(out) + ".zip").exists():
        raise ValueError("Select a fresh output directory")
    # Validate the external originals used for local-only firewall generation.
    for name in ["pf.conf", "pf.mlan0.conf"]:
        if sha(baseline / name) != reference[name]:
            raise ValueError("Unqualified firewall baseline: " + name)
    out.mkdir(parents=True); (out / "payload").mkdir()
    targets = []
    used = {}
    def cp(rel, name):
        src = inputs / rel
        if rel not in spec or not src.is_file() or src.is_symlink() or sha(src) != spec[rel]:
            raise ValueError("Unqualified retained input: " + rel)
        dest = out / "payload" / name
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src, dest)
        dest.chmod(0o755)
        used[rel] = spec[rel]
        return "payload/" + name
    def own(rel, name):
        dest = out / "payload" / name
        shutil.copyfile(root / rel, dest); dest.chmod(0o755)
        return "payload/" + name
    def new(src, target, perm="755"):
        targets.append(["new", "new%d" % len(targets), src, target, "absent", sha(out / src), perm])
    def replace(src, target, before, ident, perm="755"):
        targets.append(["replace", ident, src, target, reference[before], sha(out / src), perm])
    base = "/mnt/app/root/altscreen-u2"
    wp1 = "SEAT-MU1409-WP1-candidate-v0.1.4/"
    r13 = "MU1409-Harman-R13-migration-v0.1/"
    receiver = cp("MU1409-queue-recovery-v0.1/payload/libmibr_carplay111.so", "receiver.so")
    new(receiver, "/mnt/app/eso/lib/libmibr_carplay111.so")
    new(receiver, base + "/bin/libaltscreen111.so")
    new(cp(wp1 + "payload/libmibr_isotx2_gate.so", "gate.so"), "/mnt/app/eso/lib/libmibr_isotx2_gate.so")
    for name in ["direct-ts-remux", "owner-probe", "owner-unlock", "sha256sum", "tee"]:
        new(cp(wp1 + "payload/" + name, name), base + "/bin/" + name)
    for name in ["common.sh", "direct_ts_auto_start.sh", "direct_ts_auto_stop.sh", "direct_ts_auto_supervisor.sh", "direct_ts_auto_watchdog.sh", "direct_ts_auto_status.sh", "writev_gate.sh"]:
        new(cp(wp1 + "runtime/auto-direct/" + name, name), base + "/scripts/" + name)
    new(cp(wp1 + "runtime/auto-direct/altscreen111.conf", "altscreen111.conf"), base + "/config/altscreen111.conf", "644")
    new(cp("MU1409-autostart/boot_autostart.sh", "boot_autostart.sh"), base + "/scripts/boot_autostart.sh")
    for name in ["mibr-seat-service", "mibr-v3-genkey", "seat-storage-probe", "alt111-settings", "profile-tool"]:
        new(cp(r13 + "payload/" + name, "r13-" + name), base + "/harman-r13/bin/" + name)
    new(cp(r13 + "payload/boot.sh", "r13-boot.sh"), base + "/harman-r13/boot.sh", "644")
    new(cp(r13 + "payload/center.conf", "center.conf"), base + "/harman-r13/center.conf", "644")
    # Original R13 control.sh's restore points to the retired migration installer.
    # The fresh package supplies its own correct persistent recovery entry.
    control_input = inputs / (r13 + "payload/control.sh")
    if sha(control_input) != spec[r13 + "payload/control.sh"]:
        raise ValueError("Control input differs")
    control = control_input.read_text()
    if control.count(base + "/harman-r13/install.sh --restore") != 1:
        raise ValueError("Control recovery anchor drift")
    control = control.replace(base + "/harman-r13/install.sh --restore", "/mnt/app/root/seat-full-install-v02-backup/kit/install.sh --restore")
    (out / "payload/r13-control.sh").write_text(control)
    new("payload/r13-control.sh", base + "/harman-r13/control.sh", "644")
    new(cp("MU1409-menu-scrollbar-v0.3/payload/menu.jar", "menu.jar"), base + "/harman-r13/menu.jar", "644")
    cp("MU1409-menu-scrollbar-v0.3/payload/probe.jar", "probe.jar")
    for name in ["track.png", "thumb-red.png"]:
        new(cp("MU1409-menu-scrollbar-v0.3/payload/assets/" + name, name), base + "/harman-r13/scrollbar-assets-v03/" + name, "644")
    new(cp(r13 + "payload/gears.png", "gears.png"), "/mnt/app/eso/hmi/lsd/mibr/icons/mibr_seat_home_gears_rgba_150x150-v2.png", "644")
    new(own("config/mibr-carplay111-safearea.conf", "safearea.conf"), "/mnt/app/root/mibr-carplay111-safearea.conf", "644")
    new(own("config/mibr-seat-zoom-auto.conf", "zoom.conf"), "/mnt/app/root/mibr-seat-zoom-auto.conf", "644")
    profile = dict(line.split("=", 1) for line in (root / "config/cpvc-r5.profile").read_text().splitlines())
    tool = (root / "src/native/seat-tools/profile-tool.c").read_text()
    geometry = tool.split("geometry[]={", 1)[1].split("};", 1)[0]
    profile.update(re.findall(r'\{"([^\"]+)","([^\"]+)"\}', geometry))
    (out / "payload/cpvc-r5.profile").write_text("".join(k + "=" + v + "\n" for k, v in profile.items()))
    new("payload/cpvc-r5.profile", base + "/config/cpvc-r5.profile", "600")
    (out / "payload/enabled").write_text("1\n")
    for suffix in ["config/autostart.enabled", "config/mibr-v3-single-writer.enabled", "harman-r13/enabled"]:
        new("payload/enabled", base + "/" + suffix, "644")
    # Activation targets are last; every before-image is backed up first.
    for name in ["pf.conf", "pf.mlan0.conf"]:
        data = (baseline / name).read_text()
        anchor = "block drop in on carplay0 all"
        if data.splitlines().count(anchor) != 1 or "6031" in data:
            raise ValueError("Firewall anchor drift")
        data = data.replace(anchor, "pass in quick on carplay0 proto tcp from any to any port 6031 allow-opts\n" + anchor)
        (out / "payload" / name).write_text(data)
        expected = {"pf.conf": "c106a402f6aa39e8bbba3f16a5671e36ad6f76ad381d7e4c86d3675a2b5c19ce", "pf.mlan0.conf": "6a99ca6830b0c554a58cce8a0fb542e8ededf64dc68ce62c025d0d9805d3ebcd"}[name]
        if sha(out / "payload" / name) != expected:
            raise ValueError("Firewall candidate differs from qualified bytes")
        replace("payload/" + name, "/mnt/system/etc/" + name, name, name, "644")
    replace(cp(wp1 + "candidates/smartphone_integrator.json", "phone.json"), "/mnt/system/etc/eso/production/smartphone_integrator.json", "smartphone_integrator.json", "phone.json", "644")
    replace(cp(r13 + "payload/lsd.sh", "hmi-startup.sh"), "/mnt/app/eso/hmi/lsd/lsd.sh", "lsd.sh", "lsd.sh")
    replace(cp("MU1409-autostart/startup.sh", "system-startup.sh"), "/mnt/system/etc/boot/startup.sh", "startup.sh", "startup.sh")
    (out / "TARGETS.txt").write_text("".join(" ".join(t) + "\n" for t in targets))
    immutable = {"libairplay.so": "/mnt/app/eso/lib/libairplay.so", "dio_manager": "/mnt/app/eso/bin/apps/dio_manager", "displaymanager": "/eso/bin/apps/displaymanager", "smartphone_integrator": "/mnt/app/eso/bin/apps/smartphone_integrator", "lsd.jxe": "/ifs/lsd.jxe", "NavActiveIgnore.jar": "/mnt/app/eso/hmi/lsd/jars/NavActiveIgnore.jar"}
    (out / "IMMUTABLES.txt").write_text("".join(reference[k] + " " + v + "\n" for k, v in immutable.items()))
    shutil.copyfile(root / "deployment/full-install/consolidated.ksh", out / "install.sh"); (out / "install.sh").chmod(0o755)
    for src, dest in [("docs/CONSOLIDATED_INSTALL.md", "START-HERE.md"), ("DISCLAIMER.md", "DISCLAIMER.md"), ("LICENSE", "LICENSE"), ("THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md")]:
        shutil.copyfile(root / src, out / dest)
    shutil.copytree(root / "LICENSES", out / "LICENSES")
    with (out / "THIRD_PARTY_NOTICES.md").open("a") as f:
        f.write("\n## Local SD bundle\n\nUnlike the public source tree, this local bundle includes direct-ts-remux linked\nwith FFmpeg 6.1.5 (LGPL-2.1-or-later). Keep the supplied corresponding-source\ncompanion and LGPL license with any copy supplied to another tester. No x264\nor software transcoder is included. OEM-derived menu/startup inputs remain\nsubject to their separate rights and are not published in the public repo.\n")
    (out / "ASSEMBLY.json").write_text(json.dumps({"status": "HOST_ASSEMBLED_VEHICLE_UNTESTED", "inputs": used, "final_receiver": sha(out / receiver), "target_count": len(targets), "intermediate_receivers_installed": False}, indent=2) + "\n")
    files = sorted(p for p in out.rglob("*") if p.is_file())
    (out / "KIT.sha256").write_text("".join(sha(p) + " " + str(p.relative_to(out)) + "\n" for p in files))
    with zipfile.ZipFile(Path(str(out) + ".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file(): z.write(p, out.name + "/" + str(p.relative_to(out)))
    print("CONSOLIDATED=ASSEMBLED_LOCAL_ONLY targets=%d zip_bytes=%d vehicle_acceptance=UNTESTED" % (len(targets), Path(str(out) + ".zip").stat().st_size))


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--inputs", type=Path, required=True); a.add_argument("--baseline", type=Path, required=True)
    a.add_argument("--out", type=Path)
    args = a.parse_args(); root = Path(__file__).resolve().parents[1]
    out = (args.out or root / "build/SEAT-MU1409-final-stack-candidate-v0.2.1").resolve()
    if not out.is_relative_to(root / "build"): a.error("Generated kit must stay under build/")
    assemble(args.inputs, args.baseline, out, root)
