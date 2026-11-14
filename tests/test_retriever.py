from glossaryrag.models import GlossaryEntry
from glossaryrag.retriever import RetrievalConfig, TrieGlossaryRetriever


def test_longest_overlap_wins_and_source_order_is_preserved() -> None:
    retriever = TrieGlossaryRetriever(
        [
            GlossaryEntry("controller", "responsable"),
            GlossaryEntry("data controller", "responsable del tratamiento"),
            GlossaryEntry("personal data", "datos personales"),
        ]
    )
    matches = retriever.match("The data controller processes personal data.")
    assert [match.entry.source for match in matches] == ["data controller", "personal data"]


def test_case_insensitive_by_default_and_limit_is_optional() -> None:
    retriever = TrieGlossaryRetriever([GlossaryEntry("COVID-19", "COVID-19")])
    assert len(retriever.match("covid-19 guidance")) == 1
    assert retriever.match("covid-19 guidance", max_terms=0) == ()


def test_case_sensitive_mode() -> None:
    retriever = TrieGlossaryRetriever(
        [GlossaryEntry("APP", "APP")],
        config=RetrievalConfig(case_sensitive=True),
    )
    assert retriever.match("app") == ()
    assert len(retriever.match("APP")) == 1
