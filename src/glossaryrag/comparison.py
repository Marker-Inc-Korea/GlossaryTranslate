from __future__ import annotations

import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .io import read_jsonl
from .metrics import corpus_translation_metrics


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

    def score(sample: Sequence[dict[str, dict[str, Any]]]) -> dict[str, float]:
        references = [str(pair[baseline]["reference"]) for pair in sample]
        baseline_metrics = corpus_translation_metrics(
            [str(pair[baseline]["prediction"]) for pair in sample], references
        )
        treatment_metrics = corpus_translation_metrics(
            [str(pair[treatment]["prediction"]) for pair in sample], references
        )
        baseline_matched = sum(int(pair[baseline].get("term_matched") or 0) for pair in sample)
        treatment_matched = sum(int(pair[treatment].get("term_matched") or 0) for pair in sample)
        total = sum(int(pair[baseline].get("term_total") or 0) for pair in sample)
        baseline_term = baseline_matched / total if total else 0.0
        treatment_term = treatment_matched / total if total else 0.0
        return {
            "bleu_delta": treatment_metrics["bleu"] - baseline_metrics["bleu"],
            "chrf_delta": treatment_metrics["chrf"] - baseline_metrics["chrf"],
            "term_success_delta": treatment_term - baseline_term,
        }

    observed = score(pairs)
    rng = random.Random(seed)
    distributions = {name: [] for name in observed}
    for _ in range(bootstrap_samples):
        sample = [pairs[rng.randrange(len(pairs))] for _ in range(len(pairs))]
        sample_score = score(sample)
        for name, value in sample_score.items():
            distributions[name].append(value)

    return {
        "prediction_file": str(path),
        "baseline": baseline,
        "treatment": treatment,
        "paired_records": len(pairs),
        "bootstrap_samples": bootstrap_samples,
        "deltas": {
            name: {
                "observed": value,
                "ci95_low": _percentile(distributions[name], 0.025),
                "ci95_high": _percentile(distributions[name], 0.975),
            }
            for name, value in observed.items()
        },
    }
