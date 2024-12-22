from flask_login import UserMixin
from datetime import datetime
from app.models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref=db.backref('author', lazy=True), lazy=True)
    favorites = db.relationship('Post', secondary='favorites', lazy='dynamic',
        backref=db.backref('favorited_by', lazy=True)) 