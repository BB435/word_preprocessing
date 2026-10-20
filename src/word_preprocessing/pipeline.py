"""End-to-end extraction pipeline."""

from dataclasses import dataclass

from .analysis import analyze
from .candidates import Candidate, generate_candidates
from .filtering import FilteredToken, filter_tokens
from .preprocessing import SpaceRule, normalize_text
from .scoring import Keyword, score_candidates


@dataclass(frozen=True)
class ExtractionResult:
    """Original text, normalized text, traceable candidates and ranked keywords."""

    original_text: str
    normalized_text: str
    tokens: tuple[FilteredToken, ...]
    candidates: tuple[Candidate, ...]
    keywords: tuple[Keyword, ...]


def extract_keywords(
    text: str, *, mode: str = "C", space_rule: SpaceRule = "single-character",
    stopwords: frozenset[str] = frozenset(), excluded_words: frozenset[str] = frozenset(),
    exclude_people: bool = True, max_tokens: int = 3, max_ngram: int = 3,
    top: int = 20, deduplicate: bool = False,
) -> ExtractionResult:
    """Normalize, analyze, filter, generate noun spans and score with YAKE."""
    normalized = normalize_text(text, space_rule=space_rule)
    tokens = filter_tokens(analyze(normalized, mode=mode), stopwords=stopwords,
                           excluded_words=excluded_words, exclude_people=exclude_people)
    occurrences = generate_candidates(tokens, max_tokens=max_tokens)
    candidates = (generate_candidates(tokens, max_tokens=max_tokens, deduplicate=True)
                  if deduplicate else occurrences)
    keywords = score_candidates(tokens, occurrences, top=top, max_ngram=max_ngram)
    return ExtractionResult(text, normalized, tuple(tokens), tuple(candidates), tuple(keywords))
