# Conversational skill validation

Implemented on `codex/skill-workflow-improvements`; the `v1.0.0` tag and Streamlit spike branch remain unchanged. No external model API, service, deployment, or ZIP was used.

## Automated validation

30 Python tests pass: the 16 baseline tests plus 14 behavioral tests for strict two-file inputs, required CSV submission columns, staged batch isolation, new assignments, explicit clearing (including the last populated field), invalid and tampered batches, stale/wrong-run detection, field-bound confirmation history, review differences, and crop geometry/pixels. Skill frontmatter validation also passes.

Run:

```sh
.venv/bin/python -m unittest discover -s tests -q
```

The template contains XFA metadata. PDFium warns that its build cannot render XFA when previewing the original; the tested template also contains AcroForm widgets. Generated copies remove XFA. Preview pixels were checked against the AcroForm rendering, and a generated-field crop was visually inspected.

## Three-case development walkthrough

The active Codex agent read only each case's CSV/PDF as account evidence, inspected all 6 rendered source pages, authored assignments, and generated drafts with the skill tools. Reviewer ground truth was read by the evaluator only after the drafts were produced. This was a warm-context development walkthrough, not a fresh independent/blinded model evaluation or a pilot.

Generated walkthrough artifacts were intentionally excluded from version control because they are reproducible run outputs. A one-off mapping script in the ignored output directory recorded the agent's source-based decisions; it is not part of runtime extraction.

| Case | Expected values | Blank-category checks | Requested checkboxes | Material conflicts retained |
|---|---:|---:|---:|---|
| Clean | 15/15 | 13/13 | 2/2 | None |
| Watson | 9/9 | 13/13 | 2/2 | Street address; GL and auto policy suffixes |
| Tarheel | 9/9 | 16/16 | 2/2 | Legal name; entity/phone remain unsupported |

Total: 33 expected values, 42 blank-category checks, and 6 requested checkboxes pass. These are partial oracle checks, not a percentage of all ACORD fields or proof of every semantic mapping. The expected conflict records were separately compared with source alternatives and blank PDF destinations. Additional source questions remain in the review reports.

All 12 output pages were visually inspected: populated values remain within fields, requested checkboxes render correctly, unresolved values remain blank, and signature/unsupported-answer areas remain blank. Long carrier names use small auto-sized text. Visual results were explicitly recorded after inspection.

## Native host interaction

A separate fictional fixture under `output/skill-workflow-validation/native-qa/` prevents interaction testing from changing any real sample run.

- Codex asynchronous multiple-choice Q&A: observed. User selected `09/20/2025 — CSV`; staged/applied correction created revision 2 with the exact response in history and both source alternatives preserved. PDF readback passed, all four pages were visually inspected, and the selected expiration is visible in the generated crop.
- Resume after the asynchronous reply: observed; the correct fixture packet was continued.
- Native free-text addition: a fictional phone-number question was presented but received no answer during validation. Backend addition behavior is covered by automated tests.
- Native skip/dismiss: not yet exercised with an actual user response. Instructions leave unanswered questions unresolved; no response is fabricated.
- Claude chat / Claude Code: not run in this environment. Native tool availability and fresh installation remain separate acceptance checks.

## Boundaries

Proposed-date changes still require corrected source inputs and a new run. Corrections in one run execute sequentially. Source quotes and semantic mappings require agent review; JSON validation and readback do not establish factual correctness. Retained source issues are reported separately from resolved field conflicts.
