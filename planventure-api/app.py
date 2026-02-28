import os
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Trip

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('API_PORT', 5001))
    host = os.getenv('API_HOST', '127.0.0.1')
    app.run(host=host, port=port, debug=True)
