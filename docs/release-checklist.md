# Release checklist

- [ ] Replace the `OWNER` placeholder in `pyproject.toml` and `README.md`.
- [ ] Confirm copyright holder and public repository name.
- [ ] Run unit tests, Ruff, wheel build, and clean-environment installation.
- [ ] Run secret scanning and verify that no internal paths, credentials, or datasets exist.
- [ ] Record all upstream dataset and model revisions.
- [ ] Publish raw aggregate results, not restricted benchmark text.
- [ ] Create the GitHub repository and push `main`.
- [ ] Create the Hugging Face Space from `huggingface/space`.
- [ ] Optionally create a Hugging Face dataset repository for public result tables.
- [ ] Add final GitHub and Hugging Face URLs to the README.

