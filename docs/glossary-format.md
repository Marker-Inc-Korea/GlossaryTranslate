# Glossary formats

## CSV / TSV

Required columns:

- `source`
- `target`

Optional columns:

- `alternatives` separated with `|`
- `source_lang`
- `target_lang`
- `domain`
- `priority`
- `note`

## JSONL

```json
{"source":"data controller","target":"responsable del tratamiento","source_lang":"en","target_lang":"es","domain":"privacy","priority":10}
```

## TBX

TBX files are loaded by choosing the source and target language codes. Every
source term is paired with the first target term; additional target terms are
kept as accepted alternatives.

