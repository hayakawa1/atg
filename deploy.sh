#!/bin/bash

# エラーが発生したら停止
set -e

echo "Starting deployment..."

# アプリケーションのディレクトリに移動
cd /var/www/atg

# 現在のプロセスを停止
echo "Stopping current application..."
pkill -f "gunicorn" || true

# Gitから最新のコードを取得
echo "Pulling latest code from Git..."
git pull origin main

# 環境変数ファイルが存在することを確認
if [ ! -f .env ]; then
    echo "Creating .env file from .env.production..."
    cp .env.production .env
fi

# 仮想環境が存在することを確認
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
echo "Activating virtual environment..."
source venv/bin/activate

# 依存関係をインストール
echo "Installing dependencies..."
pip install -r requirements.txt

# データベースディレクトリの確認
if [ ! -d "instance" ]; then
    echo "Creating instance directory..."
    mkdir -p instance
    chmod 777 instance
fi

# Gunicornでアプリケーションを起動
echo "Starting application with Gunicorn..."
cd /var/www/atg && PYTHONPATH=/var/www/atg nohup gunicorn --bind 0.0.0.0:3001 --workers 3 --timeout 120 'app:app' > flask.log 2>&1 &
disown

# Nginxの設定をテスト
echo "Testing Nginx configuration..."
sudo nginx -t

# Nginxを再起動
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Deployment completed successfully!"
