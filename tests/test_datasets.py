import json
from pathlib import Path

from glossaryrag.datasets.wmt25 import prepare_wmt25_track1, prepare_wmt25_track2
from glossaryrag.models import BenchmarkRecord, GlossaryEntry, entries_from_pairs
from glossaryrag.runner import _entries_for_mode


def test_prepare_wmt25_track1(tmp_path: Path) -> None:
    source = tmp_path / "references"
    source.mkdir()
    row = {
        "en": "Use parallel processing for this job.",
        "es": "Utilice el procesamiento paralelo para este job.",
        "proper": {"parallel processing": "procesamiento paralelo", "job": "job"},
        "random": {"use": "utilice"},
        "noterm": {},
    }
    (source / "full_data.enes.jsonl").write_text(
        json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    output = tmp_path / "prepared.jsonl"
    count = prepare_wmt25_track1(source, output, target_lang="es")
    prepared = json.loads(output.read_text(encoding="utf-8"))
    assert count == 1
    assert prepared["domain"] == "information technology"
    assert prepared["proper_terms"][0]["source_lang"] == "en"


def test_entries_from_pairs_skips_empty_wmt_candidates() -> None:
    entries = entries_from_pairs(
        {"valid": ["válido", ""], "empty": [""], "": ["vacío"]},
        source_lang="en",
        target_lang="es",
    )
    assert [(entry.source, entry.target) for entry in entries] == [("valid", "válido")]


def test_benchmark_retrieves_only_terms_present_in_document() -> None:
    record = BenchmarkRecord(
        record_id="finance-1",
        domain="finance",
        source_lang="English",
        target_lang="Spanish",
        source="The central bank changed the base rate.",
        reference="El banco central modificó el tipo básico.",
        proper_terms=(
            GlossaryEntry("central bank", "banco central"),
            GlossaryEntry("deposit insurance", "seguro de depósitos"),
        ),
    )
    selected = _entries_for_mode(record, "proper")
    assert [entry.source for entry in selected] == ["central bank"]


def test_prepare_wmt25_track2_honors_limit(tmp_path: Path) -> None:
    source = tmp_path / "references"
    source.mkdir()
    rows = [
        {
            "en": "The central bank changed the base rate.",
            "zh": "中央銀行調整了基本利率。",
            "proper": {"central bank": ["中央銀行"]},
            "random": {"changed": ["調整了"]},
            "noterm": {},
        },
        {
            "en": "Deposits increased.",
            "zh": "存款增加。",
            "proper": {"deposits": ["存款"]},
            "random": {},
            "noterm": {},
        },
    ]
    (source / "full_data_2015.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    output = tmp_path / "prepared.jsonl"
    count = prepare_wmt25_track2(source, output, years=[2015], limit=1)
    assert count == 1
    assert len(output.read_text(encoding="utf-8").splitlines()) == 1
