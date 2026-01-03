## mog-excel-to-pdf

Excel ブック内の複数シートをグループ選択し、1 つの PDF にまとめて出力します。COM 経由で Excel を操作するため Windows + Microsoft Excel 環境が必須です。

![ツール概要](images/pic.png)

### 前提
- Windows（COM 経由で Excel を操作します）
- Microsoft Excel がインストールされていること
- Python 3.11 以上

### インストール（uv ベース）

PyPI からインストールする場合:

```bash
uv tool install mog-excel-to-pdf
```

リポジトリ直下の開発版を使う場合:

```bash
uv tool install --force -e .   # カレントリポジトリをツールとして登録
```

### 使い方
1. `config.toml`（または任意の TOML）を用意します（サンプルは `sample_config.toml` を参照）。
2. PowerShell / cmd から実行します。

```bash
mog-excel-to-pdf config.toml
```

### 設定ファイル例（TOML）

```toml
# 単一ファイル
excel_path = "example.xlsx"
# または複数ファイル（指定順に統合）
# excel_path = ["file1.xlsx", "file2.xlsx"]

sheets = "all"              # "all" もしくは ["Sheet1", "Sheet2"] のようにリストで指定
exclude_sheets = ["tmp"]    # 除外したいシート名（省略可）
exclude_suffixes = ["(2)"]  # サフィックスで除外（複数ファイル統合時にコピーシートが "(2)" 等になる場合に使用、省略可）
pdf_filename = "まとめ.pdf" # 出力する PDF 名（拡張子は自動付与）
output_dir = "pdf_out"      # 出力フォルダ（省略時は最初の Excel ファイルと同じ場所）
log_file = "output.log"     # ログファイル（省略時は出力フォルダ直下の excel_grouped_to_pdf.log）
open_after_publish = false  # true なら出力後に自動で開く
include_hidden = true       # 非表示/VeryHidden のシートも対象に含める
sort_sheets = false         # true ならシート名を辞書順でソートしてから PDF 化（省略可）
```

設定のポイント:
- `excel_path` は必須。単一ファイルは文字列、複数ファイルはリストで指定。複数指定時は指定順に統合して1つの PDF を生成します。
- `sheets` が必須。`"all"` かシート名リストを指定します（複数ファイルでも同じシート設定が適用されます）。
- `exclude_sheets` は `sheets` で指定した対象から完全一致で除外します。
- `exclude_suffixes` は複数ファイル統合時にコピーされたシートが "(2)" などのサフィックスを持つ場合に、それらを除外するリスト（完全後方一致）です。
- `pdf_filename` は無効文字を `_` に置換し、`.pdf` を末尾に付けて保存します。
- `output_dir`、`log_file` は省略可（デフォルト動作は以下）。
  - 出力フォルダ：最初の Excel ファイルと同じディレクトリ。
  - ログファイル：出力フォルダ直下の `excel_grouped_to_pdf.log`。
- `include_hidden` が `true` の場合、一時的にシートを可視化してから PDF 化し、終了時に元の表示状態へ戻します。
- `open_after_publish` が `true` なら、PDF 生成後に既定のビューアで開きます。
- `sort_sheets` が `true` の場合、対象シートを名前順（辞書順）でソートしてから PDF を出力します。複数ファイルの場合も、全ファイルのシートをまとめてソートします。

### 注意: COM 処理の終了時メッセージについて

実行後、以下のようなエラーメッセージが表示されることがあります：

```
Windows fatal exception: code 0x80010108
...
```

このメッセージは **PDF 生成や処理自体には影響しません**。Excel COM API の終了処理時に発生する一時的なノイズです。すべての処理が正常に完了し、PDF は正しく生成されています。エラーメッセージは無視して問題ありません。

### 実行後の挙動
- 対象シートをグループ選択して 1 つの PDF を生成します（印刷範囲は Excel 側の設定を尊重）。
- ログは標準出力とファイルの両方へ同一内容を出力します。
- `open_after_publish=true` が設定されていれば、PDF 生成後に既定のビューアで開きます。

### よくあるトラブル
- Excel の COM を取得できない場合: Excel を閉じてから再実行するか、`python -m win32com.client.makepy` で Microsoft Excel Object Library を生成してください。
- 非表示シートが PDF に含まれない: `include_hidden = true` を設定してください。

### ライセンス
MIT License（同梱の LICENSE を参照）。

コーヒーをお恵みくださると私が泣いて喜びます。(Click here)
[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mogwai.dev)
