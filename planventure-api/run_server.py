#!/usr/bin/env python3
"""
Start the PlanVenture API with auth middleware
"""

import os
from app import app, db

def init_database():
    """Initialize database tables"""
    print("Initializing database...")
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
    return True

def main():
    print("=" * 50)
    print("PLANVENTURE API WITH AUTH MIDDLEWARE")
    print("=" * 50)
    
    # Initialize database
    if not init_database():
        return
    
    print(f"\n🚀 Starting Flask app with auth middleware...")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"   Debug mode: {os.getenv('FLASK_DEBUG', 'True')}")
    print(f"   Host: 127.0.0.1")
    print(f"   Port: 5000")
    
    print(f"\n📋 Available endpoints:")
    print(f"   • POST /auth/register        - User registration") 
    print(f"   • POST /auth/login           - User login")
    print(f"   • GET  /auth/validate-email  - Email validation")
    print(f"   • GET  /auth/profile         - Profile (optional auth)")
    print(f"   • GET  /api/user/profile     - Protected user profile")
    print(f"   • GET  /api/user/trips       - User trips (protected)")
    print(f"   • POST /api/trips            - Create trip (protected)")
    
    print(f"\n🔒 Auth middleware features:")
    print(f"   • Automatic JWT validation")
    print(f"   • Route protection (@require_auth, @optional_auth)")
    print(f"   • User context in Flask g")
    print(f"   • Security headers")
    print(f"   • Helper functions (get_current_user, etc.)")
    
    print(f"\n💡 Test the API with:")
    print(f"   python test_middleware_integration.py")
    
    print(f"\n" + "=" * 50)
    
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        )
    except KeyboardInterrupt:
        print(f"\n👋 PlanVenture API stopped")
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")

if __name__ == '__main__':
    main()