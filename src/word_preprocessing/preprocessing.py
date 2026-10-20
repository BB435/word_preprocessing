"""Pure text normalization functions."""

import re
import unicodedata
from typing import Literal

SpaceRule = Literal["preserve", "single-character", "all"]
_JAPANESE = r"\u3041-\u3096\u30a1-\u30fa\u3400-\u4dbf\u4e00-\u9fff"


def normalize_text(text: str, *, space_rule: SpaceRule = "single-character") -> str:
    """Normalize text; by default join only runs of spaced single Japanese letters."""
    if space_rule not in {"preserve", "single-character", "all"}:
        raise ValueError("Unknown space rule")
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    if space_rule == "all":
        text = re.sub(rf"(?<=[{_JAPANESE}]) +(?=[{_JAPANESE}])", "", text)
    elif space_rule == "single-character":
        text = re.sub(
            rf"(?<!\w)[{_JAPANESE}](?: [{_JAPANESE}])+(?!\w)",
            lambda match: match.group().replace(" ", ""),
            text,
        )
    return text
