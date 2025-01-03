from flask import Blueprint, session, redirect, url_for, current_app, request
from flask_login import login_user, logout_user, login_required
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
from models import db, User
import os
from dotenv import load_dotenv
import json

# 環境変数の読み込み
load_dotenv()

# 環境変数からベースURLを取得
BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
REDIRECT_URI = f'{BASE_URL}/auth/callback'

auth = Blueprint('auth', __name__)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# スコープを修正
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

@auth.route('/login')
def login():
    # セッションをクリア
    session.clear()
    
    # デバッグ用のログ出力
    current_app.logger.debug(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
    current_app.logger.debug(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET}")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,  # 修正したスコープを使用
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@auth.route('/callback')
def callback():
    # デバッグログを追加
    current_app.logger.debug(f"Request URL: {request.url}")
    current_app.logger.debug(f"Headers: {request.headers}")
    current_app.logger.debug(f"REDIRECT_URI: {REDIRECT_URI}")
    
    # HTTPS経由でのリクエストURLを構築
    scheme = 'https'
    host = request.headers.get('X-Forwarded-Host', request.host)
    path = request.full_path
    authorization_response = f'{scheme}://{host}{path}'
    
    current_app.logger.debug(f"Authorization Response: {authorization_response}")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    flow.fetch_token(
        authorization_response=authorization_response,
        state=session['state']
    )
    
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
        requests.Request(),
        GOOGLE_CLIENT_ID
    )
    
    email = id_info.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        user = User(
            google_id=id_info['sub'],
            name=id_info['name'],
            email=email,
            profile_pic=id_info.get('picture')
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))