"""Reproduce pinned binary edits, refusing all other donor builds.
Usage: python3 apply_binary_patches.py ARTIFACT ORIGINAL_FILE OUTPUT_FILE
The delta file is reviewable; OEM/dependency binaries remain separate inputs.
"""
from pathlib import Path
from hashlib import sha256
import sys,json
p=Path(__file__).with_name('binary-patches.json')
spec=json.loads(p.read_text())[sys.argv[1]]
b=bytearray(Path(sys.argv[2]).read_bytes())
assert sha256(b).hexdigest()==spec['input_sha256'],'wrong donor binary'
for edit in spec['edits']:
 pos=edit['offset'];old=bytes.fromhex(edit['before']);new=bytes.fromhex(edit['after'])
 assert b[pos:pos+len(old)]==old
 b[pos:pos+len(old)]=new
assert sha256(b).hexdigest()==spec['output_sha256'],'output differs from verified artifact'
Path(sys.argv[3]).write_bytes(b)
print('NATIVE_PATCH=PASS artifact='+sys.argv[1])
