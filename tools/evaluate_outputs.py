#!/usr/bin/env python3
"""Reviewer-only scoring of saved PDF outputs. Never package with the runtime skill.
Compares supplied expected values using independent template destinations. Conflict
interpretation remains a human review item; never count keyword presence as proof.
"""
import argparse
import json
import re
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def fid(page, name): return f'F[0].P{page}[0].{name}_A[0]'
MAPPING={
 'applicant.name':fid(1,'NamedInsured_FullName'),
 'applicant.mailing_address.line1':fid(1,'NamedInsured_MailingAddress_LineOne'),
 'applicant.mailing_address.city':fid(1,'NamedInsured_MailingAddress_CityName'),
 'applicant.mailing_address.state':fid(1,'NamedInsured_MailingAddress_StateOrProvinceCode'),
 'applicant.mailing_address.postal_code':fid(1,'NamedInsured_MailingAddress_PostalCode'),
 'applicant.business_phone':fid(1,'NamedInsured_Primary_PhoneNumber'),
 'applicant.nature_of_business':fid(2,'CommercialPolicy_OperationsDescription'),
 'policy.proposed_effective_date':fid(1,'Policy_EffectiveDate'),
 'policy.proposed_expiration_date':fid(1,'Policy_ExpirationDate'),
 'prior_coverage.umbrella.premium':fid(3,'PriorCoverage_OtherLine_TotalPremiumAmount'),
}
for label,suffix in [('carrier','InsurerFullName'),('policy_number','PolicyNumberIdentifier'),('effective_date','EffectiveDate'),('expiration_date','ExpirationDate'),('premium','TotalPremiumAmount')]:
 MAPPING['prior_coverage.general_liability.'+label]=fid(3,'PriorCoverage_GeneralLiability_'+suffix)
LEGAL={
 'Limited Liability Company':fid(1,'NamedInsured_LegalEntity_LimitedLiabilityCorporationIndicator'),
 'Corporation':fid(1,'NamedInsured_LegalEntity_CorporationIndicator'),
}
REQUEST_CHECKBOXES={
 'transaction_status':{'QUOTE':fid(1,'Policy_Status_QuoteIndicator')},
 'requested_lines_of_business':{'Commercial General Liability':fid(1,'Policy_LineOfBusiness_CommercialGeneralLiability')},
}
BLANK_PATTERNS={
 'agency name and contact fields':r'\.Producer_',
 'proposed carrier and proposed policy number':r'P1\[0\]\.(Insurer_|Policy_PolicyNumber)',
 'FEIN':r'TaxIdentifier', 'SIC':r'SICCode','NAICS':r'NAICSCode','website':r'WebsiteAddress',
 'date business started':r'BusinessStart|BusinessEstablished|BusinessInception',
 'employee counts':r'(FullTime|PartTime)EmployeeCount', 'annual revenue':r'AnnualRevenueAmount',
 'requested premium':r'P1\[0\].*PremiumAmount', 'loss history':r'LossHistory_',
 'unsupported general-information answers':r'CommercialPolicy_Question_',
 'applicant and producer signatures':r'Signature|Initials',
 'applicant.legal_entity':r'NamedInsured_LegalEntity_',
}

def canonical(value):
 s=str(value or '').lower().replace('&','and')
 s=re.sub(r'\bstreet\b','st',s);s=re.sub(r'\broad\b','rd',s)
 return re.sub(r'[^a-z0-9]','',s)

def evaluate(case, revision):
 packet=json.loads((revision/'packet.json').read_text())
 fields=PdfReader(revision/'acord-125-draft.pdf').get_fields() or {}
 values={k:str(v.get('/V','')) for k,v in fields.items()}
 checks=[]
 for expected in case['supported_values']:
  key,value=expected['field'],expected['value']
  target=LEGAL.get(value) if key=='applicant.legal_entity' else MAPPING.get(key)
  expected_pdf='/1' if key=='applicant.legal_entity' else value
  actual=values.get(target,'')
  status='pass' if target and canonical(actual)==canonical(expected_pdf) else 'review'
  checks.append({'field':key,'pdf_field':target,'expected':expected_pdf,'actual':actual,'status':status})
 blank_checks=[]
 oracle=json.loads((ROOT/'sample input data/_evaluation/expected_results.json').read_text())
 global_blanks=oracle['common_fields_that_must_remain_blank']
 for category in global_blanks+case['case_specific_blanks']:
  pattern=BLANK_PATTERNS.get(category)
  targets=[k for k in values if pattern and re.search(pattern,k)] if pattern else [MAPPING[category]] if category in MAPPING else []
  violations={k:values[k] for k in targets if values.get(k,'') not in ('','/Off')}
  blank_checks.append({'category':category,'fields_checked':len(targets),'violations':violations,
                       'status':'fail' if violations else 'pass' if targets else 'review'})
 request_checks=[]
 for key,mapping in REQUEST_CHECKBOXES.items():
  requested=oracle['common_requested_application'][key]
  for value in requested if isinstance(requested,list) else [requested]:
   target=mapping.get(value)
   request_checks.append({'request':value,'pdf_field':target,'actual':values.get(target,''),
                          'status':'pass' if target and values.get(target)=='/1' else 'review'})
 conflict_records=[a for a in packet['assignments'] if a['status']=='conflict']+packet['issues']
 return {'case':case['id'],'expected_value_checks':checks,'blank_checks':blank_checks,
         'request_checkbox_checks':request_checks,
         'value_pass_count':sum(c['status']=='pass' for c in checks),'value_total':len(checks),
         'expected_conflicts':case['conflicts'],'observed_exception_records':conflict_records,
         'conflict_review':'Human must compare expected conflicts against observed records and blank PDF destinations.',
         'limitations':'Ground truth is a partial expected set. Extra supported fields, paraphrases, and conflict semantics need human review. Matching strings do not prove source accuracy.'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--case',required=True);p.add_argument('--revision-dir',type=Path,required=True);p.add_argument('--out',type=Path)
 a=p.parse_args()
 gt=json.loads((ROOT/'sample input data/_evaluation/expected_results.json').read_text())
 case=next(c for c in gt['cases'] if c['id']==a.case)
 result=evaluate(case,a.revision_dir)
 text=json.dumps(result,indent=2)
 if a.out: a.out.write_text(text+'\n')
 else:print(text)
