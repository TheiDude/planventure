"""
Authentication routes for PlanVenture API.

This module provides user registration, login, and authentication endpoints
with proper validation and JWT token management.
"""

import re
import logging
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from models import db, User
from jwt_utils import create_token_response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """
    Validate email format using regex.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant email regex (simplified version)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Additional checks
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    if '..' in email:  # Consecutive dots not allowed
        return False
    
    return re.match(email_pattern, email) is not None

def validate_password(password):
    """
    Validate password strength.
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters long"
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    
    Returns:
        JSON: Success response with JWT tokens or error message
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        # Extract and validate required fields
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # Handle None values and convert to empty string for validation
        if email is None:
            email = ''
        if password is None:
            password = ''
        if confirm_password is None:
            confirm_password = ''
            
        # Strip and lowercase email if it's a string
        if isinstance(email, str):
            email = email.strip().lower()
        else:
            email = ''  # Convert non-string email to empty string
        
        # Validate required fields
        if not email:
            return jsonify({
                'error': 'Validation error',
                'message': 'Email is required'
            }), 400
        
        if not password:
            return jsonify({
                'error': 'Validation error',
                'message': 'Password is required'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'error': 'Validation error',
                'message': 'Invalid email format'
            }), 400
        
        # Validate password strength
        is_valid_password, password_error = validate_password(password)
        if not is_valid_password:
            return jsonify({
                'error': 'Validation error',
                'message': password_error
            }), 400
        
        # Check password confirmation
        if password != confirm_password:
            return jsonify({
                'error': 'Validation error',
                'message': 'Passwords do not match'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'error': 'Registration failed',
                'message': 'An account with this email already exists'
            }), 409
        
        # Create new user
        try:
            # Log attempt for debugging
            print(f"Creating user with email: {email}")
            
            new_user = User(email=email, password=password)
            print(f"User object created: {new_user}")
            
            db.session.add(new_user)
            print("User added to session")
            
            db.session.commit()
            print(f"User committed to database with ID: {new_user.id}")
            
            # Generate JWT tokens
            print("Generating JWT tokens...")
            tokens = new_user.generate_tokens()
            print(f"Tokens generated successfully")
            
            # Return success response
            return jsonify({
                'message': 'Registration successful',
                'user': new_user.to_dict(),
                **tokens
            }), 201
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {str(e)}")
            return jsonify({
                'error': 'Registration failed',
                'message': 'An account with this email already exists'
            }), 409
        
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"SQLAlchemyError: {str(e)}")
            return jsonify({
                'error': 'Registration failed',
                'message': 'Database error occurred. Please try again.'
            }), 500
        
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error during registration: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Registration failed',
                'message': f'An error occurred while creating your account: {str(e)}'
            }), 500
    
    except BadRequest:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Invalid JSON data'
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "SecurePassword123!"
    }
    
    Returns:
        JSON: Success response with JWT tokens or error message
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        # Extract credentials
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate required fields
        if not email or not password:
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Email and password are required'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Authentication failed',
                'message': 'Invalid email or password'
            }), 401
        
        # Generate JWT tokens
        tokens = user.generate_tokens()
        
        # Return success response
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            **tokens
        }), 200
    
    except BadRequest:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Invalid JSON data'
        }), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/validate-email', methods=['POST'])
def validate_email_endpoint():
    """
    Validate email format without registration.
    
    Expected JSON payload:
    {
        "email": "user@example.com"
    }
    
    Returns:
        JSON: Validation result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must contain JSON data'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'valid': False,
                'message': 'Email is required'
            }), 400
        
        # Check email format
        is_valid = validate_email(email)
        
        if not is_valid:
            return jsonify({
                'valid': False,
                'message': 'Invalid email format'
            }), 200
        
        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'valid': False,
                'available': False,
                'message': 'Email is already registered'
            }), 200
        
        return jsonify({
            'valid': True,
            'available': True,
            'message': 'Email is valid and available'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred'
        }), 500