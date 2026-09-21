"""Behavior tests using the actual template; no model evaluation claims."""
import copy
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('conversation_tool', ROOT/'skills/acord-form-filler/scripts/form_tool.py')
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
NAME = 'F[0].P1[0].NamedInsured_FullName_A[0]'
PHONE = 'F[0].P1[0].NamedInsured_Primary_PhoneNumber_A[0]'
DATE = 'F[0].P1[0].Policy_EffectiveDate_A[0]'
FORM_ID = 'ACORD 125 (2016/03)'
FORM = t.form_definition(FORM_ID)
TEMPLATE = FORM['template_path']
OUTPUT = FORM['output_filename']

class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name); self.source = self.home/'inputs'; self.source.mkdir()
        case = ROOT/'sample input data/00_clean_walkthrough'
        for name in ['ams360_customer_policy_export.csv','insurance_document.pdf']:
            shutil.copy(case/name,self.source/name)
        self.run = self.home/'run'
        with patch.object(t,'render'): t.prepare(self.source,self.run)
        self.packet = self.run/'packet.json'
        p = t.read(self.packet)
        p['assignments'] = [{'field_id': NAME,'semantic':'applicant.name','value':'LAWN AND ORDER MOWING LLC','status':'supported','evidence':[{'file':'ams360_customer_policy_export.csv','column':'Account Name','quote':'LAWN AND ORDER MOWING LLC'}],'alternatives':[],'note':''}]
        t.save(self.packet,p)

    def stage(self, changes, name='stage.json'):
        path=self.home/name
        t.stage_corrections(self.packet,self.run,changes,path)
        return path

    def change(self, fid=NAME, value='Corrected Test LLC', **extra):
        return dict(field_id=fid,value=value,statement=f'Explicit test correction to {value}',**extra)

    def test_two_input_date_provenance(self):
        p=t.read(self.packet)
        self.assertEqual(len(p['sources']),2)
        p['assignments'].append({'field_id':DATE,'semantic':'proposal.start','value':'10/01/2026','status':'supported','evidence':[{'file':'ams360_customer_policy_export.csv','column':'Proposed Effective Date','quote':'10/01/2026'}],'alternatives':[],'note':''})
        self.assertEqual(t.validate(p,self.run),[])

    def test_additional_json_input_rejected(self):
        t.save(self.source/'submission_request.json',{'unsupported':True})
        with self.assertRaisesRegex(ValueError,'exactly ams360_customer_policy_export.csv and insurance_document.pdf'):
            t.prepare(self.source,self.home/'bad')
        self.assertFalse((self.home/'bad').exists())

    def test_missing_submission_columns_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing submission'):
            t.submission_context_from_csv({'Requested Form':FORM_ID})
        with self.assertRaisesRegex(ValueError,'Unsupported requested form'):
            t.form_definition('ACORD 126 (unregistered test)')

    def test_stage_does_not_mutate_and_batch_has_one_revision(self):
        before=self.packet.read_bytes()
        stage=self.stage([self.change(),self.change(PHONE,'555-0100',semantic='applicant.phone')])
        self.assertEqual(self.packet.read_bytes(),before)
        self.assertFalse((self.run/'packet-r002.json').exists())
        result=t.apply_corrections(self.packet,self.run,stage);new=t.read(result['packet'])
        self.assertEqual(new['revision'],2);self.assertEqual(len(new['history']),2)
        self.assertEqual(self.packet.read_bytes(),before)
        with patch.object(t,'render'): output=t.fill(result['packet'],self.run)
        self.assertTrue(t.verify(Path(output['output'])/OUTPUT,new)['technical_pass'])

    def test_invalid_batch_is_all_or_nothing(self):
        before=self.packet.read_bytes()
        with self.assertRaises(ValueError):self.stage([self.change(),self.change('made-up-field')])
        self.assertEqual(self.packet.read_bytes(),before)
        self.assertFalse((self.home/'stage.json').exists())
        with self.assertRaises(ValueError):self.stage([self.change(),self.change()])

    def test_stale_batch_and_wrong_run_rejected(self):
        first=self.stage([self.change()]);second=self.stage([self.change(value='Different LLC')],'second.json')
        t.apply_corrections(self.packet,self.run,first)
        with self.assertRaisesRegex(ValueError,'Stale'):t.apply_corrections(self.packet,self.run,second)
        self.assertFalse((self.run/'packet-r003.json').exists())

    def test_packet_changed_after_staging(self):
        stage=self.stage([self.change()]);p=t.read(self.packet);p['issues'].append({'field':'other','message':'New issue','evidence':[]});t.save(self.packet,p)
        with self.assertRaisesRegex(ValueError,'Stale'):t.apply_corrections(self.packet,self.run,stage)

    def test_clear_retains_alternatives_and_unrelated_values(self):
        p=t.read(self.packet);original=copy.deepcopy(p['assignments'][0])
        p['assignments'].append({'field_id':PHONE,'semantic':'phone','value':None,'status':'conflict','evidence':[], 'alternatives':[{'value':'111','evidence':[{'file':'insurance_document.pdf','page':1,'quote':'111'}]},{'value':'222','evidence':[{'file':'insurance_document.pdf','page':1,'quote':'222'}]}],'note':'Conflict'})
        t.save(self.packet,p)
        stage=self.stage([self.change(PHONE,None)])
        path=t.apply_corrections(self.packet,self.run,stage)['packet'];new=t.read(path)
        self.assertEqual(new['assignments'][0],original)
        self.assertEqual(new['assignments'][1]['status'],'missing')
        self.assertEqual(new['assignments'][1]['alternatives'],p['assignments'][1]['alternatives'])
        with patch.object(t,'render'): result=t.fill(path,self.run)
        self.assertTrue(t.verify(Path(result['output'])/OUTPUT,new)['technical_pass'])

    def test_user_evidence_must_match_field_history(self):
        p=t.read(self.packet);p['assignments'][0].update(status='user_confirmed',evidence=[{'file':'user','quote':'yes'}])
        p['history']=[{'at':t.now(),'field_id':PHONE,'previous_value':None,'previous_status':'missing','statement':'yes'}]
        self.assertTrue(t.validate(p,self.run))

    def test_review_distinguishes_resolved_fields_and_source_issues(self):
        p=t.read(self.packet);p['issues']=[{'field':'applicant.name','message':'Source discrepancy','evidence':[]}];t.save(self.packet,p)
        stage=self.stage([self.change()]);path=t.apply_corrections(self.packet,self.run,stage)['packet']
        report=t.review_packet(path,self.packet)
        self.assertEqual(report['counts']['unresolved'],0)
        self.assertEqual(len(report['changes']),1)
        self.assertIn('corrected',report['source_issues'][0]['context'])
        self.assertIn('Corrected Test LLC',t.review_markdown(report))

    def test_clearing_last_value_produces_blank_draft(self):
        stage=self.stage([self.change(value=None)])
        path=t.apply_corrections(self.packet,self.run,stage)['packet']
        with patch.object(t,'render'):result=t.fill(path,self.run)
        self.assertEqual(t.verify(Path(result['output'])/OUTPUT,t.read(path))['filled_fields'],0)

    def test_apply_revalidates_tampered_batch(self):
        stage=self.stage([self.change()]);data=t.read(stage)
        data['changes'].append(self.change('unknown'))
        t.save(stage,data)
        with self.assertRaises(ValueError):t.apply_corrections(self.packet,self.run,stage)
        self.assertFalse((self.run/'packet-r002.json').exists())

    def test_stage_cannot_be_used_in_different_run(self):
        stage=self.stage([self.change()]);other=self.home/'other'
        with patch.object(t,'render'):t.prepare(self.source,other)
        t.save(other/'packet.json',t.read(self.packet))
        with self.assertRaisesRegex(ValueError,'wrong-run'):t.apply_corrections(other/'packet.json',other,stage)

    def test_crop_geometry_and_pixels_match_rendered_template(self):
        result=t.field_preview(NAME,TEMPLATE,self.home/'crop',FORM_ID)
        import pypdfium2 as pdfium
        info=result['previews'][0]
        with Image.open(info['path']) as crop:
            box=info['pixel_box'];self.assertEqual(crop.size,(box[2]-box[0],box[3]-box[1]))
            doc=pdfium.PdfDocument(str(TEMPLATE));doc.init_forms();page=doc[info['page']-1];bitmap=page.render(scale=2,may_draw_forms=True)
            self.assertEqual(crop.tobytes(),bitmap.to_pil().crop(box).tobytes())
            bitmap.close();page.close();doc.close()
        f=info['field_rect'];c=info['crop_rect']
        self.assertLessEqual(c[0],f[0]);self.assertLessEqual(c[1],f[1]);self.assertGreaterEqual(c[2],f[2]);self.assertGreaterEqual(c[3],f[3])

if __name__=='__main__':unittest.main()
