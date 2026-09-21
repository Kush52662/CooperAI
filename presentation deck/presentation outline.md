# Presentation Outline

Cooper AI · ACORD 125 Form-Filler · Sales Engineer Take-Home

| # | Slide title | Content |
|---|---|---|
| 1 | **Case study and demo presentation** | ACORD 125 form-filler. Kushal Murthy, Sales Engineer take-home. Photographic cover. |
| 2 | **Pre-call account context** | Hypothetical Sterling Cooper: 100 employees, 30 commercial-lines staff, five offices, AMS360. Profile facts only: core users, primary documents, distributed servicing and repetitive entry with missing or conflicting information. Weekly volume and timing belong to discovery, not pre-call knowledge. |
| 3 | **Call Brief: Current State and Impact** | Questions 1–5 establish form variation, source reconciliation, weekly volume, ACORD 125 prevalence, where entry time is spent, and the operational consequence of exceptions. Each section ends with the resulting scope decision. |
| 4 | **Call Brief: Requirements and Evaluation** | Questions 6–10 establish the outcome target, evidence and decision ownership, exact output and handoff, pilot participants, data approval, and measurable success criteria. Each section ends with the resulting scope decision. |
| 5 | **Problem – Opportunity – Wedge** | Repeated entry and reconciliation. Assumed 30-minute baseline versus five-minute target: 25 minutes or 83.3% potential reduction. At 75% of 120–150 weekly packages, this represents 162–203 CSR hours or $5.7K–$7.1K monthly capacity at an assumed $35 loaded hourly cost. Wedge: ACORD 125 first, then a proposed pilot with two AMs/CSRs, one office, 20 synthetic cases, operations support, and IT approval. Review effort remains separate. |
| 6 | **MVP Scope** | Required CSV + insurance PDF, one account and one ACORD 125 edition. Editable unsigned draft, sources, focused questions, previews, and revision history. Explain cuts: other forms, low-quality scans and handwriting, AMS write-back, submission, production rollout, multiple accounts and arbitrary templates. Tie the boundary to discovery and the assignment timebox without claiming measured build duration. |
| 7 | **Architecture Decisions** | Compare a standalone AI workflow app, a host skill with Python tools, and model-generated filling scripts. Explain the chosen skill: host reasoning and interaction, structured sourced assignments, reusable validated PDF operations. Describe tradeoffs, including host dependence and acceptance checks. |
| 8 | **System Architecture** | CSV + insurance PDF → multimodal reading → fact extraction → ACORD 125 field mapping → deterministic Python validation and filling → AI visual QA → draft PDF with unresolved questions. Keep the diagram focused on the first draft; slide 10 explains the correction loop. |
| 9 | **Skill Design and AI Usage** | SKILL.md, form guidance, packet contract, runtime/interaction references, Python tools. AI interprets and maps evidence; tools enforce execution constraints. Distinguish runtime AI from AI assistance during development. |
| 10 | **Review and Exception Handling** | A concrete conflicting-field example: show both source alternatives, leave the draft field blank, ask a focused question, record an explicit reply, stage/apply corrections, generate and inspect a new revision. Explain missing versus conflicting values, skipped questions, retained source issues, and preserved history. Label fictional interaction fixtures. |
| 11 | **Live Demonstration** | Audience-facing product workflow: draft preparation from CSV/PDF, account-manager exception review, and confirmed corrections with preserved revision history. Takeaway: a sourced draft with the account manager in control. Actual demo actions remain presenter preparation, not slide copy. |
| 12 | **Testing and Results** | Current recorded evidence: 30 Python tests; three development cases; 33/33 expected-value comparisons, 42/42 blank-category checks, and 6/6 requested checkboxes. All 12 output pages inspected. Show automated, model, and visual evidence separately. These are partial checks, not overall field accuracy. |
| 13 | **Evaluation and Acceptance** | Development runs used existing context; independent evaluation remains pending. Multiple-choice correction was demonstrated in Codex using a fictional account; typed answers, skipped questions and Claude execution still need validation. Proposed acceptance: 20 representative synthetic cases, validate the manual baseline, average entry ≤5 minutes, measure review/correction effort separately, and check unsupported values stay blank. Do not invent an agreed accuracy threshold. |
| 14 | **Scalability and Extensibility** | The form registry selects the template, interpretation reference, output name, and form-specific field markers. More forms add one registry entry, a fillable asset, focused guidance, and evaluation cases while reusing the packet, PDF tools, correction loop, and verification workflow. More lines add interpretation rules; carrier supplements follow the same boundary. No automatic support claim. |
| 15 | **Deployment and Next Steps** | Complete fresh host and native-interaction acceptance, package the current skill, then propose two users in one office with an operations lead. Confirm data handling before customer files, run the pilot, and expand only after evaluating outcomes. Runnable packaging and customer rollout remain proposed next steps. |

## Discovery slide content

Retain all ten questions. Use concise Q&A pairs with the question prominent and the assumed answer directly below. All answers must be labeled simulated assumptions. Decisions appear once per section, not once per question.

### Slide 3: Current State and Impact

**Current state**

1. **Which forms typically go into a submission package?** ACORD 125, 126 and 140, plus account-specific applications.
2. **Where does the information come from, and what still needs manual work?** AMS360, policy PDFs, prior applications and producer notes. Staff find and enter remaining details.
3. **What is the weekly package volume, and which form appears most often?** Approximately 120–150 across five offices, with multiple forms per package. ACORD 125 appears in about 75%.

**Section decision:** Start with ACORD 125 and CSV/PDF inputs. Count packages separately from forms; verify eligible ACORD 125 volume before estimating total savings.

**Problem and impact**

4. **For ACORD 125, where is time spent before review?** About 30 minutes switching between records, documents and form fields.
5. **Which exceptions create rework, and what happens next?** Conflicting addresses, outdated details and missing answers trigger source checks or producer follow-up.

**Section decision:** Treat 30 minutes as an assumed baseline to validate. Surface gaps and conflicts, and measure review/correction effort separately.

### Slide 4: Requirements and Evaluation

**Future state and requirements**

6. **What improvement would make this worthwhile?** Five-minute entry instead of 30, leaving more time for review.
7. **When sources disagree or data is missing, who decides?** The account manager checks evidence and asks the producer or insured; every proposed value needs traceable support.
8. **What must the output contain, and who owns the handoff?** An editable ACORD 125 PDF, source references and open questions. The account manager reviews it before package assembly.

**Section decision:** Produce a sourced, editable draft and focused review questions. Keep AMS updates, package assembly and carrier submission outside scope.

**Decision and evaluation**

9. **Who should test it, and who approves customer-data use?** Two AMs/CSRs and operations test it; IT approves data handling.
10. **What must a successful trial prove?** Across 20 representative cases: average entry of five minutes or less, unsupported fields stay blank, and correction effort does not increase.

**Section decision:** Propose a 20-case synthetic evaluation before a live pilot. Validate the baseline and measure processing, human review, corrections and accuracy separately.

## Narrative and presentation guidance

- Slides 2–6 establish the customer context, discovery reasoning, and resulting scope before architecture.
- The three added slides come from splitting discovery, separating the review workflow from architecture, and separating evaluation limits from results.
- Slide 10 demonstrates reviewer control and evidence handling; slide 11 proves the workflow with a demo.
- Use the common content-slide header master. Five Q&As per discovery slide leave space for section decisions and readable type.

## Current product and slide status

Updated against README.md, SKILL.md, and SKILL_WORKFLOW_VALIDATION.md on 21 September 2026. The current product is the improved conversational skill on the v1 architecture, not the Streamlit spike or the unchanged historical v1.0.0 snapshot.

All 15 slides are complete as numbered PNGs in `cooperai-images/`. Open `cooperai-images/index.html` for the image slideshow. Slides 3–4 split the call brief into five Q&As each with section decisions. Slides 5–15 use the updated numbering. The demo slide is a presentation sequence, not a screenshot of an executed demo. Image-generated typography remains approximate.

## Content references

- Account context: [account_profile.md](../docs/account_profile.md)
- Discovery questions and assumptions: [CALL_BRIEF.md](../docs/CALL_BRIEF.md)
- Sample data and evaluation boundaries: [sample input data/README.md](../sample%20input%20data/README.md)
- Current product: [README.md](../README.md)
- Current validation: [SKILL_WORKFLOW_VALIDATION.md](../docs/SKILL_WORKFLOW_VALIDATION.md)
- Skill: [SKILL.md](../skills/acord-form-filler/SKILL.md)
- Visual style: [design.md](design.md)

## Evidence rules

- Present the 30-minute manual baseline and five-minute processing target as assumptions and targets, not measured results. Track human review separately.
- Populate Testing and Results from completed runs. Do not infer agent accuracy from passing Python tests.
- Distinguish the three development cases from the proposed 20-case pilot evaluation.
- Describe implemented capabilities from the completed build; label future deployment and expansion work as proposed.

- Use the current 33/33 development result only with its warm-context and partial-oracle limitations. Historical figures describe earlier workflows.
- Native multiple-choice correction was tested on a fictional fixture. Do not generalize it to completed Claude, free-text, or skip acceptance.
- Current inputs are exactly one CSV and one insurance PDF. Request JSON is not part of the current workflow.

## Image title treatment

Discovery slides use the shared title “Call Brief”, with “Current State and Impact” and “Requirements and Evaluation” in the eyebrow. Full section names remain in the outline. This preserves the common title size and placement.

## Audience-copy review — 21 September 2026

All 15 images reviewed. Slides 5, 6, 8, 10, 12, 13 and 15 revised after the slide 11 cleanup. Presenter commands are replaced with product behavior. Internal delivery commentary is removed from the scope slide. Testing limitations use plain language. Savings remain potential; test counts remain limited to the recorded development checks. Packaging appears as a future handoff step.
