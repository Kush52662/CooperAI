#!/usr/bin/env python3
"""Build runtime and demo ZIPs from explicit allowlists; exclude reviewer ground truth."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/acord-form-filler'
DIST=ROOT/'dist'
DIST.mkdir(exist_ok=True)
files=[SKILL/'SKILL.md',SKILL/'requirements.txt']
for folder in ['scripts','references','assets']:
 files.extend(p for p in (SKILL/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
with ZipFile(DIST/'acord-form-filler.zip','w',ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,Path('acord-form-filler')/p.relative_to(SKILL))
with ZipFile(DIST/'demo-inputs.zip','w',ZIP_DEFLATED) as z:
 for case in sorted((ROOT/'sample input data').glob('[0-9][0-9]_*')):
  for name in ['ams360_customer_policy_export.csv','insurance_document.pdf','submission_request.json']:
   p=case/name;z.write(p,Path(case.name)/name)
for filename in ['acord-form-filler.zip','demo-inputs.zip']:
 with ZipFile(DIST/filename) as z:
  assert z.testzip() is None
  assert all('_evaluation' not in n and 'expected_results' not in n and '__pycache__' not in n for n in z.namelist())
print(json.dumps({p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in DIST.glob('*.zip')},indent=2))
