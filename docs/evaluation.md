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

Use paired records and deterministic decoding. Keep raw predictions and exact command
lines. For a public report, include model revision, runtime version, hardware, seeds,
dataset revision, and source hashes.

Report paired 95% bootstrap confidence intervals for the change from `no_term`
to `proper`. The resampling unit is the source record, so baseline and treatment
outputs from the same input remain paired.
