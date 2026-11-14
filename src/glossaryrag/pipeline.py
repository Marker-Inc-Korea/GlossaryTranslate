from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .client import ChatClient
from .models import GlossaryEntry, TranslationResult
from .prompt import PromptBuilder, PromptConfig
from .retriever import TrieGlossaryRetriever


@dataclass(slots=True)
class GlossaryRAGTranslator:
    retriever: TrieGlossaryRetriever
    client: ChatClient
    prompt_builder: PromptBuilder = PromptBuilder()

    @classmethod
    def from_entries(
        cls,
        entries: Iterable[GlossaryEntry],
        *,
        client: ChatClient,
    ) -> GlossaryRAGTranslator:
        return cls(retriever=TrieGlossaryRetriever(entries), client=client)

    def translate(
        self,
        source_text: str,
        *,
        source_language: str,
        target_language: str,
        domain: str = "general",
        style: str = "professional and natural",
        max_terms: int | None = None,
    ) -> TranslationResult:
        matches = self.retriever.match(source_text, max_terms=max_terms)
        prompt_config = PromptConfig(
            source_language=source_language,
            target_language=target_language,
            domain=domain,
            style=style,
        )
        messages = self.prompt_builder.build(
            source_text,
            (match.entry for match in matches),
            prompt_config,
        )
        translated = self.client.complete(messages)
        return TranslationResult(
            text=translated,
            matches=matches,
            messages=messages,
            model=self.client.model,
        )
