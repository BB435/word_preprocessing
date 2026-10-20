import json
import subprocess
import sys

import pytest

from word_preprocessing import extract_keywords
from word_preprocessing.analysis import _dictionary, analyze

TEXT = "田中太郎は自然言語処理を研究する。自然言語処理と機械学習を活用する。"


def test_real_pipeline():
    result = extract_keywords(TEXT, excluded_words=frozenset({"研究"}), deduplicate=True)
    assert result.original_text == TEXT
    assert any(t.reason == "person" for t in result.tokens)
    assert all("田中" not in c.text and "研究" not in c.text for c in result.candidates)
    assert result.keywords
    assert [k.score for k in result.keywords] == sorted(k.score for k in result.keywords)
    keyword = next(k for k in result.keywords if k.keyword == "自然言語処理")
    assert len(keyword.occurrences) == 2
    for candidate in result.candidates:
        assert result.normalized_text[candidate.start:candidate.end] == candidate.text


@pytest.mark.parametrize("mode", ["A", "B", "C"])
def test_modes(mode):
    assert "".join(t.surface for t in analyze("国家公務員", mode=mode)) == "国家公務員"
    assert _dictionary() is _dictionary()


def test_empty_and_invalid_configuration():
    assert extract_keywords("").keywords == ()
    with pytest.raises(ValueError):
        extract_keywords(TEXT, mode="D")
    with pytest.raises(ValueError):
        extract_keywords("", top=0)


def test_cli_json(tmp_path):
    source = tmp_path / "input.txt"
    output = tmp_path / "output.json"
    source.write_text(TEXT, encoding="utf-8")
    process = subprocess.run(
        [sys.executable, "-m", "word_preprocessing", "--input", str(source),
         "--output", str(output), "--top", "2"], capture_output=True, check=False,
    )
    assert process.returncode == 0, process.stderr
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["original_text"] == TEXT
    assert 0 < len(result["keywords"]) <= 2


def test_cli_invalid_count():
    process = subprocess.run(
        [sys.executable, "-m", "word_preprocessing", "--text", "", "--top", "0"],
        capture_output=True, check=False,
    )
    assert process.returncode == 2
