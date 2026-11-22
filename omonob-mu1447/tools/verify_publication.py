"""Read-only verification of the published MU1447 source/artifact handoff."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from zipfile import ZipFile
import json,re,sys
root=Path(__file__).resolve().parents[1]
h=lambda b:sha256(b).hexdigest()
records=json.loads((root/'downloads/PACKAGES.json').read_text());assert len(records)==8
private=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----\s+[A-Za-z0-9+/=\r\n]{64,}-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')
blocked={'id_rsa','id_ed25519','mqb_car','known_hosts','wpa_supplicant.conf','pk.txt','sk.txt','pairings.json','.DS_Store'}
manifest=(root/'downloads/SHA256SUMS.txt').read_text().splitlines();assert len(manifest)==8
for item in records:
 p=root/'downloads'/item['file'];assert p.stat().st_size==item['bytes'];assert h(p.read_bytes())==item['sha256'],p.name
 assert item['sha256']+'  '+item['file'] in manifest
 with ZipFile(p) as z:
  assert z.testzip() is None
  prefix=item['name']+'/'
  entries=z.namelist();assert all(n.startswith(prefix) and '..' not in PurePosixPath(n).parts for n in entries)
  for n in entries:
   assert PurePosixPath(n).name not in blocked,n
   if not n.endswith('/'):assert not private.search(z.read(n)),n
  for line in z.read(prefix+'SHA256SUMS.txt').decode().splitlines():
   assert line[64:66]=='  ';assert h(z.read(prefix+line[66:]))==line[:64],(p.name,line[66:])
for p in root.rglob('*'):
 if not p.is_file():continue
 assert p.name not in blocked,p
 assert not private.search(p.read_bytes()),p
for p in [root/'README.md',root/'downloads/README.md',*(root/'docs').glob('*.md')]:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('https://','http://','#')):continue
  assert (p.parent/target.split('#')[0]).exists(),(p,target)
assert all((root/'src'/name).is_dir() for name in ['wired-display','wired-layout','wireless-base','wireless-network','wireless-layout','wireless-runtime','wireless-startup'])
print('PUBLICATION_VERIFY=PASS packages=8 exact_archives=1 internal_manifests=PASS private_key_and_filename_scan=PASS guide_links=PASS')
print('No car contacted and no native payload executed.')
