# Onsite demo sequence

1. Install the skill in Claude chat with code execution enabled. Confirm dependencies before the panel. If this has not been tested on that host, state that limitation; do not call a Codex run a Claude-chat test.
2. Start a fresh conversation. Upload only the three files in `00_clean_walkthrough`. Ask for a draft ACORD 125. Explain that the requested dates differ from historical coverage dates.
3. Open the PDF and review summary. Show field placement, an evidence reference, and unsupported fields left blank. Show technical readback separately from visual and factual review.
4. In a new conversation, upload one challenge case. Ask for a draft; inspect the actual exception report, without telling the agent which conflict to find.
5. For a revision demonstration, explicitly provide a fictional test correction such as “For this demo, use [chosen value] for [field].” Identify it as a demo instruction, not a newly verified fact. Inspect the new PDF and preserved history.
6. Explain the role split: AI reads documents and chooses mappings using skill instructions; Python validates and executes the assignments. Show the small tool entry point and the relevant form guidance.
7. Show measured evaluation results, including failures and fixes. The five-minute target, four development cases, and future 20-case pilot must remain distinct.

Never upload `_evaluation`, evaluation results, or the whole repository to the agent. Clean-case results alone are not evidence that the conflict cases work.
