# Organization adoption guide

GlossaryRAG Translate is intended for organizations that already maintain approved
translations, interpretation standards, product names, legal terms, medical terms,
or other domain terminology.

## Recommended workflow

1. Export approved terminology to CSV, TSV, JSONL, or TBX.
2. Assign one source expression and one preferred target rendering per row.
3. Keep alternatives only when they are genuinely acceptable.
4. Index the glossary once when the service starts.
5. For each request, retrieve only entries found in the source text.
6. Send the source and matched entries to a private/local translation model.
7. Monitor both terminology success and general translation quality.
8. Version glossary changes independently from model weights.

## Quality gates

- Reject blank source or target values during import.
- Review duplicate source expressions and assign explicit priorities where needed.
- Test the same source records without and with the glossary.
- Use unrelated or random terminology as a negative control during evaluation.
- Do not declare success from BLEU alone; report terminology success and chrF as well.
- Re-run the paired benchmark after changing a glossary, prompt, or model.

## Deployment boundary

The package calls an OpenAI-compatible model endpoint. For confidential source text
or terminology, run both this package and the model endpoint inside the organization's
controlled network. The public Hugging Face Space is an inspector, not a production
translation service.

## Updating terminology

Retraining is not required. Replace the glossary file and rebuild the retriever when
approved terms change. Model replacement and glossary replacement remain independent,
which makes revisions easier to audit and roll back.
