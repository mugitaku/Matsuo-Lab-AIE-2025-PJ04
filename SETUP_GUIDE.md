# セットアップガイド

## 必要な環境
- Python 3.10以上
- Google Gemini API キー

## セットアップ手順

### 1. 仮想環境の作成と有効化
```bash
# uvを使用する場合
uv venv
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# pipを使用する場合
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 2. 依存パッケージのインストール
```bash
# uvを使用する場合
uv pip install -r requirements.txt

# pipを使用する場合
pip install -r requirements.txt
```

### 3. 環境変数の設定
1. `.env.example` を `.env` にコピー
   ```bash
   cp .env.example .env
   ```

2. `.env` ファイルを編集し、Google Gemini API キーを設定
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 4. アプリケーションの起動
```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセス

## 使い方

### 1. 質問データの読み込み
- 「サンプルデータを読み込む」ボタンをクリックして、サンプルの質問データを読み込む
- または、ExcelファイルやJSONファイルをアップロード

### 2. クラスタの確認
- 左側のパネルに、類似質問がグループ化されたクラスタが表示される
- クラスタをクリックすると、そのクラスタ内の全質問が表示される

### 3. 要約と回答の生成
- クラスタを選択すると、自動的にAIが要約と回答案を生成
- 「回答を再生成」ボタンで、新しい回答案を生成可能
- 「回答をコピー」ボタンで、生成された回答をクリップボードにコピー

## トラブルシューティング

### Gemini APIエラーが発生する場合
1. APIキーが正しく設定されているか確認
2. APIキーが有効であることを確認
3. インターネット接続を確認

### クラスタリングが機能しない場合
1. scikit-learnが正しくインストールされているか確認
2. 質問データの形式が正しいか確認（タイムスタンプ、質問、回答の列が必要）

## パフォーマンスチューニング

### 大量の質問（1000件以上）を処理する場合
1. `clustering.py` の `similarity_threshold` を調整（デフォルト: 0.7）
   - 値を上げると、より厳密なクラスタリング（クラスタ数が増える）
   - 値を下げると、より緩いクラスタリング（クラスタ数が減る）

2. バッチ処理の実装（将来的な拡張）
   - 現在は全質問を一度に処理
   - 必要に応じて、チャンク単位での処理を実装可能