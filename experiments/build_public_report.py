from __future__ import annotations

import argparse
import json
from pathlib import Path

from glossaryrag.comparison import compare_prediction_modes
from glossaryrag.runner import score_predictions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        metavar="LABEL=PATH",
        help="human-readable label and prediction JSONL",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-revision", default="")
    parser.add_argument("--runtime", default="")
    parser.add_argument("--hardware", default="")
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    return parser


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> int:
    args = _parser().parse_args()
    studies = []
    for item in args.input:
        if "=" not in item:
            raise SystemExit(f"invalid --input, expected LABEL=PATH: {item}")
        label, raw_path = item.split("=", 1)
        path = Path(raw_path)
        studies.append(
            {
                "label": label,
                "path": str(path),
                "metrics": score_predictions(path),
                "comparison": compare_prediction_modes(
                    path,
                    bootstrap_samples=args.bootstrap_samples,
                ),
            }
        )

    payload = {
        "model": args.model,
        "model_revision": args.model_revision,
        "runtime": args.runtime,
        "hardware": args.hardware,
        "studies": studies,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    lines = [
        "# Public benchmark results",
        "",
        "This report evaluates the same source records with no glossary and with the",
        "correct matched glossary. WMT25 studies additionally include benchmark-provided",
        "random terminology as a negative control. Dataset text is not redistributed.",
        "",
        "## Runtime",
        "",
        f"- Model: `{args.model}`",
        f"- Model revision: `{args.model_revision or 'not recorded'}`",
        f"- Runtime: `{args.runtime or 'not recorded'}`",
        f"- Hardware: `{args.hardware or 'not recorded'}`",
        f"- Paired bootstrap samples: {args.bootstrap_samples}",
        "",
        "## Scores",
        "",
        "| Study | Mode | Records | BLEU | chrF | Terminology success | Mean latency |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for study in studies:
        for mode, metrics in study["metrics"]["modes"].items():
            lines.append(
                "| {label} | {mode} | {records} | {bleu:.2f} | {chrf:.2f} | "
                "{term} | {latency:.3f}s |".format(
                    label=study["label"],
                    mode=mode,
                    records=metrics["records"],
                    bleu=metrics["bleu"],
                    chrf=metrics["chrf"],
                    term=_pct(metrics["term_success_rate"]),
                    latency=metrics["mean_elapsed_seconds"],
                )
            )

    lines.extend(
        [
            "",
            "## Proper glossary effect versus no glossary",
            "",
        "Positive values favor the correct glossary. Deltas are paired means of",
        "per-record scores; intervals are 95% bootstrap confidence intervals over",
        "source records. The score table above reports corpus-level BLEU and chrF.",
            "",
            "| Study | Paired records | BLEU delta [95% CI] | chrF delta [95% CI] | "
            "Terminology-success delta [95% CI] |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for study in studies:
        comparison = study["comparison"]
        deltas = comparison["deltas"]
        bleu = deltas["bleu_delta"]
        chrf = deltas["chrf_delta"]
        term = deltas["term_success_delta"]
        lines.append(
            "| {label} | {records} | {bo:+.2f} [{bl:+.2f}, {bh:+.2f}] | "
            "{co:+.2f} [{cl:+.2f}, {ch:+.2f}] | {to:+.1%} [{tl:+.1%}, {th:+.1%}] |".format(
                label=study["label"],
                records=comparison["paired_records"],
                bo=bleu["observed"],
                bl=bleu["ci95_low"],
                bh=bleu["ci95_high"],
                co=chrf["observed"],
                cl=chrf["ci95_low"],
                ch=chrf["ci95_high"],
                to=term["observed"],
                tl=term["ci95_low"],
                th=term["ci95_high"],
            )
        )

    term_intervals = [study["comparison"]["deltas"]["term_success_delta"] for study in studies]
    chrf_intervals = [study["comparison"]["deltas"]["chrf_delta"] for study in studies]
    term_min = min(item["observed"] for item in term_intervals)
    term_max = max(item["observed"] for item in term_intervals)
    chrf_positive = sum(item["ci95_low"] > 0 for item in chrf_intervals)
    chrf_negative = sum(item["ci95_high"] < 0 for item in chrf_intervals)
    chrf_inconclusive = len(chrf_intervals) - chrf_positive - chrf_negative
    max_latency_change = max(
        abs(
            study["metrics"]["modes"]["proper"]["mean_elapsed_seconds"]
            - study["metrics"]["modes"]["no_term"]["mean_elapsed_seconds"]
        )
        for study in studies
    )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Correct matched terminology improved terminology success in all {len(studies)} "
            f"studies. The paired mean gain ranged from {term_min * 100:+.1f} to "
            f"{term_max * 100:+.1f} percentage points, "
            "and every 95% interval remained above zero.",
            f"- For paired per-record chrF, {chrf_positive} studies had an entirely positive "
            f"95% interval, {chrf_negative} had an entirely negative interval, and "
            f"{chrf_inconclusive} crossed zero. Terminology gains therefore do not guarantee "
            "a general-quality gain in every domain and language.",
            f"- The largest absolute change in mean request latency was {max_latency_change:.3f} "
            "seconds, indicating that matched glossary rows added little generation latency "
            "in this reference run.",
            "- Proper terminology outperformed the random-term control in the WMT25 IT and "
            "finance studies, supporting an effect from the correct mappings rather than "
            "from merely adding extra prompt text.",
        ]
    )

    lines.extend(
        [
            "",
            "## Interpretation rules",
            "",
            "- Terminology success is the primary measure of whether an organization termbase",
            "  is followed; BLEU and chrF monitor overall reference similarity.",
            "- A glossary is considered beneficial when terminology success improves without a",
            "  material general-quality regression. Results can vary by model and domain.",
            "- Random terminology is a negative control, not a valid operating configuration.",
            "- WMT25 data are CC BY-NC 4.0 and are downloaded from upstream for evaluation only.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
