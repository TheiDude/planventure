import os
import time
from datetime import datetime
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Trip
from jwt_utils import token_required, optional_token
from auth_routes import auth_bp
from trip_routes import trips_bp
from auth_middleware import AuthMiddleware, require_auth, optional_auth, get_current_user

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Store application start time for uptime calculation
app.start_time = time.time()

# Basic configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///planventure.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')

# Initialize extensions
db.init_app(app)

# CORS Configuration for React Frontend
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS(app, 
     origins=cors_origins,
     methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True,
     expose_headers=['Authorization']
)

# Initialize auth middleware
auth_middleware = AuthMiddleware(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    """Comprehensive health check endpoint for monitoring and load balancers"""
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": int(time.time() - app.start_time),
        "version": "1.0.0",
        "environment": os.getenv('FLASK_ENV', 'production'),
        "checks": {}
    }
    
    overall_healthy = True
    
    # Database health check
    try:
        start_time = time.time()
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        health_data["checks"]["database"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        health_data["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # Auth middleware health check
    try:
        # Simple check to ensure auth middleware is loaded
        if hasattr(app, 'auth_middleware'):
            health_data["checks"]["auth_middleware"] = {
                "status": "healthy"
            }
        else:
            health_data["checks"]["auth_middleware"] = {
                "status": "unhealthy",
                "error": "Auth middleware not initialized"
            }
            overall_healthy = False
    except Exception as e:
        health_data["checks"]["auth_middleware"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_healthy = False
    
    # CORS configuration check
    try:
        cors_origins = os.getenv('CORS_ORIGINS', '')
        health_data["checks"]["cors"] = {
            "status": "healthy" if cors_origins else "warning",
            "origins_count": len(cors_origins.split(',')) if cors_origins else 0
        }
    except Exception as e:
        health_data["checks"]["cors"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Set overall status
    if not overall_healthy:
        health_data["status"] = "unhealthy"
        return jsonify(health_data), 503  # Service Unavailable
    
    return jsonify(health_data), 200

@app.route('/status')
def simple_status():
    """Simple status endpoint for quick health checks"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route('/ready')
def readiness_check():
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick database check
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        return jsonify({"ready": True}), 200
    except Exception:
        return jsonify({"ready": False}), 503

@app.route('/live') 
def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return jsonify({"alive": True}), 200

@app.route('/auth/test-token')
@token_required
def test_protected_route(current_user_id):
    """Example protected route that requires authentication"""
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "message": "Access granted to protected route",
        "user": user.to_dict()
    })

@app.route('/auth/profile')
@optional_auth
def get_profile():
    """Example route where authentication is optional"""
    if g.is_authenticated:
        user = get_current_user()
        return jsonify({
            "authenticated": True,
            "user": user.to_dict(),
            "message": f"Welcome back, {user.email}!"
        })
    
    return jsonify({
        "authenticated": False,
        "message": "No authentication provided"
    })

@app.route('/api/user/profile')
@require_auth
def get_user_profile():
    """Protected route that requires authentication"""
    user = get_current_user()
    return jsonify({
        "message": "User profile accessed",
        "user": user.to_dict()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('API_PORT', 5001))
    host = os.getenv('API_HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=True)
