"""Sudachi morphology with a reusable full dictionary."""

from dataclasses import dataclass
from functools import lru_cache

from sudachipy import dictionary, tokenizer


@dataclass(frozen=True)
class Token:
    """A morpheme and its character offsets in normalized text."""

    surface: str
    normalized: str
    dictionary_form: str
    pos: tuple[str, ...]
    start: int
    end: int


@lru_cache(maxsize=1)
def _dictionary() -> dictionary.Dictionary:
    return dictionary.Dictionary(dict="full")


def analyze(text: str, *, mode: str = "C") -> list[Token]:
    """Analyze text in split mode A, B or C using the full dictionary."""
    if mode not in {"A", "B", "C"}:
        raise ValueError("mode must be A, B or C")
    worker = _dictionary().create()
    return [
        Token(m.surface(), m.normalized_form(), m.dictionary_form(),
              tuple(m.part_of_speech()), m.begin(), m.end())
        for m in worker.tokenize(text, getattr(tokenizer.Tokenizer.SplitMode, mode))
    ]
