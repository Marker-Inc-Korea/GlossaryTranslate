# Evaluation protocol

For every benchmark record, run the same model and decoding settings in three modes:

- `no_term`: no glossary rows are supplied.
- `proper`: domain terminology supplied by the benchmark is supplied.
- `random`: benchmark-provided random terms are supplied where available.

Report at least:

- corpus BLEU
- corpus chrF
- terminology success rate against the proper-term references
- mean generation time

Terminology success is computed over unique proper glossary entries matched in each
source record. An entry succeeds when its preferred target or an accepted alternative
appears in the model output after Unicode normalization and case folding. This is a
strict surface-form measure; it does not replace human adequacy review.

Use paired records and deterministic decoding. Keep raw predictions and exact command
lines. For a public report, include model revision, runtime version, hardware, seeds,
dataset revision, and source hashes.

Report paired 95% bootstrap confidence intervals for the mean per-record change from
`no_term` to `proper`. The resampling unit is the source record, so baseline and
treatment outputs from the same input remain paired. Use the SacreBLEU Chinese
tokenizer for Chinese targets and score opposite translation directions separately.
