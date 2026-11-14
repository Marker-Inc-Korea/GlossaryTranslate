from __future__ import annotations

import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .io import read_jsonl
from .metrics import sentence_translation_metrics


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot calculate a percentile of an empty sequence")
    index = (len(ordered) - 1) * quantile
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def compare_prediction_modes(
    path: str | Path,
    *,
    baseline: str = "no_term",
    treatment: str = "proper",
    bootstrap_samples: int = 1_000,
    seed: int = 17,
) -> dict[str, Any]:
    by_id: dict[str, dict[str, dict[str, Any]]] = {}
    for row in read_jsonl(path):
        mode = str(row.get("mode"))
        if mode in {baseline, treatment}:
            by_id.setdefault(str(row["id"]), {})[mode] = row
    pairs = [modes for modes in by_id.values() if baseline in modes and treatment in modes]
    if not pairs:
        raise ValueError(f"no paired {baseline}/{treatment} predictions in {path}")

    paired_deltas: list[dict[str, float]] = []
    target_languages = set()
    for pair in pairs:
        baseline_row = pair[baseline]
        treatment_row = pair[treatment]
        target_language = str(baseline_row.get("target_lang") or "")
        if target_language != str(treatment_row.get("target_lang") or ""):
            raise ValueError("paired predictions have different target languages")
        target_languages.add(target_language)
        reference = str(baseline_row["reference"])
        baseline_metrics = sentence_translation_metrics(
            str(baseline_row["prediction"]),
            reference,
            target_language=target_language,
        )
        treatment_metrics = sentence_translation_metrics(
            str(treatment_row["prediction"]),
            reference,
            target_language=target_language,
        )
        baseline_total = int(baseline_row.get("term_total") or 0)
        treatment_total = int(treatment_row.get("term_total") or 0)
        baseline_term = (
            int(baseline_row.get("term_matched") or 0) / baseline_total
            if baseline_total
            else 0.0
        )
        treatment_term = (
            int(treatment_row.get("term_matched") or 0) / treatment_total
            if treatment_total
            else 0.0
        )
        paired_deltas.append(
            {
                "bleu_delta": treatment_metrics["bleu"] - baseline_metrics["bleu"],
                "chrf_delta": treatment_metrics["chrf"] - baseline_metrics["chrf"],
                "term_success_delta": treatment_term - baseline_term,
            }
        )
    if len(target_languages) != 1:
        raise ValueError(
            f"prediction file mixes target languages: {sorted(target_languages)}; "
            "compare each direction separately"
        )

    observed = {
        name: sum(row[name] for row in paired_deltas) / len(paired_deltas)
        for name in paired_deltas[0]
    }
    rng = random.Random(seed)
    distributions = {name: [] for name in observed}
    for _ in range(bootstrap_samples):
        sample = [paired_deltas[rng.randrange(len(paired_deltas))] for _ in paired_deltas]
        for name in observed:
            distributions[name].append(sum(row[name] for row in sample) / len(sample))

    return {
        "prediction_file": str(path),
        "baseline": baseline,
        "treatment": treatment,
        "paired_records": len(pairs),
        "bootstrap_samples": bootstrap_samples,
        "estimator": "paired mean of per-record metric deltas",
        "deltas": {
            name: {
                "observed": value,
                "ci95_low": _percentile(distributions[name], 0.025),
                "ci95_high": _percentile(distributions[name], 0.975),
            }
            for name, value in observed.items()
        },
    }
