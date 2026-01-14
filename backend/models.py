"""
Database models for JobTracker
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import bcrypt
import secrets

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to applications
    applications = db.relationship('Application', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        """Convert user to dictionary (exclude password)"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.email}>"


class PasswordResetToken(db.Model):
    """Password reset token model"""
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref='reset_tokens')

    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_for_user(user_id):
        """Create a new reset token for a user (expires in 1 hour)"""
        token = PasswordResetToken(
            user_id=user_id,
            token=PasswordResetToken.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        return token

    def is_valid(self):
        """Check if token is valid (not expired and not used)"""
        return not self.used and datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f"<PasswordResetToken for user {self.user_id}>"


class Application(db.Model):
    """Job application model"""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Applied, Phone Screen, Interview, Offer, Rejected
    date_applied = db.Column(db.Date, nullable=False)
    job_url = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    salary_range = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'status': self.status,
            'date_applied': self.date_applied.isoformat() if self.date_applied else None,
            'job_url': self.job_url,
            'location': self.location,
            'salary_range': self.salary_range,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Application {self.company} - {self.position}>"
