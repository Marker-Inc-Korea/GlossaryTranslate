from pathlib import Path

from glossaryrag.loaders import load_csv, load_jsonl, load_tbx


def test_load_csv(tmp_path: Path) -> None:
    path = tmp_path / "terms.csv"
    path.write_text("source,target,priority\nspace,Space,3\n", encoding="utf-8")
    entries = load_csv(path)
    assert entries[0].source == "space"
    assert entries[0].priority == 3


def test_load_jsonl_alternatives(tmp_path: Path) -> None:
    path = tmp_path / "terms.jsonl"
    path.write_text(
        '{"source":"AI","target":"인공지능","alternatives":["AI"]}\n',
        encoding="utf-8",
    )
    entries = load_jsonl(path)
    assert entries[0].accepted_targets == ("인공지능", "AI")


def test_load_tbx(tmp_path: Path) -> None:
    path = tmp_path / "terms.tbx"
    path.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<martif><text><body><termEntry id="1">
<langSet xml:lang="en"><tig><term>data controller</term></tig></langSet>
<langSet xml:lang="es"><tig><term>responsable del tratamiento</term></tig></langSet>
</termEntry></body></text></martif>""",
        encoding="utf-8",
    )
    entries = load_tbx(path, source_lang="en", target_lang="es")
    assert len(entries) == 1
    assert entries[0].target == "responsable del tratamiento"
