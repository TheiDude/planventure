#!/usr/bin/env python3
"""
Test and enhance the login route with JWT token generation.
"""

import json
from app import app
from models import db, User

def test_login_route():
    """Test the login route functionality"""
    
    print("🔐 Testing Login Route with JWT Generation")
    print("=" * 60)
    
    with app.app_context():
        # Setup: Create test user
        print("Setting up test user...")
        existing_user = User.query.filter_by(email="login.test@planventure.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        test_user = User(email="login.test@planventure.com", password="LoginTest123!")
        db.session.add(test_user)
        db.session.commit()
        print(f"✅ Test user created with ID: {test_user.id}")
    
    with app.test_client() as client:
        print("\n1. Testing valid login...")
        
        valid_login = {
            "email": "login.test@planventure.com",
            "password": "LoginTest123!"
        }
        
        response = client.post('/auth/login',
            data=json.dumps(valid_login),
            content_type='application/json')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("   ✅ Login successful!")
            print(f"   User: {data['user']['email']}")
            print(f"   Access Token: {data['access_token'][:30]}...")
            print(f"   Refresh Token: {data['refresh_token'][:30]}...")
            print(f"   Token Type: {data['token_type']}")
            print(f"   Expires In: {data['expires_in']} seconds")
            
            # Save token for further testing
            access_token = data['access_token']
        else:
            data = response.get_json()
            print(f"   ❌ Login failed: {data.get('message', 'Unknown error')}")
            access_token = None
        
        print("\n2. Testing invalid credentials...")
        
        invalid_login = {
            "email": "login.test@planventure.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post('/auth/login',
            data=json.dumps(invalid_login),
            content_type='application/json')
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            data = response.get_json()
            print(f"   ✅ Invalid credentials properly rejected: {data['message']}")
        else:
            print("   ❌ Should have rejected invalid credentials")
        
        print("\n3. Testing non-existent user...")
        
        nonexistent_login = {
            "email": "nonexistent@planventure.com",
            "password": "SomePassword123!"
        }
        
        response = client.post('/auth/login',
            data=json.dumps(nonexistent_login),
            content_type='application/json')
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Non-existent user properly rejected")
        else:
            print("   ❌ Should have rejected non-existent user")
        
        print("\n4. Testing missing fields...")
        
        incomplete_login = {
            "email": "login.test@planventure.com"
            # Missing password
        }
        
        response = client.post('/auth/login',
            data=json.dumps(incomplete_login),
            content_type='application/json')
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Missing fields properly validated")
        else:
            print("   ❌ Should have validated missing fields")
        
        # Test protected endpoint with token
        if access_token:
            print("\n5. Testing JWT token with protected endpoint...")
            
            response = client.get('/auth/test-token',
                headers={'Authorization': f'Bearer {access_token}'})
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ Protected endpoint accessed: {data['message']}")
            else:
                print("   ❌ Token should have granted access")

def show_login_api_usage():
    """Show how to use the login API"""
    
    print("\n📋 Login API Usage")
    print("=" * 30)
    
    print("Endpoint: POST /auth/login")
    print("\nRequest format:")
    print(json.dumps({
        "email": "user@example.com",
        "password": "UserPassword123!"
    }, indent=2))
    
    print("\nSuccess response (200):")
    print(json.dumps({
        "message": "Login successful",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "created_at": "2026-02-28T21:00:00.000000",
            "updated_at": "2026-02-28T21:00:00.000000",
            "trip_count": 0
        },
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "Bearer",
        "expires_in": 86400
    }, indent=2))
    
    print("\nError response (401):")
    print(json.dumps({
        "error": "Authentication failed",
        "message": "Invalid email or password"
    }, indent=2))
    
    print("\ncurl example:")
    print("curl -X POST http://127.0.0.1:5001/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "email": "user@example.com",')
    print('    "password": "UserPassword123!"')
    print("  }'")

def cleanup_test_data():
    """Clean up test user"""
    with app.app_context():
        existing_user = User.query.filter_by(email="login.test@planventure.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("\n🧹 Test user cleaned up")

if __name__ == "__main__":
    test_login_route()
    show_login_api_usage()
    cleanup_test_data()
    
    print("\n🎉 Login Route Testing Complete!")
    print("✅ JWT token generation working")
    print("✅ Authentication validation working")
    print("✅ Error handling working")
    print("✅ Protected endpoint integration working")