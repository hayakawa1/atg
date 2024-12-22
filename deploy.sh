#!/bin/bash

# Gitから最新のコードを取得
git pull origin main

# 本番環境の.envファイルをコピー
cp .env.production .env

# アプリケーションを再起動
pkill -f "python3 app.py"
nohup python3 app.py > flask.log 2>&1 &
