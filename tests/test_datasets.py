import json
from pathlib import Path

from glossaryrag.datasets.wmt25 import prepare_wmt25_track1
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
