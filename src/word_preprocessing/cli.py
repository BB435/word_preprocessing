"""Command line JSON output."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .filtering import load_stopwords
from .pipeline import extract_keywords


def main() -> None:
    """Extract keywords from a UTF-8 file, an argument or standard input."""
    parser = argparse.ArgumentParser(description="日本語キーワード抽出")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text")
    source.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mode", choices=["A", "B", "C"], default="C")
    parser.add_argument("--space-rule", choices=["preserve", "single-character", "all"],
                        default="single-character")
    parser.add_argument("--stopwords", type=Path)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--keep-people", action="store_true")
    parser.add_argument("--deduplicate", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--max-tokens", type=int, default=3)
    parser.add_argument("--max-ngram", type=int, default=3)
    args = parser.parse_args()
    try:
        text = (args.input.read_text(encoding="utf-8-sig") if args.input else
                args.text if args.text is not None else sys.stdin.read())
        result = extract_keywords(
            text, mode=args.mode, space_rule=args.space_rule,
            stopwords=load_stopwords(args.stopwords) if args.stopwords else frozenset(),
            excluded_words=frozenset(args.exclude), exclude_people=not args.keep_people,
            max_tokens=args.max_tokens, max_ngram=args.max_ngram, top=args.top,
            deduplicate=args.deduplicate,
        )
        output = json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (OSError, ValueError) as error:
        parser.error(str(error))
