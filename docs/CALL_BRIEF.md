# Sterling Cooper Risk Advisors — Discovery Call Brief

**Account reference:** [account_profile.md](account_profile.md). Sterling Cooper is a hypothetical mid-market commercial P&C brokerage with 100 employees, 30 commercial-lines staff, five offices, and AMS360.

**Evidence boundary:** The answers and operational numbers below are simulated build assumptions, not verified customer findings. The AMS360 answer describes an assumed customer workflow, not a general product limitation. Time savings are targets, not achieved results.

## 1. Current state

**1. “Which forms typically go into a submission package?”**  
**Assumed answer:** “Usually ACORD 125, 126 for general liability, and 140 for property, plus additional applications depending on the account. We repeat account information across several forms.”

**2. “Where does the information come from, and what still needs manual work?”**  
**Assumed answer:** “We use AMS360 records, policy PDFs, prior applications, and producer notes. Information in those documents does not always make it into the structured record, so staff find and enter the remaining details manually.”

**3. “How many submission packages does your team prepare in a typical week?”**  
**Assumed answer:** “Approximately 120–150 packages across our five offices. Each package contains multiple forms.”

**Decision:** Build a form-filler agent for ACORD 125 first, accepting CSV exports and text-based policy PDFs. Other forms and input formats remain outside the initial scope. Count packages and individual forms separately.

## 2. Problem and impact

**4. “For the ACORD 125 alone, how much time goes into entering information before review?”**  
**Assumed answer:** “About 30 minutes per form, switching between account records and supporting documents.”

**5. “What causes the most rework or delays?”**  
**Assumed answer:** “Different addresses, outdated business details, and missing answers. Staff reopen documents or contact the producer, and the package waits until someone resolves it.”

**Decision:** Use 30 minutes per ACORD 125 as the assumed manual data-entry baseline. Measure review and correction time separately, and make missing or conflicting information visible rather than silently filling it.

## 3. Future state and requirements

**6. “What improvement would make this worthwhile for your team?”**  
**Assumed answer:** “If the ACORD 125 data entry took five minutes instead of 30, we could spend more time checking the application and progressing submissions.”

**7. “How do you decide what to enter when documents disagree or an answer is missing?”**  
**Assumed answer:** “An account manager checks the documents and asks the producer or insured when necessary. We need to see where a value came from.”

**8. “Who checks the completed application, and how is it handed off?”**  
**Assumed answer:** “An account manager reviews the PDF before it joins the submission package.”

**Decision:** Target five minutes for automated data entry, with source references and unresolved fields flagged for human review. Export a filled ACORD 125 PDF; AMS updates, package assembly, and carrier submission remain manual.

## 4. Decision and evaluation

**9. “Who should test this before we consider a wider rollout?”**  
**Assumed answer:** “Two account managers or CSRs from one office, supported by our operations lead. IT needs to review data handling before we use customer files.”

**10. “What would the trial need to demonstrate for you to continue?”**  
**Assumed answer:** “Show that it handles 20 representative test cases, averages five minutes or less for data entry, and does not create more correction work. Include incomplete and conflicting documents.”

**Decision:** Evaluate 20 synthetic cases with two users from one office. Measure processing time, human review, corrections, and field accuracy separately. Validate the manual baseline and obtain approval for customer data before a live pilot.

## Potential impact

Reducing data entry from 30 to five minutes saves **25 minutes per eligible form—an 83.3% reduction in that step**. If all 120–150 weekly packages contain an eligible ACORD 125, the gross potential is **50–62.5 hours weekly before additional review**. Actual eligibility and changes in review effort determine the net benefit; this is not a measured result.

## End-of-call brief — 100 words

Sterling Cooper is assumed to prepare 120–150 submission packages weekly across five offices, commonly combining ACORD 125, 126, and 140. Staff gather information from AMS360, policy documents, prior applications, and producer notes, then manually complete missing details. Our MVP targets ACORD 125, using CSV exports and policy PDFs to produce a filled, reviewable form. We assume 30 minutes of manual entry and target five minutes before human review. Missing answers and conflicting values require attention. Two users will evaluate 20 synthetic cases, measuring processing time, review effort, and accuracy. Broader form support follows validation and approval for customer data use.
