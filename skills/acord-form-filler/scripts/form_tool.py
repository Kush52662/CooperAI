#!/usr/bin/env python3
"""Deterministic PDF tools. No model calls, case answers, or automatic source precedence."""
import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'assets/acord_125.pdf'


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def inherited(obj, key, default=None):
    seen = set()
    while obj is not None:
        obj = obj.get_object()
        if id(obj) in seen:
            break
        seen.add(id(obj))
        if key in obj:
            return obj[key]
        obj = obj.get('/Parent')
    return default


def field_name(obj):
    parts = []
    while obj is not None:
        obj = obj.get_object()
        if obj.get('/T') is not None:
            parts.append(str(obj['/T']))
        obj = obj.get('/Parent')
    return '.'.join(reversed(parts))


def inventory(path=TEMPLATE):
    reader = PdfReader(path)
    if reader.is_encrypted and not reader.decrypt(''):
        raise ValueError('Password-protected PDFs are outside this MVP.')
    widgets = {}
    for page_index, page in enumerate(reader.pages, 1):
        for ref in page.get('/Annots', []):
            obj = ref.get_object()
            if obj.get('/Subtype') != '/Widget':
                continue
            widgets.setdefault(field_name(obj), []).append((page_index, obj))
    result = {}
    for name, field in (reader.get_fields() or {}).items():
        if field.get('/FT') not in ('/Tx', '/Btn'):
            continue
        linked = widgets.get(name, [])
        if not linked:
            raise ValueError(f'Field has no page widget: {name}')
        obj = linked[0][1]
        result[name] = {
            'type': str(field['/FT']), 'label': str(field.get('/TU', '')),
            'max_length': inherited(obj, '/MaxLen'),
            'flags': int(inherited(obj, '/Ff', 0)),
            'states': [str(s) for s in field.get('/_States_', [])],
            'widgets': [{'page': p, 'rect': [float(x) for x in o['/Rect']]} for p, o in linked],
        }
    return reader, result


def render(pdf, folder):
    import pypdfium2 as pdfium
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(pdf))
    try:
        doc.init_forms()
        for index in range(len(doc)):
            page = doc[index]
            bitmap = page.render(scale=1.5, may_draw_forms=True)
            bitmap.to_pil().save(folder / f'page-{index + 1}.png')
            bitmap.close()
            page.close()
    finally:
        doc.close()


def prepare(input_dir, run_dir):
    input_dir, run_dir = Path(input_dir).resolve(), Path(run_dir).resolve()
    names = ['ams360_customer_policy_export.csv', 'insurance_document.pdf', 'submission_request.json']
    paths = [input_dir / n for n in names]
    if not all(p.is_file() for p in paths):
        raise ValueError('Provide exactly the CSV, insurance PDF, and submission request described in the skill.')
    with paths[0].open(encoding='utf-8-sig', newline='') as handle:
        table = csv.DictReader(handle)
        rows = list(table)
        if len(rows) != 1 or len(set(table.fieldnames or [])) != len(table.fieldnames or []) or any(k is None or v is None for row in rows for k, v in row.items()):
            raise ValueError('CSV must contain unique headers and exactly one well-formed account row.')
    request = read(paths[2])
    if request.get('output_form') != 'ACORD 125 (2016/03)':
        raise ValueError('Only ACORD 125 (2016/03) is supported.')
    start = datetime.strptime(request['proposed_effective_date'], '%m/%d/%Y')
    end = datetime.strptime(request['proposed_expiration_date'], '%m/%d/%Y')
    if end <= start:
        raise ValueError('Requested expiration must follow effective date.')
    if not isinstance(request.get('requested_lines_of_business'), list) or not request['requested_lines_of_business']:
        raise ValueError('Supply requested lines of business.')
    source = PdfReader(paths[1])
    if source.is_encrypted or any(not (p.extract_text() or '').strip() for p in source.pages):
        raise ValueError('Encrypted or scan-only pages need an out-of-scope ingestion path.')
    run_dir.mkdir(parents=True, exist_ok=False)
    sources = [{'file': p.name, 'path': str(p), 'sha256': digest(p)} for p in paths]
    manifest = {'started_at': now(), 'template_sha256': digest(TEMPLATE), 'sources': sources, 'request': request}
    save(run_dir / 'manifest.json', manifest)
    (run_dir / 'source-text.txt').write_text('\n\n'.join(f'PAGE {i+1}\n{p.extract_text()}' for i, p in enumerate(source.pages)))
    render(paths[1], run_dir / 'source-pages')
    _, fields = inventory()
    save(run_dir / 'fields.json', fields)
    save(run_dir / 'packet.json', {'schema_version': '1.0', 'template_sha256': digest(TEMPLATE),
         'sources': [{'file': p['file'], 'sha256': p['sha256']} for p in sources],
         'revision': 1, 'assignments': [], 'issues': [], 'history': []})
    return {'run_dir': str(run_dir), 'fields': len(fields), 'source_pages': len(source.pages),
            'next': 'Read raw inputs, source-pages, and source-text; author packet.json using skill guidance.'}


def validate(packet, run_dir):
    run_dir = Path(run_dir)
    schema = read(ROOT / 'references/packet.schema.json')
    errors = [f'{".".join(map(str, e.path))}: {e.message}' for e in Draft202012Validator(schema).iter_errors(packet)]
    if errors:
        return errors
    manifest = read(run_dir / 'manifest.json')
    _, fields = inventory()
    if packet['template_sha256'] != digest(TEMPLATE) or manifest['template_sha256'] != digest(TEMPLATE):
        errors.append('Template hash mismatch.')
    expected_sources = [{'file': s['file'], 'sha256': s['sha256']} for s in manifest['sources']]
    if packet['sources'] != expected_sources:
        errors.append('Packet source manifest changed.')
    files = {s['file']: Path(s['path']) for s in manifest['sources']}
    for item in manifest['sources']:
        if not Path(item['path']).is_file() or digest(item['path']) != item['sha256']:
            errors.append(f'Source changed or missing: {item["file"]}')
    if errors:
        return errors
    pdf = PdfReader(files['insurance_document.pdf'])
    with files['ams360_customer_policy_export.csv'].open(encoding='utf-8-sig', newline='') as h:
        csv_row = next(csv.DictReader(h))
    request = read(files['submission_request.json'])
    seen, semantics = set(), set()
    def check_evidence(ev):
        file = ev['file']
        if file == 'user':
            if not any(h['statement'] == ev['quote'] for h in packet['history']):
                errors.append('User evidence must match a recorded correction statement.')
        elif file not in files:
            errors.append(f'Unknown evidence source: {file}')
        elif file.endswith('.pdf'):
            if not isinstance(ev.get('page'), int) or not 1 <= ev['page'] <= len(pdf.pages):
                errors.append('PDF evidence requires a valid 1-based page.')
            # A quote is not checked by substring: the rendered page may differ from embedded text.
        elif file.endswith('.csv'):
            if ev.get('column') not in csv_row or not csv_row.get(ev.get('column'), '').strip():
                errors.append('CSV evidence must reference a nonempty column.')
            elif ev['quote'] != csv_row[ev['column']]:
                errors.append('CSV evidence quote must equal the source cell.')
        elif file.endswith('.json'):
            if ev.get('key') not in request:
                errors.append('Request evidence requires an existing key.')
            else:
                value = request[ev['key']]
                if ev['quote'] != (json.dumps(value) if isinstance(value, (list, dict)) else str(value)):
                    errors.append('Request evidence quote must equal the source value (JSON for lists).')
    for a in packet['assignments']:
        fid, value, status = a['field_id'], a['value'], a['status']
        if fid in seen or a['semantic'] in semantics:
            errors.append(f'Duplicate field ID or semantic key: {fid}')
        seen.add(fid); semantics.add(a['semantic'])
        if fid not in fields:
            errors.append(f'Unknown field: {fid}'); continue
        meta = fields[fid]
        for ev in a['evidence']:
            check_evidence(ev)
        for alternative in a['alternatives']:
            for ev in alternative['evidence']:
                check_evidence(ev)
        if status in ('conflict', 'missing'):
            if value is not None:
                errors.append(f'Unresolved fields must have null values: {fid}')
            if status == 'conflict' and len(a['alternatives']) < 2:
                errors.append(f'Conflict requires at least two sourced alternatives: {fid}')
            continue
        if not a['evidence'] or not isinstance(value, str) or not value.strip():
            errors.append(f'Filled values require nonempty value and evidence: {fid}'); continue
        if status == 'user_confirmed' and not any(e['file'] == 'user' for e in a['evidence']):
            errors.append(f'User-confirmed value lacks user evidence: {fid}')
        if re.search(r'Signature|Initials', fid, re.I):
            errors.append(f'Electronic signing is not supported: {fid}')
        if meta['flags'] & 1:
            errors.append(f'Read-only field: {fid}')
        if meta['type'] == '/Btn' and value not in meta['states']:
            errors.append(f'Invalid checkbox export state: {fid}')
        if meta['type'] == '/Tx':
            if meta['max_length'] and len(value) > meta['max_length']:
                errors.append(f'Text exceeds maximum length: {fid}')
            if '\n' in value and not meta['flags'] & 4096:
                errors.append(f'Newline in single-line field: {fid}')
            if any(ord(c) < 32 for c in value) or any(ord(c) > 126 for c in value):
                errors.append(f'Unsupported control/non-ASCII glyph; do not silently transliterate: {fid}')
            if 'Enter date:' in meta['label']:
                try: datetime.strptime(value, '%m/%d/%Y')
                except ValueError: errors.append(f'Invalid MM/DD/YYYY date: {fid}')
            if 'Enter amount:' in meta['label'] and not re.fullmatch(r'\$?\d[\d,]*(\.\d{1,2})?', value):
                errors.append(f'Invalid amount: {fid}')
        date_key = ('proposed_effective_date' if 'Policy_EffectiveDate_' in fid else
                    'proposed_expiration_date' if 'Policy_ExpirationDate_' in fid else None)
        if date_key and (value != request[date_key] or not any(e['file'] == 'submission_request.json' and e.get('key') == date_key for e in a['evidence'])):
            errors.append(f'Proposed dates must match submission_request.json: {fid}')
    for issue in packet['issues']:
        for ev in issue['evidence']:
            check_evidence(ev)
    return errors


def approved_values(packet):
    return {a['field_id']: a['value'] for a in packet['assignments'] if a['status'] in ('supported', 'user_confirmed')}


def verify(pdf_path, packet):
    original, fields = inventory()
    result = PdfReader(pdf_path)
    actual = result.get_fields() or {}
    expected = approved_values(packet)
    original_fields = original.get_fields() or {}
    failures = []
    def normalized(v):
        return '' if v is None else str(v)
    for fid, meta in fields.items():
        target = expected.get(fid, original_fields[fid].get('/V'))
        if fid not in actual or normalized(actual[fid].get('/V')) != normalized(target):
            failures.append(f'Canonical field mismatch: {fid}')
    widget_names = set()
    for page in result.pages:
        for ref in page.get('/Annots', []):
            obj = ref.get_object()
            if obj.get('/Subtype') != '/Widget': continue
            fid = field_name(obj)
            if fid not in fields: continue
            widget_names.add(fid)
            target = expected.get(fid, original_fields[fid].get('/V'))
            if normalized(inherited(obj, '/V')) != normalized(target):
                failures.append(f'Widget value mismatch: {fid}')
            if fid in expected:
                ap = obj.get('/AP', {}).get('/N')
                if not ap: failures.append(f'Missing appearance: {fid}')
                elif fields[fid]['type'] == '/Tx' and not ap.get_object().get_data():
                    failures.append(f'Empty appearance: {fid}')
                if fields[fid]['type'] == '/Btn' and str(obj.get('/AS')) != expected[fid]:
                    failures.append(f'Checkbox appearance mismatch: {fid}')
    if set(fields) != widget_names:
        failures.append('Widget inventory changed.')
    if len(result.pages) != len(original.pages): failures.append('Page count changed.')
    if result.trailer['/Root']['/AcroForm'].get('/XFA'): failures.append('Stale XFA retained.')
    return {'technical_pass': not failures, 'fields_checked': len(fields), 'filled_fields': len(expected),
            'errors': failures, 'visual_review': 'pending', 'factual_accuracy': 'not established by this check'}


def fill(packet_path, run_dir):
    run_dir, packet_path = Path(run_dir), Path(packet_path)
    packet = read(packet_path)
    errors = validate(packet, run_dir)
    if errors: raise ValueError('\n'.join(errors))
    if not approved_values(packet): raise ValueError('No supported assignments to fill.')
    out = run_dir / f'revision-{packet["revision"]:03d}'
    out.mkdir(exist_ok=False)
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(TEMPLATE))
    writer._root_object['/AcroForm'].pop('/XFA', None)
    _, field_meta = inventory()
    values = {k: ((v, '/Helv', 0) if field_meta[k]['type'] == '/Tx' else v)
              for k, v in approved_values(packet).items()}
    # pypdf 6.10 ignores a tuple size of zero when a widget has a fixed /DA.
    # Set the actual default appearance to auto-size before regeneration.
    for page in writer.pages:
        for ref in page.get('/Annots', []):
            widget = ref.get_object()
            if field_name(widget) in values and inherited(widget, '/FT') == '/Tx':
                widget[NameObject('/DA')] = TextStringObject('/Helv 0 Tf 0 g')
    writer.update_page_form_field_values(None, values, auto_regenerate=False)
    pdf = out / 'acord-125-draft.pdf'
    with pdf.open('wb') as h: writer.write(h)
    save(out / 'packet.json', packet)
    report = verify(pdf, packet)
    report.update({'generated_at': now(), 'pdf_sha256': digest(pdf), 'packet_sha256': digest(out / 'packet.json')})
    save(out / 'verification.json', report)
    if not report['technical_pass']: raise ValueError('PDF readback failed; do not deliver. See verification.json.')
    render(pdf, out / 'pages')
    unresolved = [a for a in packet['assignments'] if a['status'] in ('missing', 'conflict')]
    lines = ['# Draft application review', '', 'Draft only. Unsupported fields remain blank. Not signed or submitted.', '',
             f'Filled fields: {len(approved_values(packet))}. Unresolved assignments: {len(unresolved)}.', '',
             'Technical readback passed. Visual inspection and factual review are separate.', '', '## Exceptions', '']
    for a in unresolved:
        lines.append(f'- **{a["semantic"]}** ({a["status"]}): {a["note"]}')
        for alt in a['alternatives']: lines.append(f'  - {alt["value"]}')
    for issue in packet['issues']: lines.append(f'- **{issue["field"]}**: {issue["message"]}')
    lines += ['', '## Provenance', '', '| Field | Value | Sources |', '|---|---|---|']
    for a in packet['assignments']:
        if a['status'] not in ('supported', 'user_confirmed'): continue
        sources = ', '.join(e['file'] + (f' p.{e["page"]}' if 'page' in e else '') for e in a['evidence'])
        lines.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n',' ') for x in [a['semantic'], a['value'], sources]) + ' |')
    (out / 'review.md').write_text('\n'.join(lines) + '\n')
    return {'output': str(out), 'technical_pass': True, 'visual_review': 'pending'}


def resolve_value(packet_path, run_dir, fid, value, statement):
    packet_path = Path(packet_path)
    packet = read(packet_path)
    match = next((a for a in packet['assignments'] if a['field_id'] == fid), None)
    if not match: raise ValueError('Resolution requires an existing assignment.')
    packet['history'].append({'at': now(), 'field_id': fid, 'previous_value': match['value'],
                              'previous_status': match['status'], 'statement': statement})
    match.update(value=value, status='user_confirmed')
    match['evidence'].append({'file': 'user', 'quote': statement})
    packet['revision'] += 1
    errors = validate(packet, run_dir)
    if errors: raise ValueError('\n'.join(errors))
    next_path = packet_path.with_name(f'packet-r{packet["revision"]:03d}.json')
    if next_path.exists(): raise ValueError('Revision packet already exists.')
    save(next_path, packet)
    return {'packet': str(next_path), 'note': 'Historical alternatives preserved. Reconcile related issues before filling.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('doctor')
    p = sp.add_parser('inspect'); p.add_argument('--match', default=''); p.add_argument('--out')
    p = sp.add_parser('prepare'); p.add_argument('--input-dir', required=True); p.add_argument('--run-dir', required=True)
    for name in ('validate', 'fill'):
        p = sp.add_parser(name); p.add_argument('--packet', required=True); p.add_argument('--run-dir', required=True)
    p = sp.add_parser('verify'); p.add_argument('--pdf', required=True); p.add_argument('--packet', required=True)
    p = sp.add_parser('render'); p.add_argument('--pdf', required=True); p.add_argument('--out', required=True)
    p = sp.add_parser('resolve'); p.add_argument('--packet', required=True); p.add_argument('--run-dir', required=True)
    p.add_argument('--field', required=True); p.add_argument('--value', required=True); p.add_argument('--statement', required=True)
    p = sp.add_parser('record-visual-review'); p.add_argument('--revision-dir', required=True)
    p.add_argument('--result', choices=['pass','fail'], required=True); p.add_argument('--note', required=True)
    args = ap.parse_args()
    try:
        if args.cmd == 'doctor':
            import importlib.metadata
            result = {p: importlib.metadata.version(p) for p in ['pypdf','pypdfium2','jsonschema','Pillow']}
            result['template_exists'] = TEMPLATE.is_file()
        elif args.cmd == 'inspect':
            _, fields = inventory()
            result = {k:v for k,v in fields.items() if args.match.lower() in (k+' '+v['label']).lower()}
            if args.out: save(args.out, result); result = {'fields':len(result),'path':args.out}
        elif args.cmd == 'prepare': result = prepare(args.input_dir, args.run_dir)
        elif args.cmd == 'validate':
            errors = validate(read(args.packet), args.run_dir)
            result = {'valid':not errors, 'errors':errors}
            if errors: print(json.dumps(result)); return 1
        elif args.cmd == 'fill': result = fill(args.packet, args.run_dir)
        elif args.cmd == 'verify':
            result = verify(args.pdf, read(args.packet))
            if not result['technical_pass']: print(json.dumps(result)); return 1
        elif args.cmd == 'render': render(args.pdf,args.out); result = {'pages':args.out}
        elif args.cmd == 'resolve': result = resolve_value(args.packet,args.run_dir,args.field,args.value,args.statement)
        else:
            folder = Path(args.revision_dir)
            path = folder / 'verification.json'
            result = read(path)
            if result['pdf_sha256'] != digest(folder / 'acord-125-draft.pdf'): raise ValueError('PDF changed after verification.')
            if result['packet_sha256'] != digest(folder / 'packet.json'): raise ValueError('Packet changed after verification.')
            result.update(visual_review=args.result, visual_review_note=args.note, visual_review_at=now())
            save(path,result)
        print(json.dumps(result,indent=2))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({'error':str(exc)}), file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
