# Implementation and verification — 21 September 2026

Implemented a portable `acord-form-filler` skill with Python tools. The active host model interprets documents and selects real ACORD field IDs; Python validates the assignment packet, generates an editable draft, renders it, and checks field readback. There is no separate model API, web app, or account-specific extraction code.

## Delivered

- [Installable skill ZIP](../dist/acord-form-filler.zip)
- [Four-case demo inputs ZIP](../dist/demo-inputs.zip), separate from the skill and answer key
- [Skill instructions](../skills/acord-form-filler/SKILL.md), reference guidance, schema, pinned dependencies, and bundled ACORD 125 (2016/03)
- [Python tools](../skills/acord-form-filler/scripts/form_tool.py), [tests](../tests/test_form_tool.py), and [reviewer-only evaluator](../tools/evaluate_outputs.py)
- [Write-up and setup](../README.md) and [onsite demo sequence](DEMO_TALK_TRACK.md)

The source template's 556 field-tree entries contain five structural nodes and **551 actual fields**: 387 text fields and 164 buttons. Technical verification checks all 551 fields, not just populated ones. Original sample inputs and the original template were not edited.

## Automated checks

**16 tests pass** using the bundled template. Coverage includes unknown/duplicate fields, source hashes, exact CSV evidence, invalid PDF page references, unresolved conflicts, checkbox states, proposed versus historical dates, signatures, missing user evidence, PDF readback and tampering, revision overwrite prevention, missing values, full carrier appearance sizing, and user-correction history plus PDF regeneration. Correction data in that test is explicitly fictional.

The skill-creator structural validator passes. Local dependency checks pass with Python 3.12, pypdf 6.10.0, pypdfium2 5.13.0, jsonschema 4.26.0, and Pillow 12.1.1. Both ZIPs are built with explicit file allowlists; neither contains reviewer ground truth, evaluations, generated outputs, or caches.

The final skill ZIP was unpacked outside the project and successfully ran `doctor` and the complete 551-field inspection using the local Python environment. Its template and all 12 files in the demo-input ZIP match the originals byte-for-byte; packaged text files contain no developer-specific home paths.

## Model walkthrough and separate scoring

One independent Codex agent received the copied skill and four input folders in a separate temporary directory, with instructions prohibiting access to the answer key and project documentation. This was instruction-based isolation, not an OS sandbox. The same agent processed all four cases; these were **not four independent fresh sessions**. It inspected all 11 source pages and all 16 final output pages.

Afterward, the implementation agent compared saved PDFs with the held-out reviewer file. No answer-key values were sent back to the agent under test.

| Case | Final draft | Filled fields | Expected values matched automatically | Unresolved conflict fields |
|---|---|---:|---:|---:|
| Clean walkthrough | [Revision 004](../output/forward-test/runs/00_clean_walkthrough/revision-004/acord-125-draft.pdf) | 26 | 15/15 | 0 |
| Lawn & Order challenge | [Revision 002](../output/forward-test/runs/01_lawn_and_order_mowing/revision-002/acord-125-draft.pdf) | 33 | 7/7 | 3 |
| Watson | [Revision 001](../output/forward-test/runs/02_watson_contracting/revision-001/acord-125-draft.pdf) | 28 | 8/9 | 5 |
| Tarheel | [Revision 001](../output/forward-test/runs/03_tarheel_paving/revision-001/acord-125-draft.pdf) | 29 | 9/9 | 1 |

**39/40 normalized value comparisons matched.** Watson's business description includes the expected “Grading contractor” plus a documented resurfacing/pavement-marking/traffic-control project. The implementation agent checked the additional description against source page 1; the evaluator correctly leaves this non-identical string as `review` rather than pretending it is an exact match.

All eight requested QUOTE/GL checkbox checks passed. All 55 required-blank category checks passed. These are checks against a partial oracle, not a claim of 100% extraction accuracy. Additional assignments were also reviewed by the implementation agent; no human insurance professional has reviewed these outputs.

Conflict handling was checked against the expected issues: Lawn's conflicting historical GL dates remain blank and its visible/text-layer discrepancy is reported; Watson's street-number and coverage-specific policy-number alternatives are preserved; Tarheel's disputed legal name remains blank. Watson's $11,388 premium appears only as umbrella premium. Missing entity, contact, and premium information stays blank where required.

Final revisions have passing technical reports and recorded model visual inspections. Each folder contains the PDF, four page images, packet, exception/provenance report, and verification record. Earlier failed/superseded revisions remain saved for audit and are not the recommended demo outputs.

- [Machine scoring summary](../output/reviewer/summary.json)
- [Original agent walkthrough report](../output/forward-test/forward-test-report.md)
- [Original timing records](../output/forward-test/forward-test-results.json)

The copied original report and manifests retain their original temporary paths as historical metadata; use the durable project links above to open the final files. Generated evidence is under ignored `output/` and is not part of the runtime ZIP.

## Failures found and corrected

1. **Clipped full carrier name despite correct PDF readback.** The first auto-fit attempt also failed. The final tool explicitly enables automatic sizing on the actual widget appearance before regenerating it. A regression test and visual reinspection confirm the full value fits. Text in narrow prior-carrier cells is small and may need zoom.
2. **Visible disputed contract text copied into a business description.** The Lawn draft flagged an overlay conflict but still incorporated one alternative. The implementation agent prompted a correction: retain the uncontested business description and put disputed project details in exceptions. Final revision 002 does this. The generic skill guidance now states that rule. This corrected result is not an unassisted first-pass success.
3. **Empty evidence quotation for missing data.** Validation rejected an empty CSV quote. The agent corrected the missing-information issue to have an empty evidence list; no PDF was produced for the rejected packet.
4. **Literal search usability.** `inspect --match` does not support regular-expression OR. The reference now documents literal matching and full field IDs, including page/occurrence.

The two final instruction clarifications above were not followed by a second fresh four-case run. They reflect the observed review corrections; broader reliability remains to be measured.

## Timing and remaining limits

Recorded prepare-to-final-visual-review intervals were **6m38s, 7m20s, 2m40s, and 1m53s**. They overlap and include development fixes/review revisions, so they are not clean latency benchmarks. Human review/correction time was not measured. The assumed 30-minute manual baseline, five-minute target, and 20-case pilot remain unvalidated.

**Claude-chat installation and execution have not been tested.** Local Python execution, Codex orchestration, skill structure, and ZIP packaging were tested. The remaining host check is a fresh Claude-chat installation with code execution and dependencies available, using only one case's three inputs.

Other limits: one template edition; text-based inputs only; no OCR/handwriting; ASCII output text only; no electronic signing, AMS360 write-back, or submission. PDF evidence quotes and semantic mappings remain model judgments, not mechanically proven facts. The outputs are unsigned drafts with unresolved underwriting questions.
