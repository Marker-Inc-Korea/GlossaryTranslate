import json

import pytest

from glossaryrag.comparison import compare_prediction_modes


def test_compare_prediction_modes_returns_paired_deltas(tmp_path):
    path = tmp_path / "predictions.jsonl"
    rows = [
        {
            "id": "a",
            "mode": "no_term",
            "reference": "alpha beta",
            "prediction": "alpha",
            "term_matched": 0,
            "term_total": 1,
        },
        {
            "id": "a",
            "mode": "proper",
            "reference": "alpha beta",
            "prediction": "alpha beta",
            "term_matched": 1,
            "term_total": 1,
        },
        {
            "id": "b",
            "mode": "no_term",
            "reference": "gamma delta",
            "prediction": "gamma",
            "term_matched": 0,
            "term_total": 1,
        },
        {
            "id": "b",
            "mode": "proper",
            "reference": "gamma delta",
            "prediction": "gamma delta",
            "term_matched": 1,
            "term_total": 1,
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    report = compare_prediction_modes(path, bootstrap_samples=20)

    assert report["paired_records"] == 2
    assert report["deltas"]["chrf_delta"]["observed"] > 0
    assert report["deltas"]["term_success_delta"]["observed"] == pytest.approx(1.0)


def test_compare_prediction_modes_requires_pairs(tmp_path):
    path = tmp_path / "predictions.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "a",
                "mode": "no_term",
                "reference": "alpha",
                "prediction": "alpha",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no paired"):
        compare_prediction_modes(path, bootstrap_samples=1)
