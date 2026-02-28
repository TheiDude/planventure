import os
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Trip
from jwt_utils import token_required, optional_token

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Basic configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///planventure.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')

# Initialize extensions
db.init_app(app)
CORS(app, origins=os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))

@app.route('/')
def home():
    return jsonify({"message": "Welcome to PlanVenture API"})

@app.route('/health')
def health_check():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return jsonify({
        "status": "healthy",
        "database": db_status
    })

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
@optional_token
def get_profile(current_user_id):
    """Example route where authentication is optional"""
    if current_user_id:
        user = User.query.get(current_user_id)
        if user:
            return jsonify({
                "authenticated": True,
                "user": user.to_dict()
            })
    
    return jsonify({
        "authenticated": False,
        "message": "No authentication provided"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('API_PORT', 5001))
    host = os.getenv('API_HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=True)
