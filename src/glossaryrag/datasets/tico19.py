from __future__ import annotations

import csv
import io
import random
import zipfile
from pathlib import Path

from ..io import write_jsonl
from ..models import BenchmarkRecord, GlossaryEntry
from ..retriever import TrieGlossaryRetriever

LANGUAGE_NAMES = {
    "ar": "Arabic",
    "es-LA": "Latin American Spanish",
    "fr": "French",
    "pt-BR": "Brazilian Portuguese",
    "ru": "Russian",
    "zh": "Simplified Chinese",
}


def _load_terms(path: Path, target_code: str) -> tuple[GlossaryEntry, ...]:
    entries: list[GlossaryEntry] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source = str(row.get("sourceString") or "").strip()
            target = str(row.get("targetString") or "").strip()
            if not source or not target:
                continue
            entries.append(
                GlossaryEntry(
                    source=source,
                    target=target,
                    source_lang="en",
                    target_lang=target_code,
                    domain="medical and public health",
                    note=str(row.get("description") or ""),
                )
            )
    return tuple(entries)


def prepare_tico19(
    testset_zip: str | Path,
    terminology_csv: str | Path,
    output: str | Path,
    *,
    target_lang: str,
    split: str = "test",
    limit: int | None = None,
    seed: int = 17,
) -> int:
    if target_lang not in LANGUAGE_NAMES:
        raise ValueError(f"unsupported target language: {target_lang}")
    terms = _load_terms(Path(terminology_csv), target_lang)
    retriever = TrieGlossaryRetriever(terms)
    archive_member = f"tico19-testset/{split}/{split}.en-{target_lang}.tsv"
    records: list[BenchmarkRecord] = []
    rng = random.Random(seed)
    with zipfile.ZipFile(testset_zip) as archive:
        text = archive.read(archive_member).decode("utf-8")
    for row_index, row in enumerate(csv.DictReader(io.StringIO(text), delimiter="\t")):
        source = str(row.get("sourceString") or "").strip()
        proper = tuple(match.entry for match in retriever.match(source))
        if not proper:
            continue
        proper_keys = {entry.source.casefold() for entry in proper}
        random_pool = [entry for entry in terms if entry.source.casefold() not in proper_keys]
        random_terms = tuple(rng.sample(random_pool, k=min(len(proper), len(random_pool))))
        records.append(
            BenchmarkRecord(
                record_id=f"tico19-medical-en-{target_lang}-{row_index:05d}",
                domain="medical and public health",
                source_lang="English",
                target_lang=LANGUAGE_NAMES[target_lang],
                source=source,
                reference=str(row.get("targetString") or "").strip(),
                proper_terms=proper,
                random_terms=random_terms,
                metadata={
                    "upstream": "TICO-19",
                    "string_id": row.get("stringID"),
                    "license": row.get("license"),
                },
            )
        )
        if limit is not None and len(records) >= limit:
            break
    write_jsonl(output, (record.to_dict() for record in records))
    return len(records)
