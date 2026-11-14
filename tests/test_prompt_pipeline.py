import json

from glossaryrag.client import StaticClient
from glossaryrag.models import GlossaryEntry
from glossaryrag.pipeline import GlossaryRAGTranslator


def test_pipeline_retrieves_and_delimits_glossary() -> None:
    translator = GlossaryRAGTranslator.from_entries(
        [GlossaryEntry("personal data", "datos personales")],
        client=StaticClient("Los datos personales están protegidos."),
    )
    result = translator.translate(
        "Personal data is protected.",
        source_language="English",
        target_language="Spanish",
        domain="privacy",
    )
    assert result.text.startswith("Los datos personales")
    assert len(result.matches) == 1
    user_prompt = result.messages[-1]["content"]
    assert "<glossary_data>" in user_prompt
    payload = user_prompt.split("<glossary_data>\n", 1)[1].split("\n</glossary_data>", 1)[0]
    assert json.loads(payload)[0]["target"] == "datos personales"


def test_unmatched_terms_are_not_injected() -> None:
    translator = GlossaryRAGTranslator.from_entries(
        [GlossaryEntry("patent", "patente")], client=StaticClient("Hola")
    )
    result = translator.translate(
        "Hello",
        source_language="English",
        target_language="Spanish",
    )
    assert result.matches == ()
    assert "patente" not in result.messages[-1]["content"]
