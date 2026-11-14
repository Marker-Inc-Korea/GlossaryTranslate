from glossaryrag.metrics import term_success
from glossaryrag.models import GlossaryEntry


def test_term_success_accepts_alternative_targets() -> None:
    score = term_success(
        "The output uses AI.",
        [GlossaryEntry("artificial intelligence", "인공지능", alternatives=("AI",))],
    )
    assert score.matched == 1
    assert score.rate == 1.0
