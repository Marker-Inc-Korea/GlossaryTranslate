# Public evaluation data

The repository does not redistribute benchmark text.

| Domain | Benchmark | Directions | Upstream license | Use here |
|---|---|---|---|---|
| Medical/public health | TICO-19 | English to multiple languages | CC0-1.0 | Sentence-level glossary effect |
| Information technology | WMT25 Terminology Track 1 | English to German, Spanish, Russian | CC BY-NC 4.0 | Proper/random/no-term causal comparison |
| Finance | WMT25 Terminology Track 2 | English and Traditional Chinese | CC BY-NC 4.0 | Long-document, large-dictionary evaluation |

WMT25 is non-commercial research data. Do not copy it into commercial products.
The software remains Apache-2.0 and can be used with an organization's own data.

Official sources:

- https://tico-19.github.io/
- https://github.com/wmt-conference/wmt25-terminology

## Snapshot validation note

The downloaded English-French TICO-19 test snapshot contains mismatched source and
reference rows in an observed `PubMed_8` segment. French is therefore excluded from
the release benchmark rather than reporting a misleading score. The medical study
uses Russian, Latin American Spanish, and Simplified Chinese after language-script
and sampled row-alignment checks.
