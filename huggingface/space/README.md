---
title: GlossaryRAG Translate
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
license: apache-2.0
---

# GlossaryRAG Translate prompt inspector

Upload an organization glossary, enter source text, and inspect the terms and
structured prompt that would be sent to a local translation model.

The Space only demonstrates matching and prompt construction; it does not call a
translation model or bundle model weights. Uploaded files are processed in the Space
runtime. Do not upload confidential glossaries to a public Space. Full private/local
translation is available through the GitHub package.
