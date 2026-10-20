"""Japanese keyword extraction using SudachiPy and YAKE."""

from .pipeline import extract_keywords

__all__ = ["extract_keywords"]


def main() -> None:
    """Run the command line interface."""
    from .cli import main as cli_main

    cli_main()
