from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any


def clean_text(value: Any) -> str:
    return " ".join(unicodedata.normalize("NFC", str(value or "")).split())


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    source: str
    target: str
    alternatives: tuple[str, ...] = ()
    source_lang: str = ""
    target_lang: str = ""
    domain: str = ""
    priority: int = 0
    note: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False, hash=False)

    def __post_init__(self) -> None:
        source = clean_text(self.source)
        target = clean_text(self.target)
        if not source or not target:
            raise ValueError("glossary source and target must be non-empty")
        if len(source) > 500 or len(target) > 1_000:
            raise ValueError("glossary source or target is unreasonably long")
        alternatives = tuple(
            dict.fromkeys(clean_text(value) for value in self.alternatives if clean_text(value))
        )
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "alternatives", alternatives)
        object.__setattr__(self, "source_lang", clean_text(self.source_lang))
        object.__setattr__(self, "target_lang", clean_text(self.target_lang))
        object.__setattr__(self, "domain", clean_text(self.domain))
        object.__setattr__(self, "note", clean_text(self.note))

    @property
    def accepted_targets(self) -> tuple[str, ...]:
        return (self.target, *self.alternatives)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "alternatives": list(self.alternatives),
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "domain": self.domain,
            "priority": self.priority,
            "note": self.note,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> GlossaryEntry:
        alternatives = payload.get("alternatives") or ()
        if isinstance(alternatives, str):
            alternatives = tuple(part.strip() for part in alternatives.split("|") if part.strip())
        return cls(
            source=str(payload.get("source") or payload.get("src") or ""),
            target=str(payload.get("target") or payload.get("translation") or ""),
            alternatives=tuple(str(value) for value in alternatives),
            source_lang=str(payload.get("source_lang") or payload.get("src_lang") or ""),
            target_lang=str(payload.get("target_lang") or payload.get("tgt_lang") or ""),
            domain=str(payload.get("domain") or ""),
            priority=int(payload.get("priority") or 0),
            note=str(payload.get("note") or payload.get("description") or ""),
            metadata=payload.get("metadata") or {},
        )


@dataclass(frozen=True, slots=True)
class TermMatch:
    entry: GlossaryEntry
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "entry": self.entry.to_dict()}


@dataclass(frozen=True, slots=True)
class BenchmarkRecord:
    record_id: str
    domain: str
    source_lang: str
    target_lang: str
    source: str
    reference: str
    proper_terms: tuple[GlossaryEntry, ...] = ()
    random_terms: tuple[GlossaryEntry, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.record_id,
            "domain": self.domain,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "source": self.source,
            "reference": self.reference,
            "proper_terms": [entry.to_dict() for entry in self.proper_terms],
            "random_terms": [entry.to_dict() for entry in self.random_terms],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> BenchmarkRecord:
        return cls(
            record_id=str(payload.get("id") or payload.get("record_id") or ""),
            domain=str(payload.get("domain") or ""),
            source_lang=str(payload.get("source_lang") or ""),
            target_lang=str(payload.get("target_lang") or ""),
            source=str(payload.get("source") or ""),
            reference=str(payload.get("reference") or ""),
            proper_terms=tuple(
                GlossaryEntry.from_dict(row) for row in payload.get("proper_terms") or ()
            ),
            random_terms=tuple(
                GlossaryEntry.from_dict(row) for row in payload.get("random_terms") or ()
            ),
            metadata=payload.get("metadata") or {},
        )


@dataclass(frozen=True, slots=True)
class TranslationResult:
    text: str
    matches: tuple[TermMatch, ...]
    messages: tuple[Mapping[str, str], ...]
    model: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


def entries_from_pairs(
    pairs: Mapping[str, str | Sequence[str]],
    *,
    source_lang: str = "",
    target_lang: str = "",
    domain: str = "",
) -> tuple[GlossaryEntry, ...]:
    entries: list[GlossaryEntry] = []
    for source, raw_target in pairs.items():
        clean_source = clean_text(source)
        raw_targets = [raw_target] if isinstance(raw_target, str) else list(raw_target)
        targets = [clean_text(value) for value in raw_targets if clean_text(value)]
        if not clean_source or not targets:
            continue
        entries.append(
            GlossaryEntry(
                source=clean_source,
                target=targets[0],
                alternatives=tuple(targets[1:]),
                source_lang=source_lang,
                target_lang=target_lang,
                domain=domain,
            )
        )
    return tuple(entries)
