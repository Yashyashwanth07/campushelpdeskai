from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='student')  # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.now)

    complaints = db.relationship('Complaint', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Resolved
    sentiment = db.Column(db.String(20), default='Neutral')  # Urgent, Neutral, Positive
    attachment = db.Column(db.String(256), nullable=True)
    hidden_by_user = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    replies = db.relationship('Reply', backref='complaint', lazy=True, order_by='Reply.created_at', cascade='all, delete-orphan')

    def sentiment_emoji(self):
        mapping = {
            'Urgent': '🔴',
            'Neutral': '🟡',
            'Positive': '🟢'
        }
        return mapping.get(self.sentiment, '🟡')

    def status_color(self):
        mapping = {
            'Pending': 'warning',
            'In Progress': 'info',
            'Resolved': 'success'
        }
        return mapping.get(self.status, 'secondary')


class Reply(db.Model):
    __tablename__ = 'replies'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    is_ai = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
