# Native review and questions

Read this when presenting a draft, asking for clarification, or applying a correction. The conversation is the review interface; do not build a separate UI or ask the user to edit packets or run commands.

## Choose the available host controls

Inspect the current tool definitions and restrictions, not just the product name. Tool names and availability vary by client and mode.

- Codex: prefer `request_user_input_async` when available for missing facts or conflicting values. Use `request_user_input` only when the current mode and tool instructions allow it. Do not switch to Plan mode just to obtain a question widget.
- Claude Code: use `AskUserQuestion` when exposed and permitted. Follow its current schema. Do not assume Claude chat exposes the same tool.
- Claude chat or any host without an appropriate question tool: ask one concise question in ordinary chat with labeled source alternatives and a free-text response path. Do not simulate clickable buttons with Markdown.
- Use the native image/PDF viewer to show evidence and the native file/artifact interface to deliver the PDF. In Codex desktop, open the output with `open_in_codex` when available and useful, and always include its file link. Do not promise direct PDF editing in the host preview.

## Draft first, then resolve

Deliver the verified draft before starting the clarification loop. Report the actual unresolved count, briefly name the material issues, and link the PDF and review report. Use human labels such as “General liability expiration date”; keep PDF field IDs and packet paths out of questions.

Ask one decision at a time by default, prioritizing substantive conflicts and missing information that changes the application. Group tightly related fields only when the answer can unambiguously resolve each one. Do not ask the user to reconfirm supported facts or every unused template field.

For a conflict, state the field and the conflicting evidence. Choices must show the exact value plus source and page/CSV column; include “Leave unresolved” if the tool supports enough options. Allow a custom answer via the tool's native free-text path. If required option limits cannot represent the evidence fairly, use a plain chat question instead. Show the relevant rendered source page or crop when the distinction is visual.

Do not recommend one disputed factual value merely because a question tool requires a recommended or preselected option. Where that rule applies, recommend leaving it unresolved pending confirmation. A default selection, empty response, dismissal, timeout, or elapsed time is not confirmation. Preserve the blank value and issue until the user actually answers.

While an asynchronous question is pending, continue independent verification or prepare the next evidence view. Do not fill the disputed field, issue another duplicate question, or treat a later unrelated message as its answer. If the user stops review, return the latest draft with unresolved fields blank.

## Turn answers into revisions

Bind each question to the current run, revision, field ID(s), and displayed alternatives. After resuming, read the current packet before applying the answer; check that the question still refers to the same account and issue. Reuse the packet, manifest, review report, and history for continuity instead of inventing a second state store.

Accept ordinary corrections such as “Use the certificate date” when the displayed certificate and date uniquely identify a value. If several dates or fields could match, ask a targeted follow-up. Preserve the exact user response in correction history; do not invent a fuller confirmation. Never change adjacent dates or other fields by implication.

Use review, stage-corrections, apply-corrections, validate, fill, and visual inspection. Batch all fields explicitly answered in one reply into one revision. Apply an explicit correction without a redundant approval prompt. Return the revised PDF, a brief before/after statement, and the remaining issue count; then ask the next needed question. “Leave unresolved” preserves the conflict and alternatives and does not mark a value user-confirmed.

## Capability and evidence limits

The skill can request native controls; it cannot enable tools that the host has not provided. Do not create a new API client, use another model, or send documents to a third-party integration for Q&A. Do not describe native question behavior as tested on Claude or Codex until an actual interaction has been observed on that host.

Claude Code reference: https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/command-development/references/interactive-commands.md
Codex behavior must follow the active session's tool definitions, including mode restrictions and asynchronous reply semantics.
