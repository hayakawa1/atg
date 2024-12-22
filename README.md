# Al Talk Gallery (ATG)

URLベースのスレッド形式掲示板アプリケーション

## 機能

- Google OAuth 2.0による認証
- URL付きの投稿作成
- タグ付け機能
- タグベースの投稿フィルタリング
- レスポンシブデザイン

## 技術スタック

- バックエンド: Flask 2.3.3
- データベース: SQLite
- 認証: Google OAuth 2.0
- フロントエンド: Vanilla JavaScript, HTML/CSS

## セットアップ

1. リポジトリをクローン:
```bash
git clone [repository-url]
cd atg
```

2. Python仮想環境を作成し、有効化:
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
# または
.\venv\Scripts\activate  # Windows
```

3. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

4. 環境変数を設定:
- `.env`ファイルを作成し、必要な環境変数を設定
- Google OAuth 2.0の認証情報を設定

5. データベースを初期化:
```bash
flask db upgrade
```

6. アプリケーションを実行:
```bash
flask run --port 3000
```

## 環境変数

`.env`ファイルに以下の環境変数を設定:

```
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///atg.db
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 開発

1. データベースマイグレーション:
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

2. テスト:
```bash
python -m pytest
```

## ライセンス

MIT License 