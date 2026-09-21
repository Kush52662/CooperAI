# Sample input data

Source-backed development and demo data for the Cooper AI ACORD 125 form-filler MVP. The package contains four cases: one consistent walkthrough and three realistic challenge cases. It is **not** the 20-case pilot evaluation set proposed in `docs/CALL_BRIEF.md`.

## How to use it

Upload only the three files inside one numbered case folder:

1. `ams360_customer_policy_export.csv` - one-row AMS360-style customer/policy export.
2. `insurance_document.pdf` - public insurance evidence for the same account.
3. `submission_request.json` - the requested transaction, line of business, and proposed application period.

Use `output_template/acord_125_blank_fillable.pdf` as the output form. Never upload `_evaluation/`; it contains reviewer-only expected answers.

The proposed application period is **10/01/2026-10/01/2027**. Historical dates in the CSV and PDF describe prior/current coverage and must not populate the proposed-period fields.

## Cases

| Folder | Purpose | Expected behavior |
|---|---|---|
| `00_clean_walkthrough` | Declaration-only, internally consistent first demo. | Fill supported applicant and prior-coverage values without conflicts. |
| `01_lawn_and_order_mowing` | Certificate, declarations, and a problematic PDF text layer. | Flag the 09/20 versus 12/20 policy-period conflict and the rendered-page/text-layer discrepancy. |
| `02_watson_contracting` | Same entity with conflicting street addresses and policy-number representations. | Preserve both sources and require human review. Treat $11,388 as umbrella-specific. |
| `03_tarheel_paving` | Sparse certificate plus legal-name variation. | Flag the company-name difference and leave unsupported fields blank. |

## Data classification

The PDFs and account facts come from public government records. The CSVs are normalized, source-backed AMS360-style exports; they are not exports from a live AMS360 tenant and are not AI-generated businesses. Their 27 headers are a practical subset of Vertafore's documented **Customer Policy Information** export fields. Unsupported values remain blank. FEINs and signatures are excluded.

The three challenge PDFs include ACORD 25 certificates as supporting insurance documents. That is deliberate: ACORD 25 is an input artifact containing coverage evidence, while ACORD 125 is the blank output application. The clean walkthrough excludes the certificate and uses declaration pages only.

## Provenance

Sources last verified **2026-09-21**.

### 00 and 01 - Lawn & Order Mowing LLC

- Insurance source: NCDOT contract `DN12196005`: <https://connect.ncdot.gov/letting/Division%2014%20Letting/09%2009%202025/DN12196005%20CONTRACT.pdf>
- Account source: TDOT prequalified contractor listing, vendor `1000003093`: <https://www.tn.gov/content/dam/tn/tdot/construction/prequal.pdf>
- `00` uses source pages 54, 55, and 67. `01` uses source pages 53-56 and 67.

### 02 - Watson Contracting Inc

- Insurance source: NCDOT contract `DN01046`, source pages 84-85: <https://connect.ncdot.gov/letting/Division%2014%20Letting/02%2013%202024/DN01046%20CONTRACT.pdf>
- Account source: FMCSA SAFER snapshot, USDOT `2464881`: <https://safer.fmcsa.dot.gov/query.asp?original_query_param=NAME&original_query_string=WATSON+CONTRACTING+INC&query_param=USDOT&query_string=2464881&query_type=queryCarrierSnapshot&searchtype=ANY>

### 03 - Tarheel Paving & Asphalt Company Inc.

- Insurance source: NCDOT contract `DN01066`, source page 105: <https://connect.ncdot.gov/letting/Division%2014%20Letting/01%2014%202025/DN01066%20CONTRACT.pdf>
- Account source: NCDOT award notice `DN01066`: <https://connect.ncdot.gov/letting/Division%2014%20Letting/01%2014%202025/DN01066%20-%20A.pdf>

### Output template

- Blank fillable ACORD 125, edition 2016/03: <https://sortspoke.com/hubfs/theme/acord-125-form/acord-125-blank-fillable.pdf>

## Evaluation boundary

The exact supported values, page references, conflicts, and required blanks are documented in `_evaluation/expected_results.json`. Four cases are enough for development and a live demo. A credible pilot claim still requires the planned 20-case evaluation with broader document quality, business types, and failure modes.
