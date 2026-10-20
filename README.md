# word-preprocessing

Python 3.14以降向けの日本語キーワード抽出ライブラリ・CLIです。
SudachiPyのfull辞書で解析し、連続名詞候補をYAKEでスコアリングします。

```powershell
uv sync
uv run word-preprocessing --text "自然言語処理と機械学習を研究する。自然言語処理を活用する。"
uv run word-preprocessing --input input.txt --output result.json --mode C --top 10
uv run word-preprocessing --input input.txt --stopwords stopwords.txt --exclude 研究
```

入力指定がなければ標準入力を読み込みます。ファイルはUTF-8です。
初回セットアップでは容量の大きなfull辞書をダウンロードします。

```python
from word_preprocessing import extract_keywords

result = extract_keywords("日 本 語の自然言語処理を研究する。")
for keyword in result.keywords:
    print(keyword.keyword, keyword.score)
```

JSONには元テキスト、正規化テキスト、除外理由付き形態素、候補、キーワードとスコアを含めます。
候補とキーワード出現位置のstart/endは**正規化テキスト**上の文字位置（終端を含まない）です。
元テキストは保持しますが、正規化前後の文字位置変換は提供しません。

空白処理は `--space-rule single-character` が既定です。単独の日本語文字を空白で
並べた列（例: `日 本 語`）だけを結合し、`東京 大阪` や `New York` の空白を保持します。
意味のある一文字語の区切りも結合し得るため、`preserve` で削除を無効にできます。
`all` は日本語文字間の水平空白をすべて除去します。改行は維持します。

分割モードは `--mode A/B/C`、既定はCです。人名品詞を既定で除外し、
`--keep-people` で解除できます。未知の人名の完全な除外は保証しません。
ストップワードファイルは1行1語、空行と `#` で始まる行を無視します。
表層形・正規化形・基本形のいずれかに完全一致すると除外します。

候補は連続名詞のすべての部分列を出現順で生成します。上限は `--max-tokens`（既定3）です。
除外語・非名詞・空白をまたいで結合しません。数詞も名詞なら含め、
接頭辞・接尾辞や助詞を越える特別な結合は行いません。
`--deduplicate` は候補一覧を正規化形で重複排除します。キーワードの全出現位置は保持します。

YAKEには正規化名詞を空白で区切って渡し、非名詞・除外語を句境界にします。
`--max-ngram`（既定3）はYAKEへ渡す形態素の最大数です。
結果を候補辞書で絞り込み、スコア昇順（小さいほど重要）で返します。
YAKE自身の内部処理で候補が除外される場合があり、指定件数より少なくなることがあります。
日本語に対する抽出品質・スコアの安定性およびPrecision/Recall/F1評価は今後の検証対象です。

```powershell
uv run pytest
uv run ruff check .
```
