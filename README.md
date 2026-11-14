# GlossaryRAG Translate

[한국어 문서](README.ko.md)

**Bring an organization's terminology to an LLM translator without retraining the model.**

GlossaryRAG Translate indexes a CSV, JSONL, TSV, or TBX termbase, retrieves terms
that occur in each source document, and supplies the matched mappings to a local
OpenAI-compatible LLM endpoint as structured reference data.

The project is designed for translation teams, public institutions, legal and
medical organizations, manufacturers, and any organization that maintains its own
translation or interpretation standards.

## What it provides

- reusable Trie-based exact term retrieval
- ASCII word-boundary checks with common English inflection support
- longest-overlap handling for nested terms
- CSV, TSV, JSONL, and TBX glossary input
- model-neutral structured glossary prompts
- local vLLM/OpenAI-compatible inference
- no-term, proper-term, and random-term benchmark modes
- BLEU, chrF, and terminology success evaluation
- adapters for public medical, IT, and finance benchmarks
- a lightweight Hugging Face Space for glossary matching and prompt inspection

No private model, dataset, API key, or organization glossary is included.

## Installation

```bash
git clone https://github.com/OWNER/glossaryrag-translate.git
cd glossaryrag-translate
python -m venv .venv
source .venv/bin/activate
pip install -e '.[eval]'
```

## 1. Match an organization glossary

```bash
glossaryrag match \
  --glossary examples/glossary.csv \
  --text 'The data controller records the purpose of processing personal data.'
```

Only terms found in the source are returned. Nested matches prefer the longest
source expression, so `data controller` wins over `controller` at the same span.

## 2. Translate with a local LLM

Start an OpenAI-compatible model server such as vLLM, then run:

```bash
glossaryrag translate \
  --glossary examples/glossary.csv \
  --text 'The data controller records the purpose of processing personal data.' \
  --source-lang English \
  --target-lang Spanish \
  --domain privacy \
  --base-url http://127.0.0.1:8000 \
  --model Qwen/Qwen3-8B
```

## 3. Download public evaluation data

```bash
glossaryrag download tico19 --output data/raw/tico19 --languages ru,es-LA,zh
glossaryrag download wmt25 --output data/raw/wmt25
```

Data are downloaded from the official upstream repositories and are ignored by
Git. TICO-19 is CC0. WMT25 is CC BY-NC 4.0 and must not be treated as commercial
product data.

## 4. Prepare benchmark JSONL

```bash
# Medical/public health
glossaryrag prepare tico19 \
  --input data/raw/tico19 \
  --terminology data/raw/tico19/terminologies/f_en-ru_RU.csv \
  --target-lang ru \
  --limit 100 \
  --output data/processed/tico19-en-ru.jsonl

# Information technology
glossaryrag prepare wmt25-track1 \
  --input data/raw/wmt25 \
  --target-lang es \
  --limit 100 \
  --output data/processed/wmt25-it-en-es.jsonl

# Finance, document level
glossaryrag prepare wmt25-track2 \
  --input data/raw/wmt25 \
  --per-year-limit 2 \
  --direction en-zh \
  --output data/processed/wmt25-finance.jsonl
```

## 5. Run a controlled experiment

```bash
glossaryrag benchmark \
  --dataset data/processed/wmt25-it-en-es.jsonl \
  --output results/wmt25-it-en-es.predictions.jsonl \
  --base-url http://127.0.0.1:8000 \
  --model Qwen/Qwen3-8B \
  --modes no_term,proper,random \
  --disable-thinking \
  --workers 4
```

The runner is resumable. It appends raw predictions and writes a neighboring
`*.metrics.json` report.

Use a paired bootstrap comparison to quantify the change from the same source
sentences translated without and with the correct glossary:

```bash
glossaryrag compare \
  --predictions results/wmt25-it-en-es.predictions.jsonl \
  --baseline no_term \
  --treatment proper \
  --bootstrap-samples 1000
```

## Evidence plan

The initial public study uses one Apache-2.0 open model and three domains:

| Domain | Public source | Main comparison |
|---|---|---|
| Medical/public health | TICO-19 | no glossary vs matched medical glossary |
| Information technology | WMT25 Track 1 | no term vs proper term vs random term |
| Finance | WMT25 Track 2 | long document with a large corpus-level dictionary |

See [evaluation protocol](docs/evaluation.md) and
[public data notes](docs/public-data.md). Exact reference model and inference settings
are recorded in [reference runtime](docs/reference-runtime.md).

## Public benchmark result

Using `Qwen/Qwen3-8B`, the correct matched glossary improved terminology success in
all eight evaluated domain/language studies. Paired gains ranged from **+9.9 to +51.0
percentage points**. IT and finance also showed clear BLEU/chrF gains. Medical results
were mixed for general reference similarity: Russian improved, while Spanish and
Chinese traded a small BLEU/chrF change for higher terminology adherence. This is why
the package reports both metric families and does not claim universal quality gains.

See the full [public benchmark report](reports/public-benchmark-public-v2.md), including
random-term controls and paired 95% bootstrap intervals.

For production planning, see the
[organization adoption guide](docs/organization-adoption.md). For release steps,
see [GitHub and Hugging Face publishing](docs/publishing.md). The project's scope
relative to prior terminology-aware translation work is stated in
[related work](docs/related-work.md).

## Design choices

- **Inference-time integration:** organizations can update terminology without model retraining.
- **Matched rows only:** a large termbase is indexed once; each request receives relevant rows.
- **All matches by default:** the library does not silently discard terms. `max_terms` is optional.
- **Structured data boundary:** glossary mappings are serialized as JSON reference data.
- **Model independence:** the core library has no dependency on a specific LLM vendor.

## Scope and limitations

Exact matching is predictable and fast but does not resolve morphology, semantic
aliases, or ambiguous senses by itself. Prompt-based glossary use does not guarantee
that every model will follow every mapping. Production users should evaluate their
own domains, languages, models, and glossary quality.

## License

Code is Apache-2.0. Dataset and model licenses are separate. See `NOTICE` and
`docs/public-data.md`.
