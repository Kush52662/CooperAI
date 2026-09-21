#!/usr/bin/env python3
"""Deterministic PDF tools. No model calls, case answers, or automatic source precedence."""
import argparse
import csv
import copy
import math
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
FORM_REGISTRY = ROOT / 'assets/forms.json'


REQUEST_COLUMNS = {
    'output_form': 'Requested Form',
    'transaction_status': 'Transaction Status',
    'proposed_effective_date': 'Proposed Effective Date',
    'proposed_expiration_date': 'Proposed Expiration Date',
    'requested_lines_of_business': 'Requested Lines of Business',
}


def submission_context_from_csv(row):
    missing = [column for column in REQUEST_COLUMNS.values() if not row.get(column, '').strip()]
    if missing:
        raise ValueError('Missing submission columns/values: ' + ', '.join(missing))
    request = {key: row[column].strip() for key, column in REQUEST_COLUMNS.items()}
    request['requested_lines_of_business'] = [v.strip() for v in request['requested_lines_of_business'].split(';') if v.strip()]
    return request


def save_new(path, value):
    with Path(path).open('x') as handle:
        handle.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def form_definition(form_id):
    registry = read(FORM_REGISTRY)
    if form_id not in registry:
        raise ValueError(f'Unsupported requested form: {form_id}. Registered forms: {", ".join(registry)}')
    form = dict(registry[form_id])
    required = {'edition', 'template', 'guidance', 'output_filename', 'proposed_date_fields'}
    if set(form) != required:
        raise ValueError(f'Invalid registry entry for {form_id}.')
    for key in ('template', 'guidance'):
        path = (ROOT / form[key]).resolve()
        if ROOT not in path.parents or not path.is_file():
            raise ValueError(f'Registered {key} is missing or outside the skill: {form[key]}')
        form[key + '_path'] = path
    if set(form['proposed_date_fields']) != {'proposed_effective_date', 'proposed_expiration_date'}:
        raise ValueError(f'Invalid proposed-date field mapping for {form_id}.')
    form['form_id'] = form_id
    return form


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


def inventory(path):
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
    names = ['ams360_customer_policy_export.csv', 'insurance_document.pdf']
    paths = [input_dir / name for name in names]
    supplied = {path.name for path in input_dir.iterdir() if path.is_file() and not path.name.startswith('.')}
    if supplied != set(names):
        raise ValueError('Provide exactly ams360_customer_policy_export.csv and insurance_document.pdf.')
    with paths[0].open(encoding='utf-8-sig', newline='') as handle:
        table = csv.DictReader(handle)
        rows = list(table)
        if len(rows) != 1 or len(set(table.fieldnames or [])) != len(table.fieldnames or []) or any(k is None or v is None for row in rows for k, v in row.items()):
            raise ValueError('CSV must contain unique headers and exactly one well-formed account row.')
    request = submission_context_from_csv(rows[0])
    form = form_definition(request['output_form'])
    start = datetime.strptime(request['proposed_effective_date'], '%m/%d/%Y')
    end = datetime.strptime(request['proposed_expiration_date'], '%m/%d/%Y')
    if end <= start:
        raise ValueError('Requested expiration must follow effective date.')
    if not isinstance(request.get('requested_lines_of_business'), list) or not request['requested_lines_of_business']:
        raise ValueError('Supply requested lines of business.')
    source = PdfReader(paths[1])
    if source.is_encrypted:
        raise ValueError('Encrypted PDFs are outside this MVP.')
    run_dir.mkdir(parents=True, exist_ok=False)
    sources = [{'file': p.name, 'path': str(p), 'sha256': digest(p)} for p in paths]
    manifest = {'started_at': now(), 'form_id': form['form_id'], 'form_edition': form['edition'],
                'form_guidance': form['guidance'], 'output_filename': form['output_filename'],
                'template_sha256': digest(form['template_path']), 'sources': sources, 'request': request}
    save(run_dir / 'manifest.json', manifest)
    render(paths[1], run_dir / 'source-pages')
    _, fields = inventory(form['template_path'])
    save(run_dir / 'fields.json', fields)
    save(run_dir / 'packet.json', {'schema_version': '1.0', 'form_id': form['form_id'],
         'template_sha256': digest(form['template_path']),
         'sources': [{'file': p['file'], 'sha256': p['sha256']} for p in sources],
         'revision': 1, 'assignments': [], 'issues': [], 'history': []})
    return {'run_dir': str(run_dir), 'form_id': form['form_id'], 'guidance': form['guidance'],
            'fields': len(fields), 'source_pages': len(source.pages),
            'next': 'Read the CSV and inspect every rendered PDF page; author packet.json using skill guidance.'}


def validate(packet, run_dir):
    run_dir = Path(run_dir)
    schema = read(ROOT / 'references/packet.schema.json')
    errors = [f'{".".join(map(str, e.path))}: {e.message}' for e in Draft202012Validator(schema).iter_errors(packet)]
    if errors:
        return errors
    manifest = read(run_dir / 'manifest.json')
    form = form_definition(packet['form_id'])
    _, fields = inventory(form['template_path'])
    if manifest.get('form_id') != packet['form_id']:
        errors.append('Packet form does not match the prepared run.')
    if packet['template_sha256'] != digest(form['template_path']) or manifest['template_sha256'] != digest(form['template_path']):
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
    request = submission_context_from_csv(csv_row)
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
            # The multimodal agent supplies the quotation from the rendered page.
        elif file.endswith('.csv'):
            if ev.get('column') not in csv_row or not csv_row.get(ev.get('column'), '').strip():
                errors.append('CSV evidence must reference a nonempty column.')
            elif ev['quote'] != csv_row[ev['column']]:
                errors.append('CSV evidence quote must equal the source cell.')
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
        if status == 'user_confirmed' and not any(e['file'] == 'user' and any(h['field_id'] == fid and h['statement'] == e['quote'] for h in packet['history']) for e in a['evidence']):
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
        date_key = next((key for key, marker in form['proposed_date_fields'].items() if marker in fid), None)
        if date_key and (value != request[date_key] or not any(e['file'] == 'ams360_customer_policy_export.csv' and e.get('column') == REQUEST_COLUMNS[date_key] for e in a['evidence'])):
            errors.append(f'Proposed dates must match submission inputs: {fid}')
    for issue in packet['issues']:
        for ev in issue['evidence']:
            check_evidence(ev)
    return errors


def approved_values(packet):
    return {a['field_id']: a['value'] for a in packet['assignments'] if a['status'] in ('supported', 'user_confirmed')}


def verify(pdf_path, packet):
    form = form_definition(packet['form_id'])
    original, fields = inventory(form['template_path'])
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
    form = form_definition(packet['form_id'])
    errors = validate(packet, run_dir)
    if errors: raise ValueError('\n'.join(errors))
    if not packet['assignments']: raise ValueError('No assignments to render.')
    out = run_dir / f'revision-{packet["revision"]:03d}'
    out.mkdir(exist_ok=False)
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(form['template_path']))
    writer._root_object['/AcroForm'].pop('/XFA', None)
    _, field_meta = inventory(form['template_path'])
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
    pdf = out / form['output_filename']
    with pdf.open('wb') as h: writer.write(h)
    save(out / 'packet.json', packet)
    report = verify(pdf, packet)
    report.update({'generated_at': now(), 'output_filename': form['output_filename'],
                   'pdf_sha256': digest(pdf), 'packet_sha256': digest(out / 'packet.json')})
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
    lines += ['', '## Retained source questions', '']
    for issue in review_packet(packet_path)['source_issues']:
        lines.append(f'- **{issue["field"]}**: {issue["message"]} [{issue["context"]}]')
    lines += ['', '## Provenance', '', '| Field | Value | Sources |', '|---|---|---|']
    for a in packet['assignments']:
        if a['status'] not in ('supported', 'user_confirmed'): continue
        sources = ', '.join(e['file'] + (f' p.{e["page"]}' if 'page' in e else '') for e in a['evidence'])
        lines.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n',' ') for x in [a['semantic'], a['value'], sources]) + ' |')
    (out / 'review.md').write_text('\n'.join(lines) + '\n')
    return {'output': str(out), 'technical_pass': True, 'visual_review': 'pending'}


def revision_head(run_dir):
    """Saved packets are the revision ledger; no separate database or pointer."""
    run = Path(run_dir)
    paths = [run/'packet.json', *run.glob('packet-r*.json'), *run.glob('revision-*/packet.json')]
    return max((read(p)['revision'] for p in paths if p.is_file()), default=0)


def checked_packet(packet_path, run_dir):
    packet = read(packet_path)
    errors = validate(packet, run_dir)
    if errors: raise ValueError('\n'.join(errors))
    if packet['revision'] != revision_head(run_dir):
        raise ValueError('Stale base revision. Review the latest saved packet before editing.')
    return packet


def corrected_packet(base, changes, run_dir):
    if not isinstance(changes, list) or not changes:
        raise ValueError('Corrections must be a nonempty list.')
    packet = copy.deepcopy(base)
    form = form_definition(base['form_id'])
    _, fields = inventory(form['template_path'])
    seen = set()
    for change in changes:
        if not isinstance(change, dict) or set(change) - {'field_id', 'semantic', 'value', 'statement'} or not {'field_id', 'value', 'statement'} <= set(change):
            raise ValueError('Each correction needs field_id, value, statement; semantic is required for additions.')
        fid, value, statement = change['field_id'], change['value'], change['statement']
        if not isinstance(fid, str) or fid not in fields or fid in seen:
            raise ValueError('Unknown or duplicate correction field.')
        seen.add(fid)
        if re.search(r'Signature|Initials', fid, re.I) or fields[fid]['flags'] & 1:
            raise ValueError('Cannot correct signatures or read-only fields.')
        if not isinstance(statement, str) or not statement.strip():
            raise ValueError('An explicit, nonempty user statement is required.')
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError('Use a nonempty string, or null to explicitly clear a value.')
        item = next((a for a in packet['assignments'] if a['field_id'] == fid), None)
        if item is None:
            semantic = change.get('semantic')
            if not isinstance(semantic, str) or not semantic.strip():
                raise ValueError('New assignments require a semantic name.')
            item = {'field_id': fid, 'semantic': semantic, 'value': None, 'status': 'missing',
                    'evidence': [], 'alternatives': [], 'note': ''}
            packet['assignments'].append(item)
            previous_status = 'unassigned'
        else:
            if 'semantic' in change and change['semantic'] != item['semantic']:
                raise ValueError('A correction cannot rename an existing semantic key.')
            previous_status = item['status']
        packet['history'].append({'at': now(), 'field_id': fid, 'previous_value': item['value'],
                                  'previous_status': previous_status, 'statement': statement})
        item.update(value=value, status='missing' if value is None else 'user_confirmed')
        item['evidence'].append({'file': 'user', 'quote': statement})
        if value is None: item['note'] = 'Explicitly cleared by user; remains unanswered.'
    packet['revision'] = base['revision'] + 1
    errors = validate(packet, run_dir)
    if errors: raise ValueError('\n'.join(errors))
    return packet


def stage_corrections(packet_path, run_dir, changes, out):
    base = checked_packet(packet_path, run_dir)
    corrected_packet(base, changes, run_dir)
    stage = {'base_revision': base['revision'], 'base_sha256': digest(packet_path),
             'manifest_sha256': digest(Path(run_dir)/'manifest.json'), 'changes': changes}
    save_new(out, stage)
    return {'stage': str(out), 'base_revision': base['revision'], 'corrections': len(changes), 'applied': False}


def apply_corrections(packet_path, run_dir, stage_path):
    base = checked_packet(packet_path, run_dir)
    stage = read(stage_path)
    if set(stage) != {'base_revision', 'base_sha256', 'manifest_sha256', 'changes'}:
        raise ValueError('Invalid staged correction record.')
    if (stage['base_revision'] != base['revision'] or stage['base_sha256'] != digest(packet_path)
            or stage['manifest_sha256'] != digest(Path(run_dir)/'manifest.json')):
        raise ValueError('Stale or wrong-run corrections; stage against the current packet.')
    packet = corrected_packet(base, stage['changes'], run_dir)
    path = Path(run_dir)/f'packet-r{packet["revision"]:03d}.json'
    save_new(path, packet)
    return {'packet': str(path), 'revision': packet['revision'], 'corrections': len(stage['changes']),
            'next': 'Validate, fill, inspect all output pages, and deliver the new PDF.'}


def review_packet(packet_path, before=None):
    packet = read(packet_path)
    previous = read(before) if before else None
    if previous and (previous['form_id'] != packet['form_id'] or previous['sources'] != packet['sources'] or previous['template_sha256'] != packet['template_sha256']):
        raise ValueError('Cannot compare packets from different sources or templates.')
    prior = {a['field_id']: a for a in previous['assignments']} if previous else {}
    current = {a['field_id']: a for a in packet['assignments']}
    changes = []
    if previous:
        for fid in sorted(current.keys() | prior.keys()):
            old, new = prior.get(fid), current.get(fid)
            if old != new:
                changes.append({'field_id': fid, 'semantic': (new or old)['semantic'],
                                'before': old['value'] if old else None, 'after': new['value'] if new else None,
                                'before_status': old['status'] if old else 'unassigned',
                                'after_status': new['status'] if new else 'unassigned'})
    unresolved = [a for a in packet['assignments'] if a['status'] in ('missing', 'conflict')]
    confirmed = {a['semantic'] for a in packet['assignments'] if a['status'] == 'user_confirmed'}
    confirmed.update(a['field_id'] for a in packet['assignments'] if a['status'] == 'user_confirmed')
    return {'revision': packet['revision'], 'packet_sha256': digest(packet_path),
            'assignments': packet['assignments'], 'unresolved': unresolved,
            'counts': {'filled': len(approved_values(packet)), 'unresolved': len(unresolved), 'source_issues': len(packet['issues'])},
            'source_issues': [dict(i, context='retained source issue; matching field corrected' if i['field'] in confirmed else 'requires review') for i in packet['issues']],
            'changes': changes, 'history': packet['history']}


def review_markdown(report):
    lines = [f'# Draft review — revision {report["revision"]}', '',
             f'{report["counts"]["filled"]} filled; {report["counts"]["unresolved"]} unresolved fields.', '', '## Fields']
    for a in report['assignments']:
        label = a['semantic'].replace('_', ' ').replace('.', ' / ')
        lines.append(f'- {label}: {a["value"] or "Blank"} ({a["status"]})')
        for alt in a['alternatives']:
            locations = ', '.join(e['file'] + (f' page {e["page"]}' if e.get('page') else ' '+e.get('column', e.get('key', ''))) for e in alt['evidence'])
            lines.append(f'  - Alternative: {alt["value"]} — {locations}')
    lines += ['', '## Changes']
    for c in report['changes']: lines.append(f'- {c["semantic"]}: {c["before"]} → {c["after"]}')
    lines += ['', '## Source questions (retained separately)']
    for i in report['source_issues']: lines.append(f'- {i["field"]}: {i["message"]} [{i["context"]}]')
    return '\n'.join(lines) + '\n'


def field_preview(fid, pdf, out, form_id):
    import pypdfium2 as pdfium
    form = form_definition(form_id)
    _, fields = inventory(form['template_path'])
    if fid not in fields: raise ValueError('Unknown template field.')
    reader, actual = inventory(pdf)
    template_reader = PdfReader(form['template_path'])
    if len(reader.pages) != len(template_reader.pages) or fid not in actual or actual[fid]['widgets'] != fields[fid]['widgets']:
        raise ValueError('Preview requires the known template or its generated draft.')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    doc = pdfium.PdfDocument(str(pdf))
    previews = []
    try:
        doc.init_forms()
        for n, widget in enumerate(fields[fid]['widgets'], 1):
            page = doc[widget['page']-1]
            try:
                if reader.pages[widget['page']-1].rotation:
                    raise ValueError('Rotated-page previews are unsupported.')
                width, height = page.get_size()
                x0,y0,x1,y1 = widget['rect']
                rect = [max(0, x0-96), max(0, y0-36), min(width, x1+96), min(height, y1+36)]
                bitmap = page.render(scale=2, may_draw_forms=True)
                try:
                    image = bitmap.to_pil()
                    box = [math.floor(rect[0]*image.width/width), math.floor((height-rect[3])*image.height/height),
                           math.ceil(rect[2]*image.width/width), math.ceil((height-rect[1])*image.height/height)]
                    path = out/f'field-{n}-page-{widget["page"]}.png'
                    image.crop(box).save(path)
                    previews.append({'path': str(path), 'page': widget['page'], 'field_rect': widget['rect'], 'crop_rect': rect, 'pixel_box': box})
                finally: bitmap.close()
            finally: page.close()
    finally: doc.close()
    result = {'field_id': fid, 'label': fields[fid]['label'], 'pdf_sha256': digest(pdf), 'previews': previews}
    save(out/'preview.json', result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('doctor')
    p = sp.add_parser('inspect'); p.add_argument('--form', required=True); p.add_argument('--match', default=''); p.add_argument('--out')
    p = sp.add_parser('prepare'); p.add_argument('--input-dir', required=True); p.add_argument('--run-dir', required=True)
    for name in ('validate', 'fill'):
        p = sp.add_parser(name); p.add_argument('--packet', required=True); p.add_argument('--run-dir', required=True)
    p = sp.add_parser('verify'); p.add_argument('--pdf', required=True); p.add_argument('--packet', required=True)
    p = sp.add_parser('render'); p.add_argument('--pdf', required=True); p.add_argument('--out', required=True)
    p = sp.add_parser('review'); p.add_argument('--packet', required=True); p.add_argument('--before'); p.add_argument('--format', choices=['json','markdown'], default='json')
    p = sp.add_parser('stage-corrections'); p.add_argument('--packet', required=True); p.add_argument('--run-dir', required=True)
    p.add_argument('--changes', required=True); p.add_argument('--out', required=True)
    p = sp.add_parser('apply-corrections'); p.add_argument('--packet', required=True); p.add_argument('--run-dir', required=True); p.add_argument('--stage', required=True)
    p = sp.add_parser('field-preview'); p.add_argument('--form', required=True); p.add_argument('--field', required=True); p.add_argument('--pdf'); p.add_argument('--out', required=True)
    p = sp.add_parser('record-visual-review'); p.add_argument('--revision-dir', required=True)
    p.add_argument('--result', choices=['pass','fail'], required=True); p.add_argument('--note', required=True)
    args = ap.parse_args()
    try:
        if args.cmd == 'doctor':
            import importlib.metadata
            result = {p: importlib.metadata.version(p) for p in ['pypdf','pypdfium2','jsonschema','Pillow']}
            result['registered_forms'] = {form_id: str(form_definition(form_id)['template_path']) for form_id in read(FORM_REGISTRY)}
        elif args.cmd == 'inspect':
            _, fields = inventory(form_definition(args.form)['template_path'])
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
        elif args.cmd == 'review':
            result = review_packet(args.packet, args.before)
            if args.format == 'markdown': print(review_markdown(result)); return 0
        elif args.cmd == 'stage-corrections': result = stage_corrections(args.packet, args.run_dir, read(args.changes), args.out)
        elif args.cmd == 'apply-corrections': result = apply_corrections(args.packet, args.run_dir, args.stage)
        elif args.cmd == 'field-preview':
            form = form_definition(args.form)
            result = field_preview(args.field, args.pdf or form['template_path'], args.out, args.form)
        else:
            folder = Path(args.revision_dir)
            path = folder / 'verification.json'
            result = read(path)
            if result['pdf_sha256'] != digest(folder / result['output_filename']): raise ValueError('PDF changed after verification.')
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
