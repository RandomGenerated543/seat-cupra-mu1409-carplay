#!/usr/bin/env python3
# Local OEM inputs and generated artifacts must not be published.
import os,pathlib,subprocess,zipfile,shutil
r=pathlib.Path(__file__).resolve().parents[1]
required=["JAVA","ECJ_JAR","SEAT_API_JAR","OEM_HOOKS_DIR"]
missing=[n for n in required if not os.environ.get(n)]
if missing:raise SystemExit("Required local build inputs: "+", ".join(missing))
out=pathlib.Path(os.environ.get("OUT",str(r/"build/menu"))).resolve()
out.mkdir(parents=True,exist_ok=True);classes=out/"classes";classes.mkdir(exist_ok=True)
hooks=pathlib.Path(os.environ["OEM_HOOKS_DIR"])
sources=sorted((r/"src/menu/java").rglob("*.java"))
for rel in ["de/vw/mib/cio/internal/Activator.java","generated/de/vw/mib/global/view/internal/WidgetFactoryImpl.java"]:
    f=hooks/rel
    if not f.is_file():raise SystemExit("Missing locally supplied, target-bound OEM hook: "+str(f))
    sources.append(f)
cmd=[os.environ["JAVA"],"-jar",os.environ["ECJ_JAR"],"-source","1.3","-target","1.2","-encoding","UTF-8","-warn:none","-bootclasspath",os.environ["SEAT_API_JAR"],"-classpath",os.environ["SEAT_API_JAR"],"-d",str(classes)]+[str(f) for f in sources]
subprocess.run(cmd,check=True)
files=sorted(classes.rglob("*.class"))
for f in files:
    if int.from_bytes(f.read_bytes()[6:8],"big")!=46:raise SystemExit("Wrong class version: "+str(f))
jar=out/"LOCAL-ONLY-menu.jar"
with zipfile.ZipFile(jar,"w",zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,str(f.relative_to(classes)))
print("MENU_BUILD=PASS class_format=46 local_only=1 "+str(jar))
