import pytest

from word_preprocessing.preprocessing import normalize_text


def test_normalization():
    original = "　ＡＢＣ  test\r\n日 本 語\r東京 大阪　"
    assert normalize_text(original) == "ABC test\n日本語\n東京 大阪"
    assert original.startswith("　ＡＢＣ")


@pytest.mark.parametrize("rule, expected", [
    ("preserve", "日 本 語"), ("single-character", "日本語"), ("all", "日本語"),
])
def test_space_rules(rule, expected):
    assert normalize_text("日 本 語", space_rule=rule) == expected
    assert normalize_text("New York  Python 3.14", space_rule=rule) == "New York Python 3.14"


def test_newlines_and_invalid_rule():
    assert normalize_text("日\n本", space_rule="all") == "日\n本"
    with pytest.raises(ValueError):
        normalize_text("x", space_rule="invalid")
