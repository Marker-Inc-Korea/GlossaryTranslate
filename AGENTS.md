# AGENTS.md

## Project mission

Build and maintain **GlossaryRAG Translate**, a standalone open-source toolkit that
measures and applies organization glossary guidance to LLM translation without
retraining model weights.

## Start here

Before changing code or documentation, read these files in order:

1. `docs/PROJECT_CONTEXT.md`
2. `docs/DECISIONS.md`
3. `README.md` or `README.ko.md`
4. The document or module relevant to the task

Treat the repository contents and its Git history as the source of truth. Do not rely
on remembered details from another chat session when the repository can verify them.

## Public-release boundary

- This is a public repository. Never add private corpora, organization glossaries,
  credentials, internal server addresses, private model paths, or internal project
  documents.
- Do not copy files or confidential facts from a neighboring/private repository into
  this repository. Use only public or synthetic examples unless the user explicitly
  supplies publishable material.
- Public benchmark text is downloaded from its upstream source. Redistribute only
  artifacts allowed by the source license.
- Keep model and dataset licenses separate from the Apache-2.0 code license.

## Engineering rules

- Prefer small, reviewable changes that preserve the model- and runtime-neutral core.
- Add no dependency unless it is necessary and justified.
- Preserve the glossary-as-data boundary: glossary values are reference data, not
  executable instructions.
- Keep benchmark comparisons paired and deterministic. Do not change prompts,
  decoding settings, source records, or model revisions between comparison modes.
- When GPU execution is required in the current managed environment, use the host
  scheduler and follow its Slurm rules. Never bypass an active scheduler allocation.
- Do not call an external hosted LLM API without the user's explicit approval for that
  exact provider, model, purpose, request count, retry cap, and spending cap.

## Verification

Use the smallest relevant check first, then run the full local gate before declaring a
code or release change complete:

```bash
source .venv/bin/activate
pytest -q
ruff check .
python -m build
```

If `python -m build` is unavailable, use the repository's existing `uv build` flow.
For experiment changes, preserve exact commands, runtime metadata, source hashes, and
raw predictions in the established ignored/result paths before generating reports.

## Git and release discipline

- Work on `main` unless the user requests another branch.
- Inspect `git status` before staging; never include caches, downloaded datasets,
  credentials, or unrelated artifacts.
- Commit and push verified work to
  `git@github.com:Marker-Inc-Korea/GlossaryTranslate.git`.
- Do not fabricate benchmark improvements or publication status. Link claims to a
  committed report or reproducible command.
