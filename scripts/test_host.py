#!/usr/bin/env python3
import os,pathlib,subprocess,tempfile,shutil
r=pathlib.Path(__file__).resolve().parents[1]
cc=os.environ.get("CC","cc")
with tempfile.TemporaryDirectory() as tmp:
    tmp=pathlib.Path(tmp);n=r/"src/native/altscreen111-gen2"
    for test,source in [("receiver_queue_test","alt111_video"),("receiver_view_test","alt111_control")]:
        out=tmp/test
        subprocess.run([cc,"-std=c99","-Wall","-Wextra","-Werror","-I"+str(n/"include"),str(r/"tests"/(test+".c")),str(n/"src"/(source+".c")),"-o",str(out)],check=True)
        subprocess.run([str(out)],check=True)
subprocess.run([os.environ.get("PYTHON","python3"),str(r/"tests/menu_indicator_host.py")],check=True)
subprocess.run([os.environ.get("PYTHON","python3"),str(r/"tests/consolidated_install_test.py")],check=True)
print("HOST_CHECKS=PASS vehicle_execution_not_established")
