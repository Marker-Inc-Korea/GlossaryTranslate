from glossaryrag.metrics import bleu_tokenizer, term_success
from glossaryrag.models import GlossaryEntry


def test_term_success_accepts_alternative_targets() -> None:
    score = term_success(
        "The output uses AI.",
        [GlossaryEntry("artificial intelligence", "인공지능", alternatives=("AI",))],
    )
    assert score.matched == 1
    assert score.rate == 1.0


def test_chinese_targets_use_chinese_bleu_tokenizer() -> None:
    assert bleu_tokenizer("Traditional Chinese") == "zh"
    assert bleu_tokenizer("zh") == "zh"
    assert bleu_tokenizer("Spanish") == "13a"
