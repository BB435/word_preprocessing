"""Token exclusions that preserve boundaries and exclusion reasons."""

import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .analysis import Token


@dataclass(frozen=True)
class FilteredToken:
    """A token with an optional exclusion reason."""

    token: Token
    reason: str | None = None


def load_stopwords(path: str | Path) -> frozenset[str]:
    """Read UTF-8 words, ignoring blank lines and lines starting with #."""
    return frozenset(
        unicodedata.normalize("NFKC", line.strip())
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def filter_tokens(
    tokens: list[Token], *, stopwords: frozenset[str] = frozenset(),
    excluded_words: frozenset[str] = frozenset(), exclude_people: bool = True,
) -> list[FilteredToken]:
    """Mark excluded tokens without removing the boundaries they represent."""
    stopwords = frozenset(unicodedata.normalize("NFKC", w) for w in stopwords)
    excluded_words = frozenset(unicodedata.normalize("NFKC", w) for w in excluded_words)
    result = []
    for token in tokens:
        forms = {token.surface, token.normalized, token.dictionary_form}
        reason = None
        if not token.surface.strip() or all(
            unicodedata.category(c)[0] in {"P", "S", "Z", "C"} for c in token.surface
        ):
            reason = "symbol_or_space"
        elif exclude_people and token.pos[:3] == ("名詞", "固有名詞", "人名"):
            reason = "person"
        elif forms & excluded_words:
            reason = "user"
        elif forms & stopwords:
            reason = "stopword"
        result.append(FilteredToken(token, reason))
    return result
