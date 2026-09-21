# ACORD 125 form-filler skill

A portable skill for Claude chat and Codex. Upload one account's CSV, insurance PDF, and submission request; receive an editable **draft ACORD 125**, a short exception list, and a sourced assignment record. The active AI reads documents and chooses fields; Python performs inspection, validation, filling, rendering, and readback.

## Run the demo

**V1 local test in Codex:** start a new task in this project and paste:

```text
Use skills/acord-form-filler/SKILL.md.
Prepare a draft ACORD 125 using only sample input data/00_clean_walkthrough/.
Use .venv/bin/python. Save this run under output/local-test-01.
Do not read _evaluation, previous outputs, or implementation results.
Inspect the source documents and all generated PDF pages.
Return the editable draft PDF, source references, and unresolved questions.
```

Use a new output directory for each run. Open the PDF and compare it with the inputs. To test revision history, explicitly supply a fictional correction, such as: “For this test, change the applicant phone to (202) 555-0147; generate a new revision and preserve the original.” Repeat the workflow in a fresh task with a challenge case. No ZIP is needed for local testing. Setup commands appear below.

Version `1.0.0` is the local implementation baseline. Automated and agent walkthrough results are recorded separately from user acceptance testing; Claude-chat installation remains untested. Generated ZIPs and output evidence are intentionally excluded from Git. Build ZIPs only when ready using `tools/package_skill.py`.

**Claude chat (primary delivery):** install `dist/acord-form-filler.zip` using Claude's custom-skill UI and enable code execution. Unzip `dist/demo-inputs.zip` separately. Attach only the three files from `00_clean_walkthrough`, then ask:

> Use acord-form-filler to prepare a draft ACORD 125 from these files. Leave unsupported answers blank and show anything needing my review.

The skill checks its Python dependencies and provides installation instructions if needed. It requires pypdf, pypdfium2, jsonschema, and Pillow. No extra LLM API key is required: Claude supplies the reasoning. Local tests do not establish installation success in Claude chat; see `docs/IMPLEMENTATION_RESULTS.md` for the actual verification status.

**Codex:** explicitly invoke `skills/acord-form-filler/SKILL.md` with one case directory, or install that folder into your configured Codex skills directory. Use a fresh task for evaluation and keep reviewer files outside its permitted workspace. Local setup:

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r skills/acord-form-filler/requirements.txt
.venv/bin/python skills/acord-form-filler/scripts/form_tool.py doctor
```

Use `.venv/bin/python` for the tool in this checkout. If uv is unavailable, use `python3 -m venv .venv` and `.venv/bin/python -m pip install -r skills/acord-form-filler/requirements.txt`.

The skill resolves its own paths; it does not depend on the developer's home directory. PDF interpretation uses rendered pages as well as embedded text on both hosts. A local script does not make the active model's processing local.

## Discovery and scope

The hypothetical Sterling Cooper account has 100 employees, 30 commercial-lines staff, five offices, and AMS360. `docs/CALL_BRIEF.md` records ten discovery questions, explicit assumed answers, and section decisions. The assumed workload is 120–150 multi-form packages weekly. We chose one ACORD 125 edition to demonstrate a useful bounded workflow; the 30-minute manual baseline and five-minute processing target are assumptions, not measured savings.

Included: one account per run, normalized CSV and text-based insurance PDF inputs, explicit proposed application dates, AI-driven field assignments, evidence, missing/conflict handling, draft-first output, and user-directed revisions. Reusable data includes identity, documented business/premises details, requested transaction and coverage, and prior coverage by line. Unsupported fields stay blank; a draft is not a complete underwriting submission.

Cut: a standalone web UI, OCR/handwriting, arbitrary templates, AMS360 write-back, carrier submission, electronic signatures, shared storage, and production deployment. Four supplied public-record-derived cases support development and demonstration. They are not synthetic, and they are not the proposed 20-case pilot. The clean and Lawn & Order challenge fixtures share an account.

## Architecture decisions

1. **Instructions guide the AI.** `SKILL.md` routes to ACORD interpretation and packet/runtime references. Guidance distinguishes applicant, producer, and certificate holder; historical and proposed coverage; policy-line premiums; and missing versus negative answers. It contains no case answers.
2. **AI chooses field assignments.** Template inspection supplies actual IDs, tooltips, export values, page positions, and limits. The agent interprets raw documents and maps evidence to those fields. There is no hardcoded account extractor or runtime case lookup.
3. **A structured packet separates reasoning from execution.** Assignments record semantic names, actual PDF IDs, values, sources, alternative values, and status. Hashes bind each run to inputs and the bundled template. User corrections retain the previous value and exact recorded statement.
4. **Python supplies repeatable tools.** It validates types, source locations, exact CSV/request quotes, hashes, date formats, checkbox states, and field limits. It fills supported assignments, leaves unresolved ones blank, and reads back canonical fields and widget values. Validation cannot prove a PDF quote or mapping is semantically correct; AI and human review still matter.
5. **PDF presentation is verified separately.** The original template includes XFA and an empty-password encryption layer. The generated copy is an editable AcroForm without stale XFA. Auto-fit text preserves full values where possible. Every output page requires visual inspection; unsupported glyphs fail visibly instead of silently corrupting text.

Outputs are revisioned. The first usable draft is generated without a permission checkpoint. The agent presents unresolved issues afterward, applies explicit corrections, and regenerates. The final deliverable remains unsigned and unsubmitted.

## Extension strategy and AI use

Additional forms reuse the inspection/fill/verification tools and packet structure, while adding edition-specific templates, interpretation guidance, and evaluation cases. Other insurance lines may require additional source facts and semantic fields; a new form is not automatically supported just because the model can read it. New carrier questions require evidence or user input, not invented answers.

AI was used in development to design and author instructions, Python tools, tests, and documentation, and to execute an independent skill walkthrough. Its outputs were checked with automated tests, PDF readback, and visual review. Runtime AI reads uploaded documents, selects mappings, identifies uncertainty, and explains exceptions. Python does not call another model.

Next: complete fresh Claude-chat installation testing, expand to the proposed 20-case set, establish a timed manual baseline with actual users, and measure processing plus review/correction time. Add another form only after addressing observed extraction and mapping failures. Approve real-customer data handling before a live pilot.

## Developer and reviewer commands

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python tools/package_skill.py
.venv/bin/python tools/evaluate_outputs.py --case 00_clean_walkthrough --revision-dir PATH_TO_SAVED_REVISION --out result.json
```

The evaluator uses reviewer-only ground truth and independently selected PDF destinations. It reports value comparisons, blank checks, and conflict-review evidence; it does not pretend substring matching establishes correct conflict handling. It must never be included in the installed skill or provided to the agent under test.

The ZIP builder uses explicit allowlists and checks that answer keys and caches are absent. Original sample files and template remain unchanged. The expected-results file is a partial test oracle: additional source-supported assignments still need review.
