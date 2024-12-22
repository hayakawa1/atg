from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os
from models import db, User
from dotenv import load_dotenv
import logging

# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///instance/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# デバッグログの設定
app.logger.setLevel(logging.DEBUG)

# データベースの初期化
db.init_app(app)
migrate = Migrate(app, db)

# ログイン管理の設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ルート設定
@app.route('/')
def index():
    return render_template('index.html')

# Blueprintの登録
from auth import auth
from api import api

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(api, url_prefix='/api')

# データベースの作成
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True) 