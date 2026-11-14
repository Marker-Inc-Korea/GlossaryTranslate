from __future__ import annotations

import json

import gradio as gr

from glossaryrag.loaders import load_glossary
from glossaryrag.prompt import PromptBuilder, PromptConfig
from glossaryrag.retriever import TrieGlossaryRetriever


def inspect(
    text: str,
    glossary_file,
    source_language: str,
    target_language: str,
    domain: str,
) -> tuple[str, str]:
    if not text.strip():
        return "[]", "Enter source text."
    if glossary_file is None:
        return "[]", "Upload a CSV with source and target columns."
    entries = load_glossary(
        glossary_file,
        source_lang=source_language,
        target_lang=target_language,
    )
    matches = TrieGlossaryRetriever(entries).match(text)
    messages = PromptBuilder().build(
        text,
        (match.entry for match in matches),
        PromptConfig(
            source_language=source_language,
            target_language=target_language,
            domain=domain,
        ),
    )
    return (
        json.dumps([match.to_dict() for match in matches], ensure_ascii=False, indent=2),
        json.dumps(messages, ensure_ascii=False, indent=2),
    )


with gr.Blocks() as demo:
    gr.Markdown("# GlossaryRAG Translate\nMatch organization terms before local LLM translation.")
    source = gr.Textbox(label="Source text", lines=8)
    glossary = gr.File(label="Glossary CSV", file_types=[".csv"], type="filepath")
    with gr.Row():
        source_language = gr.Textbox(label="Source language", value="English")
        target_language = gr.Textbox(label="Target language", value="Spanish")
        domain = gr.Textbox(label="Domain", value="general")
    run = gr.Button("Match glossary", variant="primary")
    matches = gr.Code(label="Matched glossary rows", language="json")
    prompt = gr.Code(label="Structured model messages", language="json")
    run.click(
        inspect,
        inputs=[source, glossary, source_language, target_language, domain],
        outputs=[matches, prompt],
    )

demo.launch()
