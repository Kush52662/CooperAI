# ACORD 125 form-filler skill

A conversational skill for Claude and Codex. Provide an account CSV and insurance PDF; receive an editable, unsigned ACORD 125 draft with source evidence and unresolved questions. The active model interprets documents; Python validates, fills, renders, and checks the PDF. No separate app or model API key is required.

## Run locally in Codex

Start a fresh task and paste:

```text
Use skills/acord-form-filler/SKILL.md.
Prepare an ACORD 125 draft from the CSV and insurance PDF in
sample input data/00_clean_walkthrough/.
Use .venv/bin/python and a new output directory.
Do not read _evaluation, previous outputs, or implementation results.
Inspect the source documents and all generated PDF pages.
Return the draft PDF, source references, and unresolved questions.
```

The CSV contains requested form, transaction status, proposed effective/expiration dates, and requested lines of business. All three sample CSVs include these columns. The user-facing workflow accepts only the CSV and insurance PDF.

After receiving the draft, answer the native question controls or reply naturally: “For this test, change the applicant phone to (202) 555-0147.” Explicit corrections create a new revision; earlier PDFs and source alternatives remain preserved. Skipped questions stay unresolved. Host previews are not direct PDF editors.

## Setup and checks

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r skills/acord-form-filler/requirements.txt
.venv/bin/python skills/acord-form-filler/scripts/form_tool.py doctor
.venv/bin/python -m unittest discover -s tests -q
```

If uv is unavailable, use `python3 -m venv .venv` and `.venv/bin/python -m pip install -r skills/acord-form-filler/requirements.txt`.

For Claude, see [runtime instructions](skills/acord-form-filler/references/runtime.md). Fresh Claude installation/execution remains untested. No current ZIP is provided; packaging is deferred. The active host processes input content, so local Python execution does not imply local-only AI processing.

## Design and scope

- **AI interpretation:** inspect every rendered source page, distinguish applicant/producer/carrier roles, map evidence to actual template fields, and preserve disagreements.
- **Deterministic execution:** enforce source hashes, field types, exact checkbox states, dates, evidence locations, and revision history; verify written PDF values.
- **Conversational review:** native Q&A where available, plain chat otherwise. Review current state, stage a batch of corrections, apply one revision, and inspect its output.
- **Separate visual checks:** readback does not prove semantic accuracy or correct appearance. Inspect every output page before recording visual approval.

Supported: one account, the registered ACORD 125 (2016/03), legible insurance PDFs, two-file inputs, corrections/additions/clearing, and focused form previews. Unsupported: arbitrary templates, handwriting, non-ASCII output, signatures, AMS360 write-back, carrier submission, and deployment. The shared engine selects form-specific templates, guidance, output names, and date-field markers through `assets/forms.json`. Another form still requires its own asset, guidance, registry entry, and evaluation cases before support can be claimed.

The three public-record-derived company cases are development examples, not a 20-case pilot. The [discovery brief](docs/CALL_BRIEF.md) records assumed workload and timing targets, not measured savings.

## Validation and references

- [Current validation](docs/SKILL_WORKFLOW_VALIDATION.md): 30 tests; three development cases; native-host testing limits.
- [Skill entrypoint](skills/acord-form-filler/SKILL.md) and [tool contracts](skills/acord-form-filler/references/packet-format.md).
- [Sample inputs](sample%20input%20data/README.md).

Reviewer-only scoring is available through `tools/evaluate_outputs.py`; never supply its answer key to the agent preparing a draft. Generated evidence stays under ignored `output/`. The `v1.0.0` baseline is preserved; Streamlit source remains on `codex/streamlit-spike`.
