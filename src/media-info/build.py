from pathlib import Path
import hashlib,json,subprocess,zipfile,struct,os
HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get('MU1409_WORKSPACE',str(HERE.parents[1]))).resolve()
JAVA=ROOT/'tools-cache/jdk/jdk-21.0.13+9/Contents/Home/bin/java'
JAVAC=JAVA.with_name('javac')
API=ROOT/'build/wp2-seat-candidate-work/seat-api-compile-only.jar'
STOCK=ROOT/'private/java/P4708-MU1409-run01/lsd.jar'
EXPORT='java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED'
def run(args,log):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
    (HERE/log).write_text(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError(log+'\n'+p.stdout+p.stderr)
    return p.stdout
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def methods(b,parts=False):
    # Compare raw Code attributes of all untouched methods, without decompilation.
    p=10;cp={};n=struct.unpack_from('>H',b,8)[0];i=1
    def u2():
        nonlocal p
        x=struct.unpack_from('>H',b,p)[0];p+=2;return x
    while i<n:
        tag=b[p];p+=1
        if tag==1:
            length=u2();cp[i]=b[p:p+length].decode('utf8',errors='replace');p+=length
        elif tag in (3,4,9,10,11,12,18):p+=4
        elif tag in (5,6):p+=8;i+=1
        elif tag in (7,8,16):p+=2
        elif tag==15:p+=3
        else:raise ValueError(tag)
        i+=1
    p+=6;interfaces=u2();p+=2*interfaces
    def attrs():
        nonlocal p
        result={}
        for _ in range(u2()):
            name=cp[u2()];length=struct.unpack_from('>I',b,p)[0];p+=4
            result[name]=b[p:p+length];p+=length
        return result
    for _ in range(u2()):p+=6;attrs()
    out={};raw={};start=p;count=u2()
    for _ in range(count):
        begin=p
        access=u2();name=cp[u2()];desc=cp[u2()];out[(name,desc)]=attrs().get('Code')
        raw[(name,desc)]=b[begin:p]
    return (b[:start],raw,b[p:]) if parts else out
def main():
    for name in ['classes','test-classes','host/classes','package/payload']:(HERE/name).mkdir(parents=True,exist_ok=True)
    src=sorted((HERE/'src').rglob('*.java'))
    run([JAVA,'-jar',ROOT/'tools-cache/ecj-3.26.0.jar','-source','1.3','-target','1.2','-warn:none','-bootclasspath',API,'-classpath',API,'-d',HERE/'classes',*src],'COMPILE.log')
    run([JAVAC,'-d',HERE/'test-classes',HERE/'src/de/mibr/media/MediaState.java',HERE/'tests/MediaStateTest.java'],'TEST-COMPILE.log')
    print(run([JAVA,'-ea','-cp',HERE/'test-classes','MediaStateTest'],'TEST.log'))
    run([JAVAC,'--add-exports',EXPORT,'-d',HERE/'host/classes',HERE/'host/PatchMedia.java'],'PATCH-COMPILE.log')
    anchors={
        'de/vw/mib/asl/internal/carplay/target/HsmTarget.class':{'initializeDSI','deInitializeDSI'},
        'de/vw/mib/asl/internal/carplay/common/CarPlayGlobalProperies.class':{'setConnectionState'},
        'de/vw/mib/bap/mqbab2/audiosd/functions/CurrentStationInfo.class':{'init','uninitialize','setStationInfoForMirrorLink'}}
    entries={};evidence=[]
    with zipfile.ZipFile(STOCK) as z:
        for index,(name,changed) in enumerate(anchors.items()):
            original=z.read(name);before=HERE/('host/before-'+str(index)+'.class');after=HERE/('host/after-'+str(index)+'.class')
            before.write_bytes(original)
            run([JAVA,'--add-exports',EXPORT,'-cp',HERE/'host/classes','PatchMedia',before,after],'PATCH-'+str(index)+'.log')
            candidate=after.read_bytes()
            # ASM deduplicates existing CP references in untouched methods. Keep the
            # original method_info bytes instead: original CP entries remain intact.
            prefix,newparts,suffix=methods(candidate,True)
            _,oldparts,_=methods(original,True)
            candidate=prefix+struct.pack('>H',len(newparts))+b''.join(
                value if key[0] in changed else oldparts[key] for key,value in newparts.items())+suffix
            candidate=candidate[:6]+struct.pack('>H',46)+candidate[8:]
            after.write_bytes(candidate)
            old=methods(original);new=methods(candidate)
            assert old.keys()==new.keys()
            actual={key[0] for key in old if old[key]!=new[key]}
            assert actual==changed,(name,actual,changed)
            entries[name]=candidate
            evidence.append({'class':name,'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':hashlib.sha256(candidate).hexdigest(),'changed_methods':sorted(changed),'untouched_methods_byte_identical':len(old)-len(changed)})
    for p in sorted((HERE/'classes').rglob('*.class')):entries[str(p.relative_to(HERE/'classes'))]=p.read_bytes()
    out=HERE/'package/payload/seat-media.jar'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(entries.items()):
            assert int.from_bytes(b[6:8],'big')==46,(n,int.from_bytes(b[6:8],'big'))
            info=zipfile.ZipInfo(n,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    cp=str(out)+':'+str(STOCK)
    run([JAVA,'-Xverify:all','-cp',cp,'de.mibr.media.MediaProbe'],'HOST-VERIFY.log')
    run([JAVAC,'-cp',cp,'-d',HERE/'test-classes',HERE/'tests/MediaBridgeTest.java'],'BRIDGE-TEST-COMPILE.log')
    print(run([JAVA,'-Xverify:all','-cp',str(HERE/'test-classes')+':'+cp,'MediaBridgeTest'],'BRIDGE-TEST.log'))
    manifest={'status':'HOST_BUILT_VEHICLE_UNTESTED','reference_commit':'f1ac169d1ce40b291d9a2ab6a0d97fe53474754f','target':'MHI2_ER_SEG11_P4708_1 MU1409 EU','scope':'AudioSD song title/artist/album only','class_format':46,'jar_sha256':sha(out),'stock_jar_sha256':sha(STOCK),'patched':evidence,'source':'Target-specific original-bytecode hooks; reference architectural comparison only','excluded':['artwork','playback timer','shuffle','telephony','navigation import'],'startup':'Separate priority jar; existing menu and native receiver unchanged'}
    (HERE/'BUILD.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
