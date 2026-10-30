#!/usr/bin/env python3
"""Exercise the real fresh-installer script against isolated host filesystem mocks.

Mount, J9, PF and process probes are mocked, so this is not target qualification.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def fixture(d, inject=False):
    kit = d / "kit"; (kit / "payload").mkdir(parents=True)
    bin_dir = d / "bin"; bin_dir.mkdir()
    def script(p, text):
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text("#!/bin/bash\n" + text); p.chmod(0o755)
    for name in ["mount", "pidin"]:
        script(bin_dir / name, "exit 0\n")
    script(d / "armle/sbin/pfctl", "exit 0\n")
    script(d / "ifs/jre/bin/j9", "echo TARGET_J9_MOCK=PASS\n")
    script(kit / "payload/owner-probe", "exit 0\n")
    helper = kit / "payload/sha256sum"
    helper.write_text("#!/usr/bin/env python3\nimport hashlib,sys\nprint(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())\n"); helper.chmod(0o755)
    for name in ["menu.jar", "probe.jar", "pf.conf", "pf.mlan0.conf"]:
        (kit / "payload" / name).write_text("fixture\n")
    paths = ["/mnt/system/etc/pf.conf", "/mnt/system/etc/pf.mlan0.conf", "/mnt/system/etc/eso/production/smartphone_integrator.json", "/mnt/app/eso/hmi/lsd/lsd.sh", "/mnt/system/etc/boot/startup.sh"]
    rows = []; originals = {}
    for i, path in enumerate(paths):
        p = d / path.lstrip("/"); p.parent.mkdir(parents=True, exist_ok=True); p.write_text("original-%d\n" % i)
        originals[p] = p.read_bytes()
        src = kit / "payload" / ("activation%d" % i); src.write_text("final-%d\n" % i)
        rows.append("replace id%d payload/activation%d %s %s %s 755" % (i, i, p, sha(p), sha(src)))
    immutable = d / "mnt/app/eso/lib/libairplay.so"; immutable.parent.mkdir(parents=True, exist_ok=True); immutable.write_text("native-baseline")
    (kit / "IMMUTABLES.txt").write_text(sha(immutable) + " " + str(immutable) + "\n")
    data = kit / "payload/profile"; data.write_text("initial-preferences\n")
    target = d / "mnt/app/root/altscreen-u2/config/cpvc-r5.profile"
    rows.insert(0, "new n1 payload/profile %s absent %s 600" % (target, sha(data)))
    (kit / "TARGETS.txt").write_text("\n".join(rows) + "\n")
    code = (ROOT / "deployment/full-install/consolidated.ksh").read_text()
    for prefix in ["/mnt/app", "/mnt/system", "/tmp/mibr-", "/armle", "/ifs"]:
        code = code.replace(prefix, str(d) + prefix)
    # Runtime /etc aliases are the same filesystem on the real target. In this
    # host fixture point the alias verification back at the mock persistent file.
    code = code.replace('verify "${TARGET#' + str(d) + '/mnt/system}" "$CURRENT"', 'verify "$TARGET" "$CURRENT"')
    code = code.replace("/bin/ksh", "/bin/bash")
    code = code.replace("95d1e6e9611905d9f91f020d34b1bcd1236085c2862dee3faf0a91e790d37f3c", sha(helper))
    script(kit / "install.sh", code)
    (kit / "KIT.sha256").write_text("".join(sha(p) + " " + str(p.relative_to(kit)) + "\n" for p in kit.rglob("*") if p.is_file()))
    if inject:
        dest = d / "mnt/app/eso/hmi/lsd/lsd.sh"
        script(bin_dir / "mv", 'if [ "$1" = "' + str(dest) + '.full-new" ] && [ ! -e "' + str(d / "fault-fired") + '" ];then touch "' + str(d / "fault-fired") + '";exit 1;fi\nexec /bin/mv "$@"\n')
    env = dict(os.environ, PATH=str(bin_dir) + ":" + os.environ["PATH"])
    def run(mode):
        return subprocess.run(["/bin/bash", str(kit / "install.sh"), mode], env=env, capture_output=True, text=True)
    return run, originals, immutable, target, kit


def main():
    with tempfile.TemporaryDirectory() as t:
        run, originals, immutable, profile, kit = fixture(Path(t))
        before = {p: p.read_bytes() for p in originals}
        anchor = Path(t) / "mnt/app/root/altscreen-u2/wp2"
        assert not anchor.exists()
        r = run("--check"); assert r.returncode == 0, r.stdout + r.stderr
        assert not anchor.exists(), "Read-only preflight created storage anchor"
        assert all(p.read_bytes() == data for p, data in before.items())
        assert not profile.exists() and not (Path(t) / "mnt/app/root/seat-full-install-v02-backup").exists()
        immutable.write_text("wrong-target")
        r = run("--apply"); assert r.returncode == 20 and "unexpected_bytes=" in r.stdout
        assert all(p.read_bytes() == data for p, data in before.items())
        immutable.write_text("native-baseline")
        r = run("--apply"); assert r.returncode == 0, r.stdout + r.stderr
        assert anchor.is_dir() and not anchor.is_symlink(), "Fresh install omitted storage probe anchor"
        assert not (anchor / "enabled").exists(), "Retired WP2 service enabled"
        assert all(p.read_bytes() != data for p, data in originals.items())
        r = run("--apply"); assert r.returncode == 0, r.stdout + r.stderr
        profile.write_text("user-edited-preferences\n")
        r = run("--restore-check"); assert r.returncode == 0, r.stdout + r.stderr
        r = run("--restore"); assert r.returncode == 0, r.stdout + r.stderr
        assert all(p.read_bytes() == data for p, data in originals.items())
        assert profile.read_text() == "user-edited-preferences\n"
        persistent = Path(t) / "mnt/app/root/seat-full-install-v02-backup/kit/install.sh"
        assert persistent.is_file(), "Missing persistent restore route"
        kit.rename(Path(t) / "removed-sd-kit")
        env = dict(os.environ, PATH=str(Path(t) / "bin") + ":" + os.environ["PATH"])
        r = subprocess.run(["/bin/bash", str(persistent), "--restore-check"], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        backup = Path(t) / "mnt/app/root/seat-full-install-v02-backup/original/id0"
        backup.write_text("corrupted-backup")
        r = subprocess.run(["/bin/bash", str(persistent), "--restore"], env=env, capture_output=True, text=True)
        assert r.returncode == 20 and "unexpected_bytes=" in r.stdout
        assert all(p.read_bytes() == data for p, data in originals.items())
    with tempfile.TemporaryDirectory() as t:
        run, originals, immutable, profile, kit = fixture(Path(t), inject=True)
        r = run("--apply")
        assert r.returncode != 0 and "ACTIVATION_FILES_ROLLED_BACK" in r.stdout, r.stdout + r.stderr
        assert all(p.read_bytes() == data for p, data in originals.items())
        r = run("--restore-check"); assert r.returncode == 0, r.stdout + r.stderr
    for symlink in [False, True]:
        with tempfile.TemporaryDirectory() as t:
            run, originals, immutable, profile, kit = fixture(Path(t))
            r = run("--apply"); assert r.returncode == 0, r.stdout + r.stderr
            before = {p: p.read_bytes() for p in originals}
            anchor = Path(t) / "mnt/app/root/altscreen-u2/wp2"
            anchor.rmdir()
            if symlink:
                anchor.symlink_to(Path(t) / "foreign-storage")
            else:
                anchor.write_text("foreign file")
            r = run("--apply")
            assert r.returncode == 20 and "storage_anchor_" in r.stdout, r.stdout + r.stderr
            assert all(p.read_bytes() == data for p, data in before.items())
    print("CONSOLIDATED_HOST=PASS readonly_preflight target_mismatch apply repeat user_preferences restore persistent_recovery activation_failure_rollback vehicle_probes_mocked=1")


if __name__ == "__main__": main()
