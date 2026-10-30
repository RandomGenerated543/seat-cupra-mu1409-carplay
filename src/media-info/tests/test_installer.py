from pathlib import Path
import tempfile,shutil,hashlib,subprocess,os,json
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'package'
OUT=ROOT/'installer-tests'
OUT.mkdir(exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fixture(root):
    package=root/'kit';shutil.copytree(PACKAGE,package)
    app=root/'app';base=app/'root/altscreen-u2';(base/'bin').mkdir(parents=True)
    target=app/'eso/hmi/lsd/lsd.sh';target.parent.mkdir(parents=True)
    target.write_bytes((package/'payload/startup-before.sh').read_bytes())
    jxe=root/'lsd.jxe';jxe.write_bytes(b'fixture_jxe')
    hashes=package/'hashes.sh';hashes.write_text(hashes.read_text().replace('25b9f1285445de0193c1d869a734230d7db95363957603598a6ede09af904403',digest(jxe)))
    helper=base/'bin/sha256sum';helper.write_text('#!/bin/sh\nexec /usr/bin/shasum -a 256 "$@"\n');helper.chmod(0o755)
    bin=root/'bin';bin.mkdir()
    for name,body in {
        'j9':'exit ${J9_FAIL:-0}',
        'mount':'echo "$*" >> "$MOUNT_LOG"; if [ "$1" = -ur ] && [ "${RO_FAIL:-0}" = 1 ];then exit 1;fi;exit 0',
        'cp':'case "$2" in *"${COPY_FAIL:-NO_FAILURE}"*) echo partial > "$2";exit 1;;esac;exec /bin/cp "$@"',
    }.items():
        p=bin/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)
    script=package/'install.sh';script.write_text(script.read_text().replace('/mnt/app',str(app)).replace('/ifs/lsd.jxe',str(jxe)).replace('/ifs/jre/bin/j9',str(bin/'j9')))
    env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],MOUNT_LOG=str(root/'mount.log'))
    return package,target,base,env
def run(p,mode,env):
    return subprocess.run(['/bin/ksh',str(p/'install.sh'),mode],env=env,capture_output=True,text=True,timeout=30)
results=[]
for case in ['readonly_check','tamper_rejected','unknown_startup','j9_rejected','apply_idempotent_restore','partial_jar','partial_startup','readonly_mount_failure']:
    with tempfile.TemporaryDirectory(dir=OUT,prefix=case) as directory:
        root=Path(directory);kit,target,base,env=fixture(root);original=target.read_bytes()
        if case=='readonly_check':
            p=run(kit,'--check',env);assert p.returncode==0,p.stdout+p.stderr
            assert not (root/'mount.log').exists() and target.read_bytes()==original
        elif case=='tamper_rejected':
            (kit/'payload/seat-media.jar').write_bytes(b'bad')
            p=run(kit,'--apply',env);assert p.returncode!=0 and not (root/'mount.log').exists()
        elif case=='unknown_startup':
            target.write_bytes(b'other');p=run(kit,'--apply',env)
            assert p.returncode!=0 and target.read_bytes()==b'other' and not (root/'mount.log').exists()
        elif case=='j9_rejected':
            p=run(kit,'--apply',dict(env,J9_FAIL='9'));assert p.returncode!=0 and target.read_bytes()==original
            assert not (root/'mount.log').exists()
        elif case=='apply_idempotent_restore':
            p=run(kit,'--apply',env);assert p.returncode==0,p.stdout+p.stderr
            assert target.read_bytes()==(kit/'payload/startup-after.sh').read_bytes()
            assert digest(base/'seat-media/seat-media.jar')==digest(kit/'payload/seat-media.jar')
            p=run(kit,'--apply',env);assert p.returncode==0 and 'ALREADY_SELECTED' in p.stdout
            p=run(kit,'--restore-check',env);assert p.returncode==0
            p=run(kit,'--restore',env);assert p.returncode==0 and target.read_bytes()==original,p.stdout+p.stderr
        elif case in ['partial_jar','partial_startup']:
            match='seat-media.jar.new' if case=='partial_jar' else 'lsd.sh.media-new'
            p=run(kit,'--apply',dict(env,COPY_FAIL=match));assert p.returncode!=0 and target.read_bytes()==original
            assert '-ur ' in (root/'mount.log').read_text()
            p=run(kit,'--restore',env);assert p.returncode==0 and target.read_bytes()==original
        else:
            p=run(kit,'--apply',dict(env,RO_FAIL='1'));assert p.returncode==35,p.stdout+p.stderr
            p=run(kit,'--restore',env);assert p.returncode==0 and target.read_bytes()==original
        results.append({'case':case,'passed':True})
(ROOT/'INSTALLER-TESTS.json').write_text(json.dumps({'scope':'Host fixtures; QNX native J9 and visible result untested','cases':results},indent=2)+'\n')
print('MEDIA_INSTALLER_TEST=PASS cases='+str(len(results)))
