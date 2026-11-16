# Project context

## Purpose

GlossaryRAG Translate is a standalone open-source project for organizations that need
an LLM translation system to follow their preferred terminology without retraining the
model. It loads a glossary, retrieves only entries that appear in the current source
text, serializes those matches as structured reference data, and sends the translation
request to an OpenAI-compatible local model endpoint.

The public project is intentionally independent from the private service in which the
idea was first explored. The reusable method, public implementation, and public
benchmark evidence belong here; private corpora, organization terminology, service
credentials, and internal deployment details do not.

## Current implementation

- Python package and CLI: `src/glossaryrag/`
- Glossary formats: CSV, TSV, JSONL, and TBX
- Matching: reusable character Trie, longest overlapping match, ASCII word-boundary
  protection, and common English inflection handling
- Prompt construction: matched glossary rows are delimited structured reference data
- Model access: OpenAI-compatible local endpoint; vLLM is the reference runtime but is
  not a hard package dependency
- Evaluation modes: no glossary, correct glossary, and random glossary where the
  benchmark provides a negative control
- Metrics: corpus BLEU, corpus chrF, terminology success, paired bootstrap confidence
  intervals, and mean generation latency
- Public demonstration: exportable Gradio glossary matcher and prompt preview
- CI: `.github/workflows/ci.yml`

## Public evidence available now

The committed public benchmark uses `Qwen/Qwen3-8B` at revision
`b968826d9c46dd6066d109eabc6255188de91218` with vLLM 0.23.0. It covers eight
domain-language studies across medical/public-health, information-technology, and
finance data.

The correct glossary improved terminology success in all eight studies. The paired
mean gain ranged from **+9.9 to +51.0 percentage points**. General BLEU and chrF also
improved clearly for the IT and finance studies, while some medical language pairs
showed small general-metric regressions despite stronger terminology adherence. The
project therefore reports both terminology success and general translation metrics
rather than treating either one as sufficient.

Canonical evidence:

- `reports/public-benchmark-public-v2.md`
- `reports/public-source-files.sha256`
- `docs/reference-runtime.md`
- `docs/evaluation.md`
- `docs/public-data.md`

## Public data and licenses

- TICO-19: medical/public-health evaluation, CC0
- WMT25 Terminology tracks: IT and finance evaluation, CC BY-NC 4.0
- Public source text is downloaded from upstream and is not redistributed in the
  package or result-only release bundle.

## Repository and release state

- GitHub: `https://github.com/Marker-Inc-Korea/GlossaryTranslate`
- Default branch: `main`
- Python distribution name: `glossaryrag-translate`
- Code license: Apache-2.0
- Unit tests, Ruff, wheel build, clean installation, secret scanning, public source
  hashes, GitHub push, and public aggregate report generation have been completed.
- Hugging Face Space and optional result-dataset publication have not yet been
  performed.
- The final copyright holder still requires confirmation before the first formal
  release.

## Near-term priorities

1. Confirm the copyright holder and update release metadata if necessary.
2. Publish the already prepared Hugging Face Space after account/repository authority
   is available.
3. Optionally publish the aggregate result-only Hugging Face dataset; do not upload
   restricted benchmark source, reference, glossary, or prediction text.
4. Add or refine experiments only when they answer a clear research or adoption
   question and preserve the paired evaluation protocol.
5. Keep documentation usable for translation companies and organizations with their
   own terminology standards.

## Starting a new OMX session

Start the session from this repository root and use:

> Read `AGENTS.md`, `docs/PROJECT_CONTEXT.md`, and `docs/DECISIONS.md` first. Treat
> them and the current Git history as the project source of truth, summarize the
> current state and remaining work briefly, and then continue with my request.
