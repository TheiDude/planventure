#!/usr/bin/env python3
"""
Diagnostic script to debug registration failures.

This script tests each component of the registration process
to identify where the failure is occurring.
"""

import json
import traceback
from app import app
from models import db, User
from jwt_utils import create_token_response

def test_database_connection():
    """Test if database connection is working"""
    print("🔍 Testing Database Connection")
    print("-" * 40)
    
    try:
        with app.app_context():
            # Test basic connection
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1")).fetchone()
                print(f"✅ Database connection successful: {result}")
                
            # Test table existence
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Available tables: {tables}")
            
            # Test User table structure
            if 'users' in tables:
                columns = inspector.get_columns('users')
                column_names = [col['name'] for col in columns]
                print(f"✅ User table columns: {column_names}")
            else:
                print("❌ Users table not found!")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        traceback.print_exc()
        return False

def test_user_model():
    """Test User model creation"""
    print("\n🧪 Testing User Model Creation")
    print("-" * 40)
    
    try:
        with app.app_context():
            # Clean up any existing test user
            existing_user = User.query.filter_by(email="diagnostic@test.com").first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
                print("✅ Cleaned up existing test user")
            
            # Test user creation
            print("Creating User object...")
            test_user = User(email="diagnostic@test.com", password="TestPass123!")
            print(f"✅ User object created: {test_user}")
            
            # Test adding to session
            print("Adding user to session...")
            db.session.add(test_user)
            print("✅ User added to session")
            
            # Test commit
            print("Committing to database...")
            db.session.commit()
            print(f"✅ User committed with ID: {test_user.id}")
            
            # Test password verification
            print("Testing password verification...")
            is_valid = test_user.check_password("TestPass123!")
            print(f"✅ Password verification: {is_valid}")
            
            # Test to_dict method
            print("Testing to_dict method...")
            user_dict = test_user.to_dict()
            print(f"✅ User dict: {user_dict}")
            
            return test_user
            
    except Exception as e:
        print(f"❌ User model test failed: {str(e)}")
        traceback.print_exc()
        return None

def test_jwt_generation(user):
    """Test JWT token generation"""
    print("\n🔐 Testing JWT Token Generation")
    print("-" * 40)
    
    try:
        with app.app_context():
            print("Generating tokens...")
            tokens = user.generate_tokens()
            print(f"✅ Tokens generated: {list(tokens.keys())}")
            
            print("Testing individual token methods...")
            access_token = user.generate_access_token()
            print(f"✅ Access token: {access_token[:50]}...")
            
            refresh_token = user.generate_refresh_token()
            print(f"✅ Refresh token: {refresh_token[:50]}...")
            
            return tokens
            
    except Exception as e:
        print(f"❌ JWT generation failed: {str(e)}")
        traceback.print_exc()
        return None

def test_registration_api():
    """Test the full registration API"""
    print("\n🌐 Testing Registration API")
    print("-" * 40)
    
    try:
        test_data = {
            "email": "api.diagnostic@test.com",
            "password": "ApiTest123!",
            "confirm_password": "ApiTest123!"
        }
        
        with app.test_client() as client:
            # Clean up any existing user first
            with app.app_context():
                existing_user = User.query.filter_by(email=test_data["email"]).first()
                if existing_user:
                    db.session.delete(existing_user)
                    db.session.commit()
            
            print("Making registration request...")
            response = client.post(
                '/auth/register',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            print(f"Response status: {response.status_code}")
            response_data = response.get_json()
            print(f"Response data: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 201:
                print("✅ Registration API successful!")
                return True
            else:
                print(f"❌ Registration API failed: {response_data.get('message', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ Registration API test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_jwt_config():
    """Test JWT configuration"""  
    print("\n⚙️  Testing JWT Configuration")
    print("-" * 40)
    
    try:
        with app.app_context():
            jwt_secret = app.config.get('JWT_SECRET_KEY')
            print(f"JWT Secret Key configured: {'Yes' if jwt_secret else 'No'}")
            if jwt_secret:
                print(f"JWT Secret Key length: {len(jwt_secret)} characters")
            else:
                print("❌ JWT_SECRET_KEY not configured!")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ JWT config test failed: {str(e)}")
        return False

def run_full_diagnostic():
    """Run complete diagnostic test"""
    print("🩺 PlanVenture Registration Diagnostic")
    print("=" * 60)
    
    results = {
        "database": test_database_connection(),
        "jwt_config": test_jwt_config(),
        "user_model": None,
        "jwt_generation": False,
        "registration_api": False
    }
    
    if results["database"] and results["jwt_config"]:
        user = test_user_model()
        results["user_model"] = user is not None
        
        if user:
            tokens = test_jwt_generation(user)
            results["jwt_generation"] = tokens is not None
            
            results["registration_api"] = test_registration_api()
    
    print("\n📊 Diagnostic Results")
    print("=" * 30)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️ SKIP"
        
        print(f"{test_name:20} {status}")
    
    if all(r is True for r in results.values() if r is not None):
        print("\n🎉 All tests passed! Registration should work.")
    else:
        failed_tests = [name for name, result in results.items() if result is False]
        print(f"\n⚠️  Failed tests: {', '.join(failed_tests)}")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    run_full_diagnostic()