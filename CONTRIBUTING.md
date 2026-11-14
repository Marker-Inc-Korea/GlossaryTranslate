# Contributing

Contributions are welcome after the public repository is created.

1. Create a focused branch and keep changes small.
2. Do not commit private glossaries, source documents, model weights, credentials,
   benchmark text with redistribution restrictions, or raw prediction files.
3. Add or update tests for behavior changes.
4. Run:

```bash
python -m pip install -e '.[dev,eval]'
ruff check .
pytest -q
```

Changes to matching, prompts, models, or decoding settings should include a paired
`no_term` versus `proper` evaluation and should report terminology success together
with general translation quality.
