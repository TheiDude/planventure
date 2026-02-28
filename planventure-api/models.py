from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import json
import jwt_utils

# Try to import bcrypt as fallback
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

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
        try:
            # Try pbkdf2:sha256 method first (most compatible)
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        except Exception as e:
            print(f"pbkdf2:sha256 failed: {e}")
            try:
                # Fallback to bcrypt if available
                if BCRYPT_AVAILABLE:
                    salt = bcrypt.gensalt()
                    self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                    # Add a prefix to identify bcrypt hashes
                    self.password_hash = 'bcrypt:' + self.password_hash
                else:
                    # Final fallback to pbkdf2:sha1 (older but more compatible)
                    self.password_hash = generate_password_hash(password, method='pbkdf2:sha1')
            except Exception as fallback_error:
                print(f"All password hashing methods failed: {fallback_error}")
                raise Exception(f"Password hashing failed: {fallback_error}")
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        try:
            # Check if it's a bcrypt hash
            if self.password_hash.startswith('bcrypt:'):
                if BCRYPT_AVAILABLE:
                    bcrypt_hash = self.password_hash[7:]  # Remove 'bcrypt:' prefix
                    return bcrypt.checkpw(password.encode('utf-8'), bcrypt_hash.encode('utf-8'))
                else:
                    print("bcrypt hash detected but bcrypt not available")
                    return False
            else:
                # Use Werkzeug's check_password_hash for other methods
                return check_password_hash(self.password_hash, password)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
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
            # Ensure each itinerary item has required fields
            if isinstance(itinerary_data, list):
                for item in itinerary_data:
                    if isinstance(item, dict):
                        # Add default fields if missing
                        if 'day' not in item and 'activity' in item:
                            # Try to infer day from position if not specified
                            item['day'] = itinerary_data.index(item) + 1
                        if 'location' not in item:
                            item['location'] = self.destination or 'TBD'
                        if 'notes' not in item:
                            item['notes'] = ''
            
            self.itinerary = json.dumps(itinerary_data, indent=2)
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
    
    @classmethod
    def generate_default_itinerary_template(cls, duration_days, destination=None):
        """Generate a default itinerary template based on trip duration"""
        if duration_days <= 0:
            return []
        
        template = []
        
        # Day 1 - Arrival
        template.append({
            'day': 1,
            'activity': 'Arrival and check-in',
            'location': f'{destination} Airport/Hotel' if destination else 'Airport/Hotel',
            'notes': 'Settle in, explore nearby area, get familiar with surroundings'
        })
        
        # Middle days - Exploration (if more than 1 day)
        if duration_days > 1:
            exploration_days = duration_days - 1 if duration_days <= 3 else duration_days - 2
            
            for day in range(2, 2 + exploration_days):
                if day == 2:
                    activity = 'Main attractions and sightseeing'
                    location = f'Popular spots in {destination}' if destination else 'City center/Main attractions'
                elif day == 3:
                    activity = 'Cultural experiences and local food'
                    location = f'Local neighborhoods in {destination}' if destination else 'Local markets/Cultural sites'
                elif day == 4:
                    activity = 'Adventure activities or day trip'
                    location = f'Outskirts of {destination}/Day trip destination' if destination else 'Adventure location'
                else:
                    activity = f'Free exploration day {day - 1}'
                    location = f'Explore {destination}' if destination else 'Open exploration'
                
                template.append({
                    'day': day,
                    'activity': activity,
                    'location': location,
                    'notes': 'Customize based on your interests and preferences'
                })
        
        # Last day - Departure (if more than 2 days)
        if duration_days > 2:
            template.append({
                'day': duration_days,
                'activity': 'Last-minute shopping and departure',
                'location': f'{destination} Shopping area/Airport' if destination else 'Shopping/Airport',
                'notes': 'Pack, checkout, head to airport with buffer time'
            })
        
        return template
    
    def generate_default_itinerary(self):
        """Generate default itinerary for this trip instance"""
        duration = self.get_duration_days()
        return self.generate_default_itinerary_template(duration, self.destination)
    
    def set_default_itinerary(self):
        """Set the trip's itinerary to the default template"""
        default_template = self.generate_default_itinerary()
        self.set_itinerary(default_template)
    
    @classmethod
    def get_itinerary_suggestions_by_type(cls, trip_type='general'):
        """Get activity suggestions based on trip type"""
        suggestions = {
            'general': [
                'City walking tour',
                'Visit local museums',
                'Try local cuisine',
                'Shopping at local markets',
                'Explore historical sites'
            ],
            'adventure': [
                'Hiking or trekking',
                'Water sports activities',
                'Mountain biking',
                'Rock climbing or zip-lining',
                'Wildlife watching'
            ],
            'cultural': [
                'Visit art galleries and museums',
                'Attend local festivals or events',
                'Historical site tours',
                'Traditional craft workshops',
                'Local cooking classes'
            ],
            'relaxation': [
                'Spa and wellness activities',
                'Beach or lakeside relaxation',
                'Scenic walks and nature',
                'Yoga or meditation sessions',
                'Leisurely cafe visits'
            ],
            'business': [
                'Business meetings and conferences',
                'Networking events',
                'City exploration during free time',
                'Local business district tours',
                'Professional dining experiences'
            ],
            'family': [
                'Family-friendly attractions',
                'Parks and playgrounds',
                'Interactive museums',
                'Beach or outdoor activities',
                'Local entertainment shows'
            ]
        }
        
        return suggestions.get(trip_type, suggestions['general'])
    
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