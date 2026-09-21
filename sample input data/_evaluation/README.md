# Evaluation ground truth

Do **not** upload this directory to the form-filler. It contains reviewer-only expected results for the four numbered cases.

For each case, evaluate whether the system:

1. Uses `submission_request.json` for proposed application dates.
2. Treats CSV and insurance-policy dates as historical/prior coverage.
3. Fills only source-supported ACORD 125 fields.
4. Carries page-level provenance.
5. Flags every listed conflict rather than resolving it silently.
6. Leaves every listed unsupported field blank.

This is a development and demo set of four cases. It does not satisfy the 20-case pilot evaluation proposed in `docs/CALL_BRIEF.md`.
