# Book ISBN Extractor（日本語版）

書籍カバー画像からバーコード（EAN-13）を認識し、ISBN情報を自動抽出、外部APIで書籍情報を取得するPythonシステムです。

## 主な機能

- **バーコード認識**: pyzbarで書籍バーコード（EAN-13）を検出・デコード
- **ISBN抽出**: バーコードから978または979で始まる13桁のISBNを抽出
- **書籍情報取得**: Google Books APIから詳細情報を取得
- **CSV出力**: 収集データをCSV形式でエクスポート
- **エラー処理**: ログ出力による堅牢なエラー処理
- **重複排除**: ISBNの重複を自動的に除去

## 動作環境

### 必要なPythonパッケージ

以下のPythonパッケージが必要です（`requirements.txt`で自動インストールされます）：

- pyzbar
- opencv-python
- pandas
- requests
- numpy
- Pillow

バーコード認識には **zbar** 共有ライブラリも必要です：
- macOSの場合: Homebrewでインストール
  ```sh
  brew install zbar
  ```
  `Unable to find zbar shared library` というエラーが出る場合は、下記のようにパスを設定してください：
  ```sh
  export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
  ```
  （Homebrewが`/usr/local`の場合は `/usr/local/lib` を指定）
- Ubuntu/Debianの場合: aptでインストール
  ```sh
  sudo apt-get install libzbar0
  ```
- Windowsの場合: [pyzbar公式ドキュメント](https://github.com/NaturalHistoryMuseum/pyzbar#installation) を参照してください

## インストール方法

1. リポジトリをクローン:
```bash
git clone https://github.com/kuwaharu-git/book-isbn.git
cd book-isbn
```

2. Python依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使い方
```bash
python book_isbn_extractor.py /path/to/image/folder
```

### 詳細オプション
```bash
python book_isbn_extractor.py /path/to/image/folder -o output.csv --api-delay 1.5
```

### コマンドライン引数
- `folder_path`: 画像ファイルが入ったフォルダのパス（必須）
- `-o, --output`: 出力CSVファイル名（デフォルト: book_information.csv）
- `--api-delay`: API呼び出し間隔（秒、デフォルト: 1.0）

## 対応画像フォーマット
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## 出力CSVフォーマット

以下の列が含まれます:
- **ISBN**: 抽出されたISBN番号
- **Title**: 書籍タイトル
- **Authors**: 著者（カンマ区切り）
- **Publisher**: 出版社
- **Published Date**: 出版日
- **Description**: 書籍説明（省略あり）
- **Page Count**: ページ数
- **Language**: 言語
- **Source Files**: ISBNが見つかった画像ファイル名

## 処理の流れ
1. **フォルダスキャン**: 指定フォルダ内の対応画像ファイルを検索
2. **バーコード認識**: 画像からバーコードを検出・デコード
3. **ISBN抽出**: バーコードデータからISBNを抽出・検証
4. **重複排除**: 異なる画像間の重複ISBNを除去
5. **API呼び出し**: Google Books APIで書籍情報取得
6. **CSV出力**: 収集データをCSV保存

## エラー処理
- **読めない画像**: 警告をログ出力し処理継続
- **バーコード認識失敗**: エラーをログ出力し次の画像へ
- **API失敗**: エラーをログ出力し「情報なし」で出力
- **無効なISBN**: チェックサム検証
- **ネットワーク障害**: タイムアウト・リトライ機能

## ログ出力
`book_isbn_extractor.log`に詳細な処理状況・ISBN・API結果・エラー・警告を記録します。

## パフォーマンス
- **APIレート制限**: API呼び出し間隔を設定可能
- **画像サイズ最適化**: 大きな画像は自動リサイズ
- **メモリ管理**: 画像は1枚ずつ処理

## 使用例
### フォルダ内の書籍画像を処理:
```bash
python book_isbn_extractor.py ~/Desktop/book_photos
```
### 出力ファイル指定・API遅延指定:
```bash
python book_isbn_extractor.py ~/Desktop/book_photos -o my_books.csv --api-delay 2.0
```

## ライセンス
オープンソースです。詳細はLICENSEファイルをご覧ください。

## コントリビュート
貢献歓迎！Pull Requestをお待ちしています。
