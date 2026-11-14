# Architecture

GlossaryRAG Translate keeps organization terminology separate from model weights.

1. A glossary loader reads CSV, TSV, JSONL, or TBX.
2. A reusable character Trie indexes source terms once.
3. The retriever finds exact source spans and resolves overlaps by longest match.
4. Only matched glossary rows are serialized as delimited JSON reference data.
5. An OpenAI-compatible local endpoint produces the translation.
6. Evaluation compares no-term, proper-term, and random-term conditions.

The core package does not require a specific model server. vLLM is the reference
runtime because it exposes an OpenAI-compatible endpoint, but compatible local
runtimes can be substituted.

## Boundaries

- Glossary rows are data, not executable instructions.
- Source and target corpora are never bundled in the Python wheel.
- Public benchmark adapters download data from upstream maintainers.
- Dataset and model licenses remain independent of the Apache-2.0 code license.

