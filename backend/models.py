"""
Database models for JobTracker
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Application(db.Model):
    """Job application model"""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
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
