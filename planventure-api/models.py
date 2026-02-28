from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import json
import jwt_utils

# Create db instance that will be initialized by app
db = SQLAlchemy()


class User(db.Model):
    """User model for PlanVenture application"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with trips
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password=None):
        self.email = email
        if password:
            self.set_password(password)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'trip_count': len(self.trips)
        }
    
    def generate_tokens(self, include_refresh=True):
        """Generate JWT tokens for the user"""
        return jwt_utils.create_token_response(self.id, include_refresh)
    
    def generate_access_token(self, expires_in_hours=24):
        """Generate access token for the user"""
        return jwt_utils.generate_token(self.id, expires_in_hours)
    
    def generate_refresh_token(self, expires_in_days=30):
        """Generate refresh token for the user"""
        return jwt_utils.generate_refresh_token(self.id, expires_in_days)
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user ID if valid"""
        payload = jwt_utils.validate_token(token)
        if payload:
            return payload.get('user_id')
        return None
    
    def __repr__(self):
        return f'<User {self.email}>'


class Trip(db.Model):
    """Trip model for PlanVenture application"""
    
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Location coordinates
    latitude = db.Column(db.Numeric(precision=10, scale=8), nullable=True)
    longitude = db.Column(db.Numeric(precision=11, scale=8), nullable=True)
    
    # Trip details
    description = db.Column(db.Text, nullable=True)
    itinerary = db.Column(db.Text, nullable=True)  # JSON string of itinerary items
    budget = db.Column(db.Numeric(precision=10, scale=2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='planned')  # planned, active, completed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, destination, start_date, end_date, **kwargs):
        self.user_id = user_id
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_coordinates(self, latitude, longitude):
        """Set trip coordinates"""
        self.latitude = latitude
        self.longitude = longitude
    
    def set_itinerary(self, itinerary_data):
        """Set itinerary as JSON string"""
        if isinstance(itinerary_data, (list, dict)):
            self.itinerary = json.dumps(itinerary_data)
        else:
            self.itinerary = itinerary_data
    
    def get_itinerary(self):
        """Get itinerary as Python object"""
        if self.itinerary:
            try:
                return json.loads(self.itinerary)
            except json.JSONDecodeError:
                return self.itinerary  # Return as string if not valid JSON
        return None
    
    def get_duration_days(self):
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def to_dict(self):
        """Convert trip object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'description': self.description,
            'itinerary': self.get_itinerary(),
            'budget': float(self.budget) if self.budget else None,
            'status': self.status,
            'duration_days': self.get_duration_days(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Trip {self.destination} ({self.start_date} - {self.end_date})>'