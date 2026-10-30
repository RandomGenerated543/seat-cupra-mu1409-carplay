import java.nio.file.*;
import jdk.internal.org.objectweb.asm.*;

/** Preserve exact target bytecode; only append fail-open calls at qualified anchors. */
public final class PatchMedia {
    static final String BRIDGE="de/mibr/media/MediaBridge";
    static final String STATION="de/vw/mib/bap/mqbab2/audiosd/functions/CurrentStationInfo";
    static final String FUNCTION="de/vw/mib/bap/mqbab2/common/api/stages/Function";
    static final String HSM="de/vw/mib/asl/internal/carplay/target/HsmTarget";
    static final String STATUS="de/vw/mib/bap/mqbab2/generated/audiosd/serializer/CurrentStationInfo_Status";
    static int hits;
    public static void main(String[] args)throws Exception{
        ClassReader r=new ClassReader(Files.readAllBytes(Path.of(args[0])));
        String cls=r.getClassName();
        ClassWriter w=new ClassWriter(r,ClassWriter.COMPUTE_MAXS);
        r.accept(new ClassVisitor(Opcodes.ASM8,w){
            public MethodVisitor visitMethod(int access,String name,String desc,String sig,String[] exceptions){
                MethodVisitor out=super.visitMethod(access,name,desc,sig,exceptions);
                String hook=null; boolean entry=false;
                if(cls.equals(HSM)&&name.equals("initializeDSI")&&desc.equals("()V"))hook="attach";
                if(cls.equals(HSM)&&name.equals("deInitializeDSI")&&desc.equals("()V")){hook="detach";entry=true;}
                if(cls.endsWith("/CarPlayGlobalProperies")&&name.equals("setConnectionState")&&desc.equals("(I)V"))hook="connection";
                if(cls.equals(STATION)&&name.equals("init")&&desc.equals("(Lde/vw/mib/bap/mqbab2/common/api/stages/BAPStageInitializer;)Lde/vw/mib/bap/datatypes/BAPEntity;"))hook="stationReady";
                if(cls.equals(STATION)&&name.equals("uninitialize")&&desc.equals("()V")){hook="stationGone";entry=true;}
                if(cls.equals(STATION)&&name.equals("setStationInfoForMirrorLink")&&desc.equals("(L"+STATUS+";)V"))hook="render";
                if(hook==null)return out;
                hits++;
                final String call=hook; final boolean atEntry=entry;
                return new MethodVisitor(Opcodes.ASM8,out){
                    void inject(){
                        Label begin=new Label(),end=new Label(),handler=new Label(),resume=new Label();
                        super.visitTryCatchBlock(begin,end,handler,"java/lang/Throwable");
                        // The init ARETURN has a value on stack. Store it so catch has the same empty stack.
                        if(call.equals("stationReady"))super.visitVarInsn(Opcodes.ASTORE,10);
                        super.visitLabel(begin);
                        if(call.equals("attach")){
                            super.visitVarInsn(Opcodes.ALOAD,0);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"(L"+HSM+";)V",false);
                        }else if(call.equals("connection")){
                            super.visitVarInsn(Opcodes.ILOAD,1);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"(I)V",false);
                        }else if(call.equals("stationReady")){
                            super.visitVarInsn(Opcodes.ALOAD,0);super.visitVarInsn(Opcodes.ALOAD,0);
                            super.visitMethodInsn(Opcodes.INVOKEVIRTUAL,FUNCTION,"getThreadSwitchingService","()Lde/vw/mib/genericevents/ThreadSwitchingTarget;",false);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"(L"+STATION+";Lde/vw/mib/genericevents/ThreadSwitchingTarget;)V",false);
                        }else if(call.equals("stationGone")){
                            super.visitVarInsn(Opcodes.ALOAD,0);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"(L"+STATION+";)V",false);
                        }else if(call.equals("render")){
                            super.visitVarInsn(Opcodes.ALOAD,1);super.visitVarInsn(Opcodes.ALOAD,0);
                            super.visitMethodInsn(Opcodes.INVOKEVIRTUAL,FUNCTION,"getSmartphoneIntegrationService","()Lde/vw/mib/bap/mqbab2/common/api/smartphoneintegration/SmartphoneIntegrationService;",false);
                            super.visitMethodInsn(Opcodes.INVOKEINTERFACE,"de/vw/mib/bap/mqbab2/common/api/smartphoneintegration/SmartphoneIntegrationService","getSmarphoneIntegrationActiveConnectionType","()I",true);
                            super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"(L"+STATUS+";I)V",false);
                        }else super.visitMethodInsn(Opcodes.INVOKESTATIC,BRIDGE,call,"()V",false);
                        super.visitLabel(end);super.visitJumpInsn(Opcodes.GOTO,resume);
                        super.visitLabel(handler);super.visitInsn(Opcodes.POP);super.visitLabel(resume);
                        if(call.equals("stationReady"))super.visitVarInsn(Opcodes.ALOAD,10);
                    }
                    public void visitCode(){super.visitCode();if(atEntry)inject();}
                    public void visitInsn(int opcode){
                        if(!atEntry&&(opcode==Opcodes.RETURN||opcode==Opcodes.ARETURN))inject();
                        super.visitInsn(opcode);
                    }
                };
            }
        },0);
        int expected=cls.equals(STATION)?3:cls.equals(HSM)?2:1;
        if(hits!=expected)throw new IllegalStateException("anchor_count="+hits+" expected="+expected);
        Files.write(Path.of(args[1]),w.toByteArray());
        System.out.println(cls+" patched_methods="+hits);
    }
}
