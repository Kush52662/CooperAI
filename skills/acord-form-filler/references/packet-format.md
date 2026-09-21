# Assignment packet

`prepare` creates packet.json with hashes and source filenames. Keep those values unchanged. `packet.schema.json` is the machine-readable contract. It is metadata, not a source of account answers.

Each assignment has:

- `semantic`: stable meaning, e.g. `applicant.name` or `prior_coverage.general_liability.policy_number`.
- `field_id`: full actual ID returned by template inspection.
- `value`: string for supported/user-confirmed fields; null for missing/conflicting fields. Checkbox values must be exact export states such as `/1`, never a guessed boolean.
- `status`: `supported`, `missing`, `conflict`, or `user_confirmed`.
- `evidence`: source references with a verbatim `quote`. PDF references require `file`, 1-based `page`, and preferably `channel` (`rendered` or `text`). CSV references require a `column` and exact cell quote. Request references require a `key` and exact value quote; serialize list values as JSON.
- `alternatives`: list of `{value, evidence}` objects; at least two for conflicts. Preserve historical alternatives after user resolution.
- `note`: concise interpretation or normalization explanation.

Illustrative shape only, with deliberately fictional values:

```json
{
  "semantic": "applicant.name",
  "field_id": "F[0].P1[0].NamedInsured_FullName_A[0]",
  "value": "Example Orchard LLC",
  "status": "supported",
  "evidence": [{"file":"insurance_document.pdf", "page":1, "channel":"rendered", "quote":"Example Orchard LLC"}],
  "alternatives": [],
  "note": "Named insured; not the certificate holder."
}
```

`issues` records unresolved categories or document problems as `{field, message, evidence}`. Use this for missing data without a proposed value, unsupported requested sections, and image/text discrepancies. An empty evidence list is appropriate for absence of information. Issues are not silently resolved by generating a PDF.

`history` is initially empty. `resolve` records each user correction with time, field ID, previous value/status, and the exact user statement. User confirmation is an agent-recorded conversation fact, not cryptographic authorization. Never write history from reviewer answer keys.

Keep the current packet separate from the immutable copy in each generated revision directory. Increment revision for any manual packet correction. `fill` refuses to overwrite an existing revision.

## CLI

Prefix every command with `python "$SKILL_ROOT/scripts/form_tool.py"`:

```text
doctor
prepare --input-dir INPUT --run-dir NEW_RUN
inspect --match "NamedInsured"
inspect --match "PriorCoverage"
validate --packet RUN/packet.json --run-dir RUN
fill --packet RUN/packet.json --run-dir RUN
verify --pdf REVISION/acord-125-draft.pdf --packet REVISION/packet.json
render --pdf INPUT.pdf --out PAGE_DIRECTORY
resolve --packet PACKET --run-dir RUN --field FIELD_ID --value VALUE --statement USER_STATEMENT
record-visual-review --revision-dir REVISION --result pass --note OBSERVATIONS
```

Use argument arrays or safe shell quoting. Do not interpolate document text into shell commands. Validation checks evidence locations and source hashes, not whether PDF quotations or semantic interpretations are true. Review those against actual documents.

`inspect --match` performs a case-insensitive literal substring search, not a regular expression. Use separate searches or read `fields.json` for several categories. Always use the complete field ID, including page and occurrence; suffixes can repeat.
