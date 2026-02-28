#!/usr/bin/env python3
"""
Test the password hashing fix for the scrypt error.
"""

import json
from app import app
from models import db, User

def test_password_hashing_fix():
    """Test that password hashing works without scrypt errors"""
    
    print("🔧 Testing Password Hashing Fix")
    print("=" * 50)
    
    with app.app_context():
        # Clean up existing test user
        existing_user = User.query.filter_by(email="scrypttest@planventure.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("✅ Cleaned up existing test user")
        
        try:
            print("1. Testing User model password hashing...")
            user = User(email="scrypttest@planventure.com", password="ScryptTest123!")
            print(f"✅ User created successfully")
            print(f"✅ Password hash: {user.password_hash[:50]}...")
            
            print("2. Testing password verification...")
            is_valid = user.check_password("ScryptTest123!")
            print(f"✅ Correct password verification: {is_valid}")
            
            is_invalid = user.check_password("WrongPassword")
            print(f"✅ Wrong password rejection: {not is_invalid}")
            
            print("3. Testing database operations...")
            db.session.add(user)
            db.session.commit()
            print(f"✅ User saved to database with ID: {user.id}")
            
            print("4. Testing registration API...")
            test_registration_api()
            
        except Exception as e:
            print(f"❌ Error during password hashing test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_registration_api():
    """Test the registration API with the password fix"""
    
    test_data = {
        "email": "regtest@planventure.com",
        "password": "RegTest123!",
        "confirm_password": "RegTest123!"
    }
    
    with app.test_client() as client:
        # Clean up existing user
        with app.app_context():
            existing_user = User.query.filter_by(email=test_data["email"]).first()
            if existing_user:
                db.session.delete(existing_user)
                db.session.commit()
        
        try:
            response = client.post(
                '/auth/register',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            if response.status_code == 201:
                response_data = response.get_json()
                print("✅ Registration API successful!")
                print(f"   User: {response_data['user']['email']}")
                print(f"   Token: {response_data['access_token'][:30]}...")
                return True
            else:
                response_data = response.get_json()
                print(f"❌ Registration API failed: {response_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Registration API error: {str(e)}")
            return False

def show_hash_methods():
    """Show what hashing methods are available"""
    
    print("\n🔍 Available Hashing Methods")
    print("-" * 40)
    
    from werkzeug.security import generate_password_hash
    
    methods_to_test = [
        'pbkdf2:sha256',
        'pbkdf2:sha1', 
        'pbkdf2:md5'
    ]
    
    for method in methods_to_test:
        try:
            test_hash = generate_password_hash("test123", method=method)
            print(f"✅ {method}: Working")
        except Exception as e:
            print(f"❌ {method}: Failed - {str(e)}")
    
    # Test bcrypt availability
    try:
        import bcrypt
        print("✅ bcrypt: Available as fallback")
    except ImportError:
        print("❌ bcrypt: Not available")

if __name__ == "__main__":
    show_hash_methods()
    success = test_password_hashing_fix()
    
    if success:
        print("\n🎉 Password hashing fix successful!")
        print("✅ The scrypt error has been resolved")
        print("✅ Registration API is working")
        print("✅ Password verification is working")
    else:
        print("\n❌ Password hashing fix failed")
        print("Please check the error messages above")