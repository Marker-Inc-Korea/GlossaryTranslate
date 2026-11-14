# Public benchmark plan

## Goal

Measure whether inference-time glossary retrieval improves terminology use without
degrading overall translation quality across unrelated domains.

## Common model

- Model: `Qwen/Qwen3-8B`
- License: Apache-2.0
- Runtime: vLLM OpenAI-compatible server
- Decoding: temperature 0, thinking disabled

Using one model and one decoding configuration avoids attributing a model change to
the glossary method.

## Stage 1: smoke experiment

- 12 medical records from TICO-19 English-French
- 12 IT records from WMT25 English-Spanish
- one finance document from WMT25 English-Chinese
- modes: no-term and proper-term; random-term where supplied by WMT25

Stop if the data adapters, language direction, output format, or terminology metric
is invalid.

## Stage 2: public evaluation

- TICO-19: at least 100 term-bearing records in three target languages
- WMT25 Track 1: 500 records for each of English-German, English-Spanish, English-Russian
- WMT25 Track 2: all released finance documents in both directions

## Primary outputs

- raw prediction JSONL for every condition
- aggregate BLEU and chrF
- terminology success rate
- paired per-record differences
- generation time and model/runtime metadata
- errors grouped by missing term, wrong term, grammar, and context mismatch

## Interpretation

A glossary method is considered useful only when terminology success improves and
overall translation quality does not show a practically meaningful decline. Results
must be reported by domain and language direction rather than as one pooled number.

