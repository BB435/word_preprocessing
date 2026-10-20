"""YAKE scoring of noun sequences, constrained to generated candidates."""

from dataclasses import dataclass

import yake

from .candidates import Candidate
from .filtering import FilteredToken


@dataclass(frozen=True)
class Keyword:
    """A keyword score (smaller is better) and all matching noun spans."""

    keyword: str
    score: float
    occurrences: tuple[Candidate, ...]


def score_candidates(
    tokens: list[FilteredToken], candidates: list[Candidate], *,
    top: int = 20, max_ngram: int = 3,
) -> list[Keyword]:
    """Score spaced nouns with YAKE, using sentence breaks at excluded tokens."""
    if top < 1 or max_ngram < 1:
        raise ValueError("top and max_ngram must be positive")
    if not candidates:
        return []
    pieces = []
    for item in tokens:
        pieces.append(
            item.token.normalized
            if item.reason is None and item.token.pos[0] == "名詞" else "."
        )
    extractor = yake.KeywordExtractor(
        lan="ja", n=max_ngram, top=max(len(candidates), top),
        dedup_lim=1.0, stopwords=set(),
    )
    matches: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        matches.setdefault(candidate.normalized.casefold(), []).append(candidate)
    scores: dict[str, float] = {}
    for phrase, score in extractor.extract_keywords(" ".join(pieces)):
        key = "".join(phrase.split()).casefold()
        if key in matches:
            scores[key] = min(scores.get(key, float("inf")), float(score))
    return [
        Keyword(matches[key][0].normalized, score, tuple(matches[key]))
        for key, score in sorted(scores.items(), key=lambda pair: pair[1])[:top]
    ]
