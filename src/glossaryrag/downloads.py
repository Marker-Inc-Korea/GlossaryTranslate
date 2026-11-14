from __future__ import annotations

import json
import urllib.request
from collections.abc import Iterable
from pathlib import Path

WMT25_RAW = "https://raw.githubusercontent.com/wmt-conference/wmt25-terminology/main"
TICO19_RAW = "https://raw.githubusercontent.com/tico-19/tico-19.github.io/master/data"


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as response:
        destination.write_bytes(response.read())


def download_wmt25(destination: str | Path) -> Path:
    root = Path(destination)
    files: list[str] = [
        "ranking/references/track1/full_data.ende.jsonl",
        "ranking/references/track1/full_data.enes.jsonl",
        "ranking/references/track1/full_data.enru.jsonl",
        *[f"ranking/references/track2/full_data_{year}.jsonl" for year in range(2015, 2025)],
        "LICENSE.txt",
    ]
    for relative in files:
        _download(f"{WMT25_RAW}/{relative}", root / relative)
    (root / "SOURCE.json").write_text(
        json.dumps(
            {
                "name": "WMT25 Terminology Shared Task",
                "source": "https://github.com/wmt-conference/wmt25-terminology",
                "license": "CC BY-NC 4.0",
                "redistributed": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def download_tico19(destination: str | Path, *, languages: Iterable[str]) -> Path:
    root = Path(destination)
    _download(f"{TICO19_RAW}/tico19-testset.zip", root / "tico19-testset.zip")
    terminology_names = {
        "ar": "f_en-ar_AR.csv",
        "es-LA": "f_en-es_XX.csv",
        "fr": "f_en-fr_XX.csv",
        "pt-BR": "f_en-pt_XX.csv",
        "ru": "f_en-ru_RU.csv",
        "zh": "f_en-zh_CN.csv",
    }
    for language in languages:
        name = terminology_names.get(language)
        if name is None:
            raise ValueError(f"unsupported TICO-19 terminology language: {language}")
        _download(f"{TICO19_RAW}/terminologies/{name}", root / "terminologies" / name)
    _download(
        "https://raw.githubusercontent.com/tico-19/tico-19.github.io/master/LICENSE.md",
        root / "LICENSE.md",
    )
    (root / "SOURCE.json").write_text(
        json.dumps(
            {
                "name": "TICO-19",
                "source": "https://tico-19.github.io/",
                "license": "CC0-1.0",
                "redistributed": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return root
