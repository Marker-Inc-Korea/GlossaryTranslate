from __future__ import annotations

import csv
import io
import json

import gradio as gr


def inspect(text: str, glossary_file) -> tuple[str, str]:
    if not text.strip():
        return "[]", "Enter source text."
    if glossary_file is None:
        return "[]", "Upload a CSV with source and target columns."
    content = open(glossary_file, encoding="utf-8-sig").read()
    terms = []
    for row in csv.DictReader(io.StringIO(content)):
        source = (row.get("source") or "").strip()
        target = (row.get("target") or "").strip()
        if source and target and source.casefold() in text.casefold():
            terms.append({"source": source, "target": target})
    prompt = (
        "<glossary_data>\n"
        + json.dumps(terms, ensure_ascii=False, separators=(",", ":"))
        + "\n</glossary_data>\n<source_text>\n"
        + text
        + "\n</source_text>"
    )
    return json.dumps(terms, ensure_ascii=False, indent=2), prompt


with gr.Blocks() as demo:
    gr.Markdown("# GlossaryRAG Translate\nMatch organization terms before local LLM translation.")
    source = gr.Textbox(label="Source text", lines=8)
    glossary = gr.File(label="Glossary CSV", file_types=[".csv"], type="filepath")
    run = gr.Button("Match glossary", variant="primary")
    matches = gr.Code(label="Matched glossary rows", language="json")
    prompt = gr.Textbox(label="Structured model input", lines=12)
    run.click(inspect, inputs=[source, glossary], outputs=[matches, prompt])

demo.launch()
