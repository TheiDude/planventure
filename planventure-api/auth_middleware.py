"""
Authentication middleware for PlanVenture API.

This module provides middleware for automatic JWT token validation,
route protection, and user context management.
"""

from functools import wraps
from flask import request, jsonify, g, current_app
from jwt_utils import validate_token, extract_token_from_header
from models import User
import re


class AuthMiddleware:
    """Authentication middleware class for Flask applications"""
    
    def __init__(self, app=None):
        self.app = app
        self.protected_routes = set()
        self.optional_auth_routes = set()
        self.public_routes = set()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        self.app = app
        
        # Register before_request handler
        app.before_request(self.before_request)
        
        # Register after_request handler for CORS and security headers
        app.after_request(self.after_request)
        
        # Add middleware instance to app
        app.auth_middleware = self
    
    def before_request(self):
        """Process request before reaching route handlers"""
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return
        
        # Get current route info
        endpoint = request.endpoint
        path = request.path
        
        # Initialize user context
        g.current_user = None
        g.current_user_id = None
        g.is_authenticated = False
        
        # Skip authentication for public routes
        if self._is_public_route(path, endpoint):
            return
        
        # Extract and validate token
        auth_header = request.headers.get('Authorization')
        token = extract_token_from_header(auth_header)
        
        if token:
            payload = validate_token(token)
            if payload:
                user_id = payload.get('user_id')
                if user_id:
                    # Load user from database
                    user = User.query.get(user_id)
                    if user:
                        g.current_user = user
                        g.current_user_id = user_id
                        g.is_authenticated = True
        
        # Check if route requires authentication
        if self._requires_authentication(path, endpoint):
            if not g.is_authenticated:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'Please provide a valid access token'
                }), 401
    
    def after_request(self, response):
        """Process response after route handler"""
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add CORS headers if needed
        if current_app.config.get('CORS_ENABLED', True):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        
        return response
    
    def _is_public_route(self, path, endpoint):
        """Check if route is explicitly marked as public"""
        
        # Default public routes
        default_public = {
            '/health',
            '/auth/register', 
            '/auth/login',
            '/auth/validate-email',
            '/',
            '/static'
        }
        
        # Check exact matches
        if path in default_public or path in self.public_routes:
            return True
        
        # Check patterns
        public_patterns = [
            r'^/static/.*',
            r'^/auth/(register|login|validate-email)$'
        ]
        
        for pattern in public_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _requires_authentication(self, path, endpoint):
        """Check if route requires authentication"""
        
        # Check if explicitly marked as protected
        if path in self.protected_routes:
            return True
        
        # Check patterns that require auth
        protected_patterns = [
            r'^/auth/(profile|test-token)$',
            r'^/api/.*',
            r'^/trips/.*',
            r'^/users/.*'
        ]
        
        for pattern in protected_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def protect_route(self, path_or_func):
        """Decorator to mark routes as requiring authentication"""
        
        if isinstance(path_or_func, str):
            # Used as @auth_middleware.protect_route('/api/endpoint')
            def decorator(func):
                self.protected_routes.add(path_or_func)
                return func
            return decorator
        else:
            # Used as @auth_middleware.protect_route
            func = path_or_func
            # Extract route path from function (requires route to be already registered)
            return func
    
    def public_route(self, path_or_func):
        """Decorator to mark routes as public (no authentication required)"""
        
        if isinstance(path_or_func, str):
            def decorator(func):
                self.public_routes.add(path_or_func)
                return func
            return decorator
        else:
            func = path_or_func
            return func
    
    def optional_auth(self, path_or_func):
        """Decorator to mark routes with optional authentication"""
        
        if isinstance(path_or_func, str):
            def decorator(func):
                self.optional_auth_routes.add(path_or_func)
                return func
            return decorator
        else:
            func = path_or_func
            return func


# Convenience decorators that work with Flask-style decorators
def require_auth(f):
    """
    Decorator to require authentication for a route.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            return jsonify({'user_id': g.current_user_id})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('is_authenticated', False):
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide a valid access token'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def optional_auth(f):
    """
    Decorator for routes where authentication is optional.
    
    Usage:
        @app.route('/optional')
        @optional_auth
        def optional_route():
            if g.is_authenticated:
                return jsonify({'message': f'Hello {g.current_user.email}'})
            return jsonify({'message': 'Hello anonymous user'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authentication was already processed in middleware
        # Just call the function
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges.
    
    Usage:
        @app.route('/admin')
        @admin_required
        def admin_route():
            return jsonify({'message': 'Admin access granted'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('is_authenticated', False):
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please provide a valid access token'
            }), 401
        
        # Check if user has admin role (you'll need to add this field to User model)
        # For now, we'll use a simple check
        if not hasattr(g.current_user, 'is_admin') or not g.current_user.is_admin:
            return jsonify({
                'error': 'Insufficient privileges',
                'message': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Helper function to get current authenticated user"""
    return g.get('current_user')


def get_current_user_id():
    """Helper function to get current authenticated user ID"""
    return g.get('current_user_id')


def is_authenticated():
    """Helper function to check if current request is authenticated"""
    return g.get('is_authenticated', False)