# Runtime adapters

## Claude chat

Install the skill ZIP using Claude's custom-skill installation UI; enable code execution. Upload one case's three source files in the chat, not reviewer files. The skill is instruction-driven: Claude performs the reasoning and calls scripts in its execution environment. No API key or second model call is needed.

Locate the installed SKILL.md and uploaded files using the environment's file tools. Do not hardcode /mnt paths. Run the doctor command using the available Python. If dependencies are missing and package installation is available, run `python -m pip install -r "$SKILL_ROOT/requirements.txt"`. If installation is unavailable, report the exact missing dependency; do not claim the skill ran successfully. A fresh Claude-chat install must be tested before the onsite; local tool tests do not establish Claude-chat compatibility.

Use native PDF vision plus the tool's rendered pages and embedded text. Open generated page images with the host's image-viewing tool. Provide output links using that host's artifact/file interface.

## Codex

The same folder can be installed as a local Codex skill or explicitly invoked by its SKILL.md path. Run from a task workspace. Use its local Python environment (create a venv and install requirements if needed). Resolve paths from the skill directory. Use local file/image tools to inspect all source and output pages; do not claim to have read a PDF visually from a text dump.

Link results with absolute local paths. A fresh evaluation task must receive only the skill and the case inputs. Keep answer keys outside its workspace; do not read a repository root indiscriminately.

## Shared limits

One account and one known template per run. No background service, model API client, cloud database, email, or carrier portal. Input content is processed by the active model host; local script execution does not mean the model's processing is local. Public-record-derived sample inputs are not synthetic. Keep the application labeled a draft even when technical checks pass.
