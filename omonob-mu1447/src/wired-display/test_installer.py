"""Host fixtures of installer transactions; QNX loader check is mocked separately."""
from pathlib import Path
import tempfile,subprocess,shutil,os
kit=Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='mu1447-wired-fixture-') as td:
    t=Path(td);u=t/'unit';u.mkdir();k=t/'kit';shutil.copytree(kit,k)
    mock=t/'bin';mock.mkdir();(mock/'mount').write_text('#!/bin/sh\nexit 0\n');(mock/'mount').chmod(0o755)
    check=k/'payload/file-check';check.write_text('#!/bin/sh\ncase "$1" in --same) cmp -s "$2" "$3";; --load) [ "${MOCK_LOAD_FAIL:-0}" = 0 ];; *) exit 2;; esac\n');check.chmod(0o755)
    s=(kit/'install.sh').read_text()
    for prefix in ['/mnt/','/ifs/','/ramdisk/','/dev/']:s=s.replace(prefix,str(u)+prefix)
    (k/'install.sh').write_text(s)
    root=u/'mnt/app/carplaymaps';root.mkdir(parents=True)
    dio=u/'mnt/app/eso/bin/apps/dio_manager';dio.parent.mkdir(parents=True)
    for path in ['ifs','ramdisk','dev/shmem']:(u/path).mkdir(parents=True)
    with (u/'ifs/lsd.jxe').open('wb') as f:f.truncate(55712574)
    (root/'PROFILE').write_text('MU1447/790\n')
    stock=root/'stock_first/dio_manager.real';stock.parent.mkdir();stock.write_bytes(b'original vehicle executable');stock.chmod(0o755)
    core=root/'core.so';wrapper=root/'dio_manager.wrapper.sh';addon=root/'libmu1447-wired-display.so'
    origcore=(kit/'payload/core-original.so').read_bytes();newcore=(kit/'payload/core-display.so').read_bytes()
    origwrapper=(kit/'payload/wrapper-original.sh').read_bytes();newwrapper=(kit/'payload/wrapper-display.sh').read_bytes()
    core.write_bytes(origcore);wrapper.write_bytes(origwrapper);dio.write_bytes(origwrapper)
    backup=u/'mnt/app/.mu1447-wired-display-v011'
    env=dict(os.environ,PATH=str(mock)+':'+os.environ['PATH'])
    def run(action,success=True):
        r=subprocess.run(['/bin/sh',str(k/'install.sh'),action],env=env,text=True,capture_output=True)
        assert (r.returncode==0)==success,(action,r.stdout,r.stderr)
        return r.stdout
    def persistent():return {str(p.relative_to(u)):p.read_bytes() for p in (u/'mnt').rglob('*') if p.is_file()}
    before=persistent();assert 'CHECK=PASS' in run('--check');assert persistent()==before
    env['MOCK_LOAD_FAIL']='1';run('--apply',False);assert persistent()==before;env.pop('MOCK_LOAD_FAIL')
    run('--apply');assert core.read_bytes()==newcore and wrapper.read_bytes()==dio.read_bytes()==newwrapper and addon.is_file()
    baseline={p.name:p.read_bytes() for p in backup.iterdir() if p.is_file()}
    run('--apply');assert baseline=={p.name:p.read_bytes() for p in backup.iterdir() if p.is_file()}
    run('--restore');assert core.read_bytes()==origcore and wrapper.read_bytes()==dio.read_bytes()==origwrapper and not addon.exists()
    run('--restore');assert core.read_bytes()==origcore
    live={key:val for key,val in persistent().items() if '/.mu1447-wired-display-v011/' not in key}
    assert live==before
    run('--apply');wrapper.write_bytes(origwrapper)
    assert 'PARTIAL_RESTORE_REQUIRED' in run('--status');run('--apply',False);run('--restore')
    core.write_bytes(b'unknown');run('--apply',False);assert core.read_bytes()==b'unknown';core.write_bytes(origcore)
    (u/'ramdisk/mu1447-wired-display.lock').write_text('other');run('--apply',False)
    assert (u/'ramdisk/mu1447-wired-display.lock').read_text()=='other';(u/'ramdisk/mu1447-wired-display.lock').unlink()
    (u/'dev/ipod0').write_text('connected');run('--apply',False);(u/'dev/ipod0').unlink()
    (backup/'core.so').write_bytes(b'corrupt');run('--restore',False)
    assert core.read_bytes()==origcore
print('INSTALLER_FIXTURES=PASS no_persistent_check_writes failed_load_no_writes exact_backup repeated_apply exact_restore partial_install_recovery unknown_receiver lock live_session corrupt_backup')
