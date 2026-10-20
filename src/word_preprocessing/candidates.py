"""Contiguous noun candidates."""

from dataclasses import dataclass

from .filtering import FilteredToken


@dataclass(frozen=True)
class Candidate:
    """A noun span, located in normalized text."""

    text: str
    normalized: str
    start: int
    end: int
    token_count: int


def generate_candidates(
    tokens: list[FilteredToken], *, max_tokens: int = 3, deduplicate: bool = False,
) -> list[Candidate]:
    """Generate all contiguous noun spans up to max_tokens, in source order."""
    if max_tokens < 1:
        raise ValueError("max_tokens must be positive")
    result: list[Candidate] = []
    seen: set[str] = set()
    for index, item in enumerate(tokens):
        span = []
        for next_item in tokens[index:index + max_tokens]:
            token = next_item.token
            if next_item.reason or token.pos[0] != "名詞":
                break
            if span and span[-1].end != token.start:
                break
            span.append(token)
            normalized = "".join(t.normalized for t in span)
            if not deduplicate or normalized not in seen:
                result.append(Candidate(
                    "".join(t.surface for t in span), normalized,
                    item.token.start, token.end, len(span),
                ))
                seen.add(normalized)
    return result
