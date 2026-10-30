"""Generate the owner-only deployment from separately held exact target inputs."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build import HERE,ROOT,sha

BASELINE_SHA='d2c82cdf956eb729cd915b46f27768e17f122a2cf98ead10958c96af6564908a'
JXE_SHA='25b9f1285445de0193c1d869a734230d7db95363957603598a6ede09af904403'
def main():
    baseline=ROOT/'work/seat-public-handoff/repo/build/SEAT-MU1409-final-stack-candidate-v0.2.1/payload/hmi-startup.sh'
    assert sha(baseline)==BASELINE_SHA,'Unknown target startup; do not expand the allowlist without comparison'
    package=HERE/'package';payload=package/'payload'
    before=baseline.read_bytes()
    assert before.count(b'-Xbootclasspath/p:')==2
    after=before.replace(b'-Xbootclasspath/p:',b'-Xbootclasspath/p:/mnt/app/root/altscreen-u2/seat-media/seat-media.jar:')
    (payload/'startup-before.sh').write_bytes(before)
    (payload/'startup-after.sh').write_bytes(after)
    (package/'hashes.sh').write_text('MEDIA_JAR_SHA='+sha(payload/'seat-media.jar')+'\nSTARTUP_BEFORE_SHA='+BASELINE_SHA+'\nSTARTUP_AFTER_SHA='+hashlib.sha256(after).hexdigest()+'\nOEM_JXE_SHA='+JXE_SHA+'\n')
    for name in ['BUILD.json','INSTALLER-TESTS.json']:
        shutil.copyfile(HERE/name,package/name)
    public=ROOT/'work/seat-public-handoff/repo'
    for name in ['LICENSE','DISCLAIMER.md']:
        shutil.copyfile(public/name,package/name)
    out=HERE/'MU1409-media-info-v0.1'
    if out.exists():shutil.rmtree(out)
    shutil.copytree(package,out)
    manifest={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
    (out/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=HERE/'MU1409-media-info-v0.1.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,str(p.relative_to(HERE)))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('PACKAGE='+str(archive)+' bytes='+str(archive.stat().st_size)+' sha256='+sha(archive))
if __name__=='__main__':main()
