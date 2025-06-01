from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to activity logs
    activities = db.relationship('ActivityLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    base_name = db.Column(db.String(100), nullable=False)
    base_ip = db.Column(db.String(15), nullable=False)
    comment = db.Column(db.String(200), nullable=False)
    start_number = db.Column(db.Integer, nullable=False)
    end_number = db.Column(db.Integer, nullable=False)
    password_length = db.Column(db.Integer, nullable=False)
    character_types = db.Column(db.String(50), nullable=False)  # Store as comma-separated values
    users_generated = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<ActivityLog {self.user.username} - {self.users_generated} users>'
