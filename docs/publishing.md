# Publishing GitHub and Hugging Face releases

## GitHub

1. Create an empty public repository named `glossaryrag-translate`.
2. Replace `OWNER` in `README.md` and `pyproject.toml`.
3. Add the remote and push the recorded history:

```bash
git remote add origin https://github.com/OWNER/glossaryrag-translate.git
git push -u origin main
```

## Hugging Face Space

Create a self-contained Space directory that reuses the exact Python matcher:

```bash
python scripts/export_hf_space.py --output dist/hf-space
```

Create a public Gradio Space and upload the contents of `dist/hf-space`. The Space
does not call a model; it demonstrates glossary matching and structured prompt input.

## Hugging Face result dataset

Build a result-only dataset directory:

```bash
python scripts/export_hf_results.py \
  --report reports/public-benchmark-public-v1.md \
  --output dist/hf-results
```

Upload only this aggregate report and metadata. Do not upload WMT25 source, reference,
terminology, or prediction text because its license is CC BY-NC 4.0 and this project
deliberately downloads it from upstream instead of redistributing it.
