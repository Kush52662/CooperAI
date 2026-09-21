# ACORD 125 interpretation guidance

Support the bundled 2016/03 edition only. Its 556 field-tree entries include five structural nodes and 551 writable-type fields (387 text, 164 buttons). Use inspection output for actual field IDs and checkbox export values; no positional guesses.

## Source and role distinctions

- Read the insured's own data into applicant fields. A certificate's producer/contact/phone is the historical issuing agency, not automatically the agency preparing the new application. A certificate holder is not the applicant.
- Use the CSV submission columns (or legacy submission_request.json) for proposed effective/expiration dates, transaction status, and requested lines. Existing-policy carriers, policy numbers, premiums, and dates belong in appropriate prior-coverage fields, not the new proposed policy block.
- Prior GL, auto, property, and other lines have separate columns. Keep values tied to their exact line and policy period. Umbrella may use the prior-coverage Other column with its line label; it is not GL. Do not sum premiums across unrelated coverages.
- Do not assume an existing limit is a requested limit, or check every coverage appearing on a certificate as requested coverage.
- Named-insured mailing address is not automatically a premises address. A location schedule can independently support premises. Do not infer occupancy, ownership, revenue, employee count, years in business, or building details from an address or business name.
- A certificate is evidence of the coverage values it lists, not a complete policy or an application. Preserve contradictions with declarations; do not invent endorsements that explain them.

## Mapping behavior

Read the actual field tooltip. For example, a proposed policy number and a prior GL policy number are different fields even if both contain `PolicyNumber` in their names. The agent proposes mappings; the script checks IDs and types, not their semantic correctness.

- Normalize case, whitespace, ordinary address abbreviations, and punctuation only when meaning is preserved. ZIP and matching ZIP+4 are compatible; retain the specific source and record the normalization.
- Different street numbers, changed legal-name words, different policy-number suffixes, and different dates are not mere formatting. Preserve both values and leave the affected field blank pending resolution.
- Obtain legal entity from explicit source statements. Do not infer it solely from an Inc./LLC suffix if other sources are incomplete or inconsistent.
- Business description may be a faithful concise paraphrase; codes such as NAICS/SIC must be explicitly supported. An insurance classification code is not automatically NAICS.
- If only part of a description is disputed, retain the independently supported description and put the disputed project details in the exception list. Do not silently incorporate the visible alternative merely because an overlay is readable.
- Preserve scope: a payroll exposure amount is not revenue; a line premium is not a combined package premium; historical information is not a new proposal.
- Unsupported general-information questions remain unanswered. Missing evidence of losses is not evidence of no losses. Never auto-check No for unanswered questions.
- Leave initials, signatures, and signature dates blank. Do not copy a historical signature or create a new one. The current date is not automatically a user-authorized signing date.

## Draft completeness

Useful categories to check: applicant identity and address, contact, explicitly supported legal entity, business description, documented premises, requested transaction/lines/period, and prior coverages. Unsupported sections stay blank and are summarized in review issues. Do not force data into a field merely to increase coverage.

Inspect image and embedded-text evidence together. If a PDF overlay displays one value while extracted text includes older hidden values, flag the discrepancy and preserve page/channel provenance. A readable text layer is not proof it represents the visible page.
