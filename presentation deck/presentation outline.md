# Presentation Outline

Cooper AI · ACORD 125 Form-Filler · Sales Engineer Take-Home

| # | Slide title | Content |
|---|---|---|
| 1 | **Commercial Insurance Application Automation** | ACORD 125 form-filler · Sales Engineer take-home · Kushal Murthy. Reuse the existing cover. |
| 2 | **Account Context** | Sterling Cooper’s profile: 100 employees, 30 commercial-lines staff, five offices, AMS360. Current workflow and source documents. |
| 3 | **Call Brief** | All **10 questions and assumed answers**, grouped into the four discovery sections: current state; problem and impact; future state and requirements; decision and evaluation. Use concise one-line Q&As in a four-section layout. |
| 4 | **Problem – Opportunity – Wedge** | **Problem:** repetitive entry across application packages. **Opportunity:** assumed 30-minute baseline versus five-minute target. **Wedge:** ACORD 125 first. Clearly label assumptions and targets. |
| 5 | **MVP Scope** | Supported inputs, draft PDF output, review and revision flow. What we included, deferred, and cut within the assignment’s timebox. |
| 6 | **Architecture Decisions** | Options considered and why we selected a Claude skill with Python tools. Explain AI-controlled interpretation and mapping, tool-based execution, and conversational review. |
| 7 | **System Architecture** | Inputs → skill-guided AI → sourced field assignments → validation → PDF filling → verification. Show the user correction loop. |
| 8 | **Skill Design and AI Usage** | `SKILL.md`, form-specific guidance, Python tools, and evidence records. Explain where AI operates in the product and how AI assisted development. |
| 9 | **Live Demonstration** | Clean case → filled draft. Conflict case → flagged exceptions. User correction → revised PDF. |
| 10 | **Testing and Results** | Four development cases, actual outcomes, processing time, field accuracy, conflict detection, and limitations. Separate tool tests from agent evaluations. |
| 11 | **Scalability and Extensibility** | How we add forms, insurance lines, and carrier supplements. What is reused versus what requires new guidance, data, mappings, and tests. |
| 12 | **Customer Deployment and Next Steps** | Proposed pilot with two users in one office, data-access approval, baseline measurement, 20-case evaluation, handoff package, and expansion criteria. |

## Content references

- Account context: [account_profile.md](../docs/account_profile.md)
- Discovery questions and assumptions: [CALL_BRIEF.md](../docs/CALL_BRIEF.md)
- Sample data and evaluation boundaries: [sample input data/README.md](../sample%20input%20data/README.md)
- Visual style: [design.md](design.md)

## Evidence rules

- Present the 30-minute manual baseline and five-minute processing target as assumptions and targets, not measured results. Track human review separately.
- Populate Testing and Results from completed runs. Do not infer agent accuracy from passing Python tests.
- Distinguish the four development cases from the proposed 20-case pilot evaluation.
- Describe implemented capabilities from the completed build; label future deployment and expansion work as proposed.
