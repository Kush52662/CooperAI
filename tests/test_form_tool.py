"""Actual bundled-template tests. These fixtures are tool tests, not model evaluation."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('form_tool', ROOT/'skills/acord-form-filler/scripts/form_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
NAME = 'F[0].P1[0].NamedInsured_FullName_A[0]'
QUOTE = 'F[0].P1[0].Policy_Status_QuoteIndicator_A[0]'
DATE = 'F[0].P1[0].Policy_EffectiveDate_A[0]'
FORM_ID = 'ACORD 125 (2016/03)'
FORM = tool.form_definition(FORM_ID)
TEMPLATE = FORM['template_path']
OUTPUT = FORM['output_filename']

class FormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.run_dir = Path(cls.tmp.name)/'run'
        with patch.object(tool,'render'):
            tool.prepare(ROOT/'sample input data/00_clean_walkthrough', cls.run_dir)
        cls.base = tool.read(cls.run_dir/'packet.json')
        import csv
        with (ROOT/'sample input data/00_clean_walkthrough/ams360_customer_policy_export.csv').open() as h:
            cls.row=next(csv.DictReader(h))
        cls.request=tool.submission_context_from_csv(cls.row)

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def packet(self):
        p=copy.deepcopy(self.base)
        p['assignments']=[{'semantic':'applicant.name','field_id':NAME,'value':self.row['Account Name'],'status':'supported',
            'evidence':[{'file':'ams360_customer_policy_export.csv','column':'Account Name','quote':self.row['Account Name']}],
            'alternatives':[],'note':''}]
        return p

    def test_inventory_excludes_structural_nodes(self):
        _,fields=tool.inventory(TEMPLATE)
        self.assertEqual(len(fields),551)
        self.assertEqual(fields[QUOTE]['states'],['/1','/Off'])
        self.assertIn('named insured',fields[NAME]['label'])

    def test_valid_sourced_assignment(self): self.assertEqual(tool.validate(self.packet(),self.run_dir),[])

    def test_wrong_field_id(self):
        p=self.packet();p['assignments'][0]['field_id']='not_a_field'
        self.assertIn('Unknown field',str(tool.validate(p,self.run_dir)))

    def test_duplicate_assignment(self):
        p=self.packet();p['assignments']*=2
        self.assertIn('Duplicate',str(tool.validate(p,self.run_dir)))

    def test_evidence_must_match_csv_cell(self):
        p=self.packet();p['assignments'][0]['evidence'][0]['quote']='invented'
        self.assertIn('quote must equal',str(tool.validate(p,self.run_dir)))

    def test_source_hash_changes_rejected(self):
        p=self.packet();p['sources'][0]['sha256']='0'*64
        self.assertIn('source manifest changed',str(tool.validate(p,self.run_dir)))

    def test_invalid_pdf_page(self):
        p=self.packet();p['assignments'][0]['evidence']=[{'file':'insurance_document.pdf','page':99,'quote':'x'}]
        self.assertIn('valid 1-based page',str(tool.validate(p,self.run_dir)))

    def test_conflict_cannot_be_silently_filled(self):
        p=self.packet();p['assignments'][0]['status']='conflict'
        self.assertIn('null',str(tool.validate(p,self.run_dir)))

    def test_invalid_checkbox_state(self):
        p=self.packet();p['assignments'][0].update(field_id=QUOTE,value='yes')
        self.assertIn('checkbox',str(tool.validate(p,self.run_dir)))

    def test_historical_date_not_allowed_as_proposed_date(self):
        p=self.packet();p['assignments'][0].update(field_id=DATE,value='09/20/2024')
        self.assertIn('Proposed dates',str(tool.validate(p,self.run_dir)))

    def test_unsupported_signatures(self):
        p=self.packet();p['assignments'][0]['field_id']='F[0].P4[0].NamedInsured_Signature_A[0]'
        self.assertIn('signing',str(tool.validate(p,self.run_dir)))

    def test_fake_user_confirmation(self):
        p=self.packet();p['assignments'][0]['status']='user_confirmed'
        self.assertIn('lacks user evidence',str(tool.validate(p,self.run_dir)))

    def test_pdf_roundtrip_preserves_unassigned_fields_and_checkboxes(self):
        p=self.packet()
        p['assignments'].append({'semantic':'policy.transaction','field_id':QUOTE,'value':'/1','status':'supported',
            'evidence':[{'file':'ams360_customer_policy_export.csv','column':'Transaction Status','quote':'QUOTE'}],
            'alternatives':[],'note':''})
        path=Path(self.tmp.name)/'packet.json';tool.save(path,p)
        with patch.object(tool,'render'):
            result=tool.fill(path,self.run_dir)
        out=Path(result['output'])/OUTPUT
        self.assertTrue(tool.verify(out,p)['technical_pass'])
        r=PdfReader(out)
        self.assertNotIn('/XFA',r.trailer['/Root']['/AcroForm'])
        self.assertEqual(str(r.get_fields()[QUOTE]['/V']),'/1')
        # A genuine output change must fail verification even though the file still parses.
        writer=PdfWriter();writer.clone_document_from_reader(r)
        writer.update_page_form_field_values(None,{NAME:'WRONG ACCOUNT'},auto_regenerate=False)
        bad=Path(self.tmp.name)/'bad.pdf'
        with bad.open('wb') as h: writer.write(h)
        self.assertFalse(tool.verify(bad,p)['technical_pass'])
        with self.assertRaises(FileExistsError): tool.fill(path,self.run_dir)

    def test_long_carrier_appearance_shrinks_to_fit(self):
        p=self.packet();p['revision']=42
        carrier='F[0].P3[0].PriorCoverage_GeneralLiability_InsurerFullName_A[0]'
        full='Selective Insurance Company of the Southeast'
        p['assignments'][0].update(field_id=carrier,value=full)
        path=Path(self.tmp.name)/'long.json';tool.save(path,p)
        with patch.object(tool,'render'): result=tool.fill(path,self.run_dir)
        r=PdfReader(Path(result['output'])/OUTPUT)
        import re
        for ref in r.pages[2]['/Annots']:
            obj=ref.get_object()
            if tool.field_name(obj)==carrier:
                stream=obj['/AP']['/N'].get_data().decode()
                size=float(re.search(r'/Helv ([0-9.]+) Tf',stream).group(1))
                self.assertLess(size,8)
                self.assertIn(full,stream)
                break
        else: self.fail('Carrier widget missing')

    def test_missing_stays_blank(self):
        p=self.packet();p['assignments'][0].update(value=None,status='missing',evidence=[])
        self.assertEqual(tool.validate(p,self.run_dir),[])
        self.assertEqual(tool.approved_values(p),{})

    def test_registered_form_drives_manifest_and_rendered_pages(self):
        manifest=tool.read(self.run_dir/'manifest.json')
        self.assertEqual(manifest['form_id'],FORM_ID)
        self.assertEqual(manifest['form_guidance'],'references/acord-125.md')
        self.assertEqual(manifest['output_filename'],OUTPUT)
        self.assertFalse((self.run_dir/'source-text.txt').exists())
        self.assertEqual(len(self.base['sources']),2)

if __name__=='__main__': unittest.main()
