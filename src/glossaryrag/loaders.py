from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path

from .models import GlossaryEntry

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def _deduplicate(entries: Iterable[GlossaryEntry]) -> tuple[GlossaryEntry, ...]:
    selected: dict[tuple[str, str, str], GlossaryEntry] = {}
    for entry in entries:
        key = (entry.source, entry.source_lang, entry.target_lang)
        previous = selected.get(key)
        if previous is None or entry.priority > previous.priority:
            selected[key] = entry
    return tuple(selected.values())


def load_csv(path: str | Path, *, delimiter: str | None = None) -> tuple[GlossaryEntry, ...]:
    source = Path(path)
    actual_delimiter = delimiter or ("\t" if source.suffix.lower() == ".tsv" else ",")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle, delimiter=actual_delimiter)
        return _deduplicate(GlossaryEntry.from_dict(row) for row in rows)


def load_jsonl(path: str | Path) -> tuple[GlossaryEntry, ...]:
    entries: list[GlossaryEntry] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            entries.append(GlossaryEntry.from_dict(payload))
    return _deduplicate(entries)


def load_tbx(
    path: str | Path,
    *,
    source_lang: str,
    target_lang: str,
    domain: str = "",
) -> tuple[GlossaryEntry, ...]:
    root = ET.parse(path).getroot()
    entries: list[GlossaryEntry] = []
    for term_entry in root.iter():
        if term_entry.tag.rsplit("}", 1)[-1] != "termEntry":
            continue
        by_language: dict[str, list[str]] = {}
        for lang_set in term_entry:
            if lang_set.tag.rsplit("}", 1)[-1] != "langSet":
                continue
            language = lang_set.attrib.get(XML_LANG) or lang_set.attrib.get("lang") or ""
            terms = [
                (node.text or "").strip()
                for node in lang_set.iter()
                if node.tag.rsplit("}", 1)[-1] == "term" and (node.text or "").strip()
            ]
            if terms:
                by_language.setdefault(language, []).extend(terms)
        sources = by_language.get(source_lang, [])
        targets = by_language.get(target_lang, [])
        for source_term in sources:
            if targets:
                entries.append(
                    GlossaryEntry(
                        source=source_term,
                        target=targets[0],
                        alternatives=tuple(targets[1:]),
                        source_lang=source_lang,
                        target_lang=target_lang,
                        domain=domain,
                    )
                )
    return _deduplicate(entries)


def load_glossary(
    path: str | Path,
    *,
    source_lang: str = "",
    target_lang: str = "",
    domain: str = "",
) -> tuple[GlossaryEntry, ...]:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        return load_csv(source)
    if suffix in {".jsonl", ".ndjson"}:
        return load_jsonl(source)
    if suffix in {".tbx", ".xml"}:
        if not source_lang or not target_lang:
            raise ValueError("TBX loading requires source_lang and target_lang")
        return load_tbx(
            source,
            source_lang=source_lang,
            target_lang=target_lang,
            domain=domain,
        )
    raise ValueError(f"unsupported glossary format: {source.suffix}")
