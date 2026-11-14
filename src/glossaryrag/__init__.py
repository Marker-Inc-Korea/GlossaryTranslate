"""GlossaryRAG Translate public API."""

from .models import BenchmarkRecord, GlossaryEntry, TermMatch, TranslationResult
from .pipeline import GlossaryRAGTranslator
from .prompt import PromptBuilder, PromptConfig
from .retriever import TrieGlossaryRetriever

__all__ = [
    "BenchmarkRecord",
    "GlossaryEntry",
    "GlossaryRAGTranslator",
    "PromptBuilder",
    "PromptConfig",
    "TermMatch",
    "TranslationResult",
    "TrieGlossaryRetriever",
]

__version__ = "0.1.0"
