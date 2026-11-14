from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .models import GlossaryEntry


def normalized_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", value).strip()


@dataclass(frozen=True, slots=True)
class TermScore:
    matched: int
    total: int

    @property
    def rate(self) -> float:
        return self.matched / self.total if self.total else 0.0


def term_success(output: str, entries: Iterable[GlossaryEntry]) -> TermScore:
    normalized_output = normalized_text(output)
    matched = 0
    total = 0
    for entry in entries:
        total += 1
        if any(normalized_text(target) in normalized_output for target in entry.accepted_targets):
            matched += 1
    return TermScore(matched=matched, total=total)


def corpus_translation_metrics(
    predictions: Sequence[str],
    references: Sequence[str],
    *,
    target_language: str = "",
) -> dict[str, float]:
    if len(predictions) != len(references):
        raise ValueError("prediction and reference counts differ")
    try:
        import sacrebleu
    except ImportError as exc:
        raise RuntimeError("install the evaluation extra: pip install '.[eval]'") from exc
    bleu = sacrebleu.corpus_bleu(
        list(predictions),
        [list(references)],
        tokenize=bleu_tokenizer(target_language),
    )
    chrf = sacrebleu.corpus_chrf(list(predictions), [list(references)])
    return {"bleu": float(bleu.score), "chrf": float(chrf.score)}


def sentence_translation_metrics(
    prediction: str,
    reference: str,
    *,
    target_language: str = "",
) -> dict[str, float]:
    try:
        import sacrebleu
    except ImportError as exc:
        raise RuntimeError("install the evaluation extra: pip install '.[eval]'") from exc
    bleu = sacrebleu.sentence_bleu(
        prediction,
        [reference],
        tokenize=bleu_tokenizer(target_language),
    )
    chrf = sacrebleu.sentence_chrf(prediction, [reference])
    return {"bleu": float(bleu.score), "chrf": float(chrf.score)}


def bleu_tokenizer(target_language: str) -> str:
    normalized = normalized_text(target_language)
    if normalized.startswith("zh") or "chinese" in normalized:
        return "zh"
    return "13a"
