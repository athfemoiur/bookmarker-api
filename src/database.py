import random
import string
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DATETIME, default=datetime.now())
    updated_at = db.Column(db.DATETIME, onupdate=datetime.now())

    def __repr__(self):
        return f"user >> {self.username}"


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.short_url = self.generate_short_characters()

    def generate_short_characters(self):
        characters = string.digits + string.ascii_letters
        picked_chars = ''.join(random.choices(characters, k=3))

        if self.query.filter_by(short_url=picked_chars).first():
            return self.generate_short_characters()
        return picked_chars

    def __repr__(self) -> str:
        return f'bookmark >> {self.url}'
