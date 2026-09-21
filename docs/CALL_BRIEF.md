# Sterling Cooper Risk Advisors — Discovery Call Brief

**Account reference:** [account_profile.md](account_profile.md). Sterling Cooper is a hypothetical mid-market commercial P&C brokerage with 100 employees, 30 commercial-lines staff, five offices, and AMS360.

**Evidence boundary:** The answers and operational numbers below are simulated build assumptions, not verified customer findings. The AMS360 answer describes an assumed customer workflow, not a general product limitation. Time savings are targets, not achieved results.

## 1. Current state

**1. “Which forms are required, and how does that vary by account or carrier?”**  
**Assumed answer:** “ACORD 125, 126 for general liability, and 140 for property are typical. Account and carrier requirements add other applications, while common account information repeats across forms.”

**2. “Which sources are used, and what work remains manual?”**  
**Assumed answer:** “We use AMS360 records, policy PDFs, prior applications, and producer notes. Staff reconcile differences across those sources and enter missing details into the form.”

**3. “What is the weekly package volume, and which form appears most often?”**  
**Assumed answer:** “Approximately 120–150 packages across our five offices. Each contains multiple forms. ACORD 125 is our most-used form, appearing in about 75% of packages.”

**Decision:** Prioritize ACORD 125 because it is assumed to be the most-used form, appearing in 75% of weekly packages. Build a multimodal form-filler accepting CSV exports and legible policy PDFs. Other forms and input formats remain outside the initial scope. The 75% measures packages containing ACORD 125, not its share of all individual forms.

## 2. Problem and impact

**4. “For ACORD 125, where is time spent before review?”**  
**Assumed answer:** “About 30 minutes per form, switching between account records, supporting documents, and individual form fields.”

**5. “Which exceptions create rework, and what happens next?”**  
**Assumed answer:** “Conflicting addresses, outdated business details, and missing answers trigger source checks or producer follow-up. The package waits until someone resolves the exception.”

**Decision:** Use 30 minutes per ACORD 125 as the assumed manual data-entry baseline. Measure review and correction time separately, and make missing or conflicting information visible rather than silently filling it.

## 3. Future state and requirements

**6. “What outcome would make automation worthwhile?”**  
**Assumed answer:** “If the ACORD 125 data entry took five minutes instead of 30, we could spend more time checking the application and progressing submissions.”

**7. “When sources disagree or data is missing, who decides?”**  
**Assumed answer:** “An account manager checks the evidence and asks the producer or insured when necessary. Every proposed value needs traceable source support.”

**8. “What must the output contain, and who owns the handoff?”**  
**Assumed answer:** “An editable ACORD 125 PDF, source references, and open questions. An account manager reviews it before package assembly.”

**Decision:** Target five minutes for automated data entry, with source references and unresolved fields flagged for human review. Export a filled ACORD 125 PDF; AMS updates, package assembly, and carrier submission remain manual.

## 4. Decision and evaluation

**9. “Who should test it, and who approves customer-data use?”**  
**Assumed answer:** “Two account managers or CSRs and an operations lead test it. IT approves data handling before customer files enter the workflow.”

**10. “What must a successful trial prove?”**  
**Assumed answer:** “Across 20 representative cases, average entry is five minutes or less, unsupported fields remain blank, and correction effort does not increase. Include incomplete and conflicting documents.”

**Decision:** Evaluate 20 synthetic cases with two users from one office. Measure processing time, human review, corrections, and field accuracy separately. Validate the manual baseline and obtain approval for customer data before a live pilot.

## Potential impact

Reducing data entry from 30 to five minutes would save **25 minutes per eligible ACORD 125—an 83.3% reduction in that step**. At the assumed 75% inclusion rate across 120–150 weekly packages, the gross potential is **approximately 37.5–46.9 hours weekly, or 162–203 CSR hours monthly**, before additional review. At an assumed **$35 loaded CSR cost per hour**, that represents **approximately $5.7K–$7.1K in monthly staff capacity**. The estimate assumes 4.33 weeks per month and one eligible ACORD 125 per included package. Supported template and input eligibility still require validation. Changes in review and correction effort determine the net benefit. These are scenario estimates, not measured results.

## End-of-call brief — 100 words

Sterling Cooper is assumed to prepare 120–150 submission packages weekly across five offices. ACORD 125 is the most-used form, appearing in 75% of packages, making it our initial focus. Staff gather information from AMS360, policy documents, prior applications, and producer notes. The MVP uses CSV exports and policy PDFs to produce a reviewable ACORD 125. Manual entry is assumed to take 30 minutes; the target is five minutes before review. Missing answers and conflicts remain visible. Two users will evaluate 20 synthetic cases for processing time, review effort, corrections, and accuracy. Customer data use requires approval before any live pilot.
