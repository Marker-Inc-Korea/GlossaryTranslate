from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass

from .models import GlossaryEntry, TermMatch

_ENTRY = object()


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    case_sensitive: bool = False
    longest_overlap_wins: bool = True
    unique_source_terms: bool = True
    max_terms: int | None = None


class TrieGlossaryRetriever:
    """Reusable exact glossary retriever with longest-overlap resolution."""

    def __init__(
        self,
        entries: Iterable[GlossaryEntry],
        *,
        config: RetrievalConfig | None = None,
    ) -> None:
        self.config = config or RetrievalConfig()
        self.entries = tuple(entries)
        self._trie: dict[object, object] = {}
        for entry in self.entries:
            key = self._normalize(entry.source)
            node = self._trie
            for character in key:
                node = node.setdefault(character, {})  # type: ignore[assignment]
            node.setdefault(_ENTRY, []).append(entry)  # type: ignore[attr-defined]

    def _normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFC", value)
        return normalized if self.config.case_sensitive else normalized.casefold()

    def match(self, text: str, *, max_terms: int | None = None) -> tuple[TermMatch, ...]:
        normalized = self._normalize(text)
        candidates: list[TermMatch] = []
        for start in range(len(normalized)):
            node = self._trie
            cursor = start
            while cursor < len(normalized):
                next_node = node.get(normalized[cursor])
                if not isinstance(next_node, dict):
                    break
                node = next_node
                for entry in node.get(_ENTRY, []):
                    candidates.append(TermMatch(entry=entry, start=start, end=cursor + 1))
                cursor += 1

        candidates.sort(
            key=lambda match: (
                match.start,
                -(match.end - match.start),
                -match.entry.priority,
                match.entry.source,
            )
        )
        accepted: list[TermMatch] = []
        seen_sources: set[str] = set()
        for candidate in candidates:
            source_key = self._normalize(candidate.entry.source)
            if self.config.unique_source_terms and source_key in seen_sources:
                continue
            if self.config.longest_overlap_wins and any(
                candidate.start < previous.end and candidate.end > previous.start
                for previous in accepted
            ):
                continue
            accepted.append(candidate)
            seen_sources.add(source_key)

        accepted.sort(key=lambda match: (match.start, -(match.end - match.start)))
        limit = max_terms if max_terms is not None else self.config.max_terms
        if limit is not None:
            if limit <= 0:
                return ()
            accepted = accepted[:limit]
        return tuple(accepted)
