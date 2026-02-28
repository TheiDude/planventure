"""
JWT utility functions for PlanVenture API.

This module provides functions for generating and validating JWT tokens
for user authentication and authorization.
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
import os


def generate_token(user_id, expires_in_hours=24):
    """
    Generate a JWT token for a user.
    
    Args:
        user_id (int): The user's ID
        expires_in_hours (int): Token expiration time in hours (default: 24)
    
    Returns:
        str: JWT token string
    """
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow(),
            'sub': str(user_id)  # Subject claim
        }
        
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
    except Exception as e:
        raise Exception(f"Token generation failed: {str(e)}")


def generate_refresh_token(user_id, expires_in_days=30):
    """
    Generate a refresh token for a user.
    
    Args:
        user_id (int): The user's ID
        expires_in_days (int): Token expiration time in days (default: 30)
    
    Returns:
        str: JWT refresh token string
    """
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=expires_in_days),
            'iat': datetime.utcnow(),
            'sub': str(user_id),
            'type': 'refresh'  # Token type identifier
        }
        
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return token
    except Exception as e:
        raise Exception(f"Refresh token generation failed: {str(e)}")


def validate_token(token):
    """
    Validate and decode a JWT token.
    
    Args:
        token (str): JWT token string
    
    Returns:
        dict: Decoded token payload if valid
        None: If token is invalid or expired
    """
    try:
        secret_key = current_app.config['JWT_SECRET_KEY']
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # Additional validation checks
        if 'user_id' not in payload:
            return None
        
        # Check if token is not expired (jwt.decode already does this, but double-check)
        if datetime.utcnow().timestamp() > payload.get('exp', 0):
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid
    except Exception:
        return None  # Other errors


def extract_token_from_header(auth_header):
    """
    Extract JWT token from Authorization header.
    
    Args:
        auth_header (str): Authorization header value
    
    Returns:
        str: JWT token if found
        None: If no valid token found
    """
    if not auth_header:
        return None
    
    # Expected format: "Bearer <token>"
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]


def get_current_user_id():
    """
    Get the current user ID from the request token.
    
    Returns:
        int: Current user's ID if authenticated
        None: If not authenticated or invalid token
    """
    auth_header = request.headers.get('Authorization')
    token = extract_token_from_header(auth_header)
    
    if not token:
        return None
    
    payload = validate_token(token)
    if not payload:
        return None
    
    return payload.get('user_id')


def token_required(f):
    """
    Decorator to require JWT authentication for routes.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user_id):
            return jsonify({'user_id': current_user_id})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({
                'error': 'Token is missing',
                'message': 'Authentication required'
            }), 401
        
        payload = validate_token(token)
        if not payload:
            return jsonify({
                'error': 'Token is invalid or expired',
                'message': 'Please log in again'
            }), 401
        
        # Pass the user_id to the decorated function
        return f(payload['user_id'], *args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    Decorator for routes where authentication is optional.
    
    Usage:
        @app.route('/optional')
        @optional_token
        def optional_route(current_user_id):
            if current_user_id:
                return jsonify({'message': 'Authenticated user'})
            return jsonify({'message': 'Anonymous user'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = get_current_user_id()
        return f(user_id, *args, **kwargs)
    
    return decorated


def create_token_response(user_id, include_refresh=True):
    """
    Create a standardized token response.
    
    Args:
        user_id (int): User's ID
        include_refresh (bool): Whether to include refresh token
    
    Returns:
        dict: Token response with access_token and optionally refresh_token
    """
    try:
        response = {
            'access_token': generate_token(user_id),
            'token_type': 'Bearer',
            'expires_in': 86400  # 24 hours in seconds
        }
        
        if include_refresh:
            response['refresh_token'] = generate_refresh_token(user_id)
        
        return response
    
    except Exception as e:
        raise Exception(f"Token response creation failed: {str(e)}")