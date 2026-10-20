import pytest

from word_preprocessing.analysis import Token
from word_preprocessing.candidates import generate_candidates
from word_preprocessing.filtering import filter_tokens, load_stopwords


def noun(text, start, pos=("名詞", "普通名詞", "一般")):
    return Token(text, text, text, pos, start, start + len(text))


def test_spans_and_boundaries():
    tokens = filter_tokens([noun("情報", 0), noun("検索", 2), noun("除外", 4),
                            noun("技術", 6)], excluded_words=frozenset({"除外"}))
    candidates = generate_candidates(tokens, max_tokens=2)
    assert [c.text for c in candidates] == ["情報", "情報検索", "検索", "技術"]
    assert [(c.start, c.end) for c in candidates] == [(0, 2), (0, 4), (2, 4), (6, 8)]
    with pytest.raises(ValueError):
        generate_candidates(tokens, max_tokens=0)


def test_duplicates_and_offset_gap():
    tokens = filter_tokens([noun("情報", 0), noun("情報", 3)])
    assert len(generate_candidates(tokens)) == 2
    assert len(generate_candidates(tokens, deduplicate=True)) == 1


def test_filter_reasons_and_stopword_file(tmp_path):
    path = tmp_path / "stop.txt"
    path.write_text("\ufeff# comment\n\n検索\nＡＩ\n", encoding="utf-8")
    tokens = [noun("太郎", 0, ("名詞", "固有名詞", "人名")), noun("検索", 2),
              noun("技術", 4), noun("。", 6), noun(" ", 7)]
    marked = filter_tokens(tokens, stopwords=load_stopwords(path),
                           excluded_words=frozenset({"技術"}))
    assert [t.reason for t in marked] == ["person", "stopword", "user",
                                           "symbol_or_space", "symbol_or_space"]
    assert "AI" in load_stopwords(path)
