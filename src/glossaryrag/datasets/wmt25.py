from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from ..io import write_jsonl
from ..models import BenchmarkRecord, entries_from_pairs

TRACK1_LANGUAGES = {"de": "German", "es": "Spanish", "ru": "Russian"}


def _read_rows(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise ValueError(f"invalid WMT25 row in {path}")
                yield payload


def prepare_wmt25_track1(
    reference_dir: str | Path,
    output: str | Path,
    *,
    target_lang: str,
    limit: int | None = None,
) -> int:
    if target_lang not in TRACK1_LANGUAGES:
        raise ValueError(f"target_lang must be one of {sorted(TRACK1_LANGUAGES)}")
    path = Path(reference_dir) / f"full_data.en{target_lang}.jsonl"
    records: list[BenchmarkRecord] = []
    for index, row in enumerate(_read_rows(path)):
        if limit is not None and len(records) >= limit:
            break
        records.append(
            BenchmarkRecord(
                record_id=f"wmt25-it-en-{target_lang}-{index:04d}",
                domain="information technology",
                source_lang="English",
                target_lang=TRACK1_LANGUAGES[target_lang],
                source=str(row["en"]),
                reference=str(row[target_lang]),
                proper_terms=entries_from_pairs(
                    row.get("proper") or {},
                    source_lang="en",
                    target_lang=target_lang,
                    domain="information technology",
                ),
                random_terms=entries_from_pairs(
                    row.get("random") or {},
                    source_lang="en",
                    target_lang=target_lang,
                    domain="information technology",
                ),
                metadata={"upstream": "WMT25 Terminology Track 1", "row": index},
            )
        )
    write_jsonl(output, (record.to_dict() for record in records))
    return len(records)


def prepare_wmt25_track2(
    reference_dir: str | Path,
    output: str | Path,
    *,
    years: Iterable[int] = range(2015, 2025),
    limit: int | None = None,
) -> int:
    records: list[BenchmarkRecord] = []
    for year in years:
        path = Path(reference_dir) / f"full_data_{year}.jsonl"
        source_code, target_code = ("en", "zh") if year % 2 else ("zh", "en")
        source_name, target_name = (
            ("English", "Traditional Chinese")
            if source_code == "en"
            else ("Traditional Chinese", "English")
        )
        for row_index, row in enumerate(_read_rows(path)):
            if limit is not None and len(records) >= limit:
                break
            records.append(
                BenchmarkRecord(
                    record_id=f"wmt25-finance-{source_code}-{target_code}-{year}-{row_index:03d}",
                    domain="finance",
                    source_lang=source_name,
                    target_lang=target_name,
                    source=str(row[source_code]),
                    reference=str(row[target_code]),
                    proper_terms=entries_from_pairs(
                        row.get("proper") or {},
                        source_lang=source_code,
                        target_lang=target_code,
                        domain="finance",
                    ),
                    random_terms=entries_from_pairs(
                        row.get("random") or {},
                        source_lang=source_code,
                        target_lang=target_code,
                        domain="finance",
                    ),
                    metadata={"upstream": "WMT25 Terminology Track 2", "year": year},
                )
            )
        if limit is not None and len(records) >= limit:
            break
    write_jsonl(output, (record.to_dict() for record in records))
    return len(records)
