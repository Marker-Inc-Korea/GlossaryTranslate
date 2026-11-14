from __future__ import annotations

import json
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from .client import OpenAICompatibleClient
from .io import append_jsonl, read_jsonl
from .metrics import corpus_translation_metrics, term_success
from .models import BenchmarkRecord, GlossaryEntry
from .prompt import PromptBuilder, PromptConfig
from .retriever import TrieGlossaryRetriever

MODES = ("no_term", "proper", "random")


def _entries_for_mode(record: BenchmarkRecord, mode: str) -> tuple[GlossaryEntry, ...]:
    if mode == "no_term":
        return ()
    if mode == "proper":
        candidates = record.proper_terms
    elif mode == "random":
        candidates = record.random_terms
    else:
        raise ValueError(f"unsupported mode: {mode}")
    if not candidates:
        return ()
    return tuple(match.entry for match in TrieGlossaryRetriever(candidates).match(record.source))


def run_benchmark(
    dataset_path: str | Path,
    output_path: str | Path,
    *,
    base_url: str,
    model: str,
    modes: Iterable[str] = MODES,
    api_key: str = "",
    workers: int = 1,
    max_tokens: int = 1_024,
    limit: int | None = None,
    disable_thinking: bool = False,
) -> dict[str, Any]:
    records = [BenchmarkRecord.from_dict(row) for row in read_jsonl(dataset_path)]
    if limit is not None:
        records = records[:limit]
    selected_modes = tuple(modes)
    invalid = set(selected_modes) - set(MODES)
    if invalid:
        raise ValueError(f"invalid modes: {sorted(invalid)}")
    output = Path(output_path)
    completed: set[tuple[str, str]] = set()
    if output.is_file():
        completed = {(str(row.get("id")), str(row.get("mode"))) for row in read_jsonl(output)}
    client = OpenAICompatibleClient(
        base_url=base_url,
        model=model,
        api_key=api_key,
        max_tokens=max_tokens,
        extra_body=(
            {"chat_template_kwargs": {"enable_thinking": False}} if disable_thinking else {}
        ),
    )
    prompt_builder = PromptBuilder()

    def execute(record: BenchmarkRecord, mode: str) -> dict[str, Any]:
        terms = _entries_for_mode(record, mode)
        expected_terms = _entries_for_mode(record, "proper")
        messages = prompt_builder.build(
            record.source,
            terms,
            PromptConfig(
                source_language=record.source_lang,
                target_language=record.target_lang,
                domain=record.domain,
            ),
        )
        started = time.perf_counter()
        prediction = client.complete(messages)
        elapsed = time.perf_counter() - started
        score = term_success(prediction, expected_terms)
        return {
            "id": record.record_id,
            "mode": mode,
            "domain": record.domain,
            "source_lang": record.source_lang,
            "target_lang": record.target_lang,
            "source": record.source,
            "reference": record.reference,
            "prediction": prediction,
            "proper_terms": [entry.to_dict() for entry in expected_terms],
            "provided_terms": [entry.to_dict() for entry in terms],
            "term_matched": score.matched,
            "term_total": score.total,
            "elapsed_seconds": elapsed,
            "model": model,
        }

    tasks = [
        (record, mode)
        for record in records
        for mode in selected_modes
        if (record.record_id, mode) not in completed
    ]
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(execute, record, mode): (record.record_id, mode)
            for record, mode in tasks
        }
        for future in as_completed(futures):
            append_jsonl(output, future.result())
    return score_predictions(output)


def score_predictions(path: str | Path) -> dict[str, Any]:
    rows = list(read_jsonl(path))
    report: dict[str, Any] = {"prediction_file": str(path), "rows": len(rows), "modes": {}}
    for mode in MODES:
        selected = [row for row in rows if row.get("mode") == mode]
        if not selected:
            continue
        metrics = corpus_translation_metrics(
            [str(row["prediction"]) for row in selected],
            [str(row["reference"]) for row in selected],
        )
        term_matched = sum(int(row.get("term_matched") or 0) for row in selected)
        term_total = sum(int(row.get("term_total") or 0) for row in selected)
        metrics.update(
            {
                "records": len(selected),
                "term_success_rate": term_matched / term_total if term_total else 0.0,
                "term_matched": term_matched,
                "term_total": term_total,
                "mean_elapsed_seconds": sum(float(row["elapsed_seconds"]) for row in selected)
                / len(selected),
            }
        )
        report["modes"][mode] = metrics
    report_path = Path(path).with_suffix(".metrics.json")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
