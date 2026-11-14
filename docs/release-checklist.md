# Release checklist

- [ ] Replace the `OWNER` placeholder in `pyproject.toml` and `README.md`.
- [ ] Confirm copyright holder and public repository name.
- [x] Run unit tests, Ruff, wheel build, and clean-environment installation.
- [x] Run secret scanning and verify that no internal paths, credentials, or datasets exist.
- [x] Record the model revision and public source-file hashes.
- [x] Generate aggregate results without restricted benchmark text.
- [ ] Create the GitHub repository and push `main`.
- [ ] Create the Hugging Face Space from `huggingface/space`.
- [x] Build the Space bundle with `scripts/export_hf_space.py` and smoke-test it.
- [ ] Optionally create a Hugging Face dataset repository for public result tables.
- [x] Build the result-only dataset with `scripts/export_hf_results.py`.
- [ ] Add final GitHub and Hugging Face URLs to the README.
