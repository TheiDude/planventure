#!/usr/bin/env python3
"""
Comprehensive demonstration of the login route with JWT token generation.

This shows all aspects of the login functionality including:
- Valid login with JWT generation
- Error handling for various scenarios
- Token usage with protected endpoints
- API usage examples
"""

import json
from app import app
from models import db, User

def demonstrate_login_functionality():
    """Demonstrate complete login functionality"""
    
    print("🔐 Login Route with JWT Token Generation")
    print("=" * 60)
    
    # Setup test user
    with app.app_context():
        # Clean up existing test user
        existing_user = User.query.filter_by(email="demo@planventure.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        # Create new test user
        demo_user = User(email="demo@planventure.com", password="DemoLogin123!")
        db.session.add(demo_user)
        db.session.commit()
        print(f"✅ Demo user created: {demo_user.email} (ID: {demo_user.id})")
    
    with app.test_client() as client:
        
        # Test 1: Successful login
        print("\n1. ✅ Successful Login Test")
        print("-" * 40)
        
        login_data = {
            "email": "demo@planventure.com",
            "password": "DemoLogin123!"
        }
        
        response = client.post('/auth/login', json=login_data)
        
        print(f"Request: POST /auth/login")
        print(f"Payload: {json.dumps(login_data, indent=2)}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            access_token = data['access_token']
            
            print("Response:")
            response_display = {
                "message": data["message"],
                "user": data["user"],
                "access_token": data["access_token"][:50] + "...",
                "refresh_token": data["refresh_token"][:50] + "...",
                "token_type": data["token_type"],
                "expires_in": data["expires_in"]
            }
            print(json.dumps(response_display, indent=2))
            
        else:
            print(f"❌ Unexpected error: {response.get_json()}")
            return
        
        # Test 2: Invalid password
        print("\n2. ❌ Invalid Password Test")
        print("-" * 40)
        
        invalid_login = {
            "email": "demo@planventure.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post('/auth/login', json=invalid_login)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            data = response.get_json()
            print(f"✅ Properly rejected: {data['message']}")
        else:
            print("❌ Should have rejected invalid password")
        
        # Test 3: Non-existent user
        print("\n3. ❌ Non-existent User Test")
        print("-" * 40)
        
        nonexistent_login = {
            "email": "doesnotexist@planventure.com",
            "password": "SomePassword123!"
        }
        
        response = client.post('/auth/login', json=nonexistent_login)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Properly rejected non-existent user")
        else:
            print("❌ Should have rejected non-existent user")
        
        # Test 4: Missing fields
        print("\n4. ❌ Missing Fields Test")
        print("-" * 40)
        
        incomplete_login = {"email": "demo@planventure.com"}  # Missing password
        
        response = client.post('/auth/login', json=incomplete_login)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Properly validated missing fields")
        else:
            print("❌ Should have validated missing password")
        
        # Test 5: Using JWT token with protected endpoint
        print("\n5. 🔑 JWT Token Usage Test")
        print("-" * 40)
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/auth/test-token', headers=headers)
        print(f"Protected endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Token granted access: {data['message']}")
            print(f"Authenticated user: {data['user']['email']}")
        else:
            print("❌ Token should have granted access")

def show_api_documentation():
    """Show API documentation and usage examples"""
    
    print("\n📋 Login API Documentation")
    print("=" * 60)
    
    print("Endpoint: POST /auth/login")
    print("Content-Type: application/json")
    
    print("\n📤 Request Format:")
    request_example = {
        "email": "user@example.com",
        "password": "UserPassword123!"
    }
    print(json.dumps(request_example, indent=2))
    
    print("\n📥 Success Response (200):")
    success_example = {
        "message": "Login successful",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "created_at": "2026-02-28T21:00:00.000000",
            "updated_at": "2026-02-28T21:00:00.000000",
            "trip_count": 0
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer",
        "expires_in": 86400
    }
    print(json.dumps(success_example, indent=2))
    
    print("\n📥 Error Response (401):")
    error_example = {
        "error": "Authentication failed",
        "message": "Invalid email or password"
    }
    print(json.dumps(error_example, indent=2))
    
    print("\n🌐 cURL Example:")
    print("curl -X POST http://127.0.0.1:5001/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "email": "user@example.com",')
    print('    "password": "UserPassword123!"')
    print("  }'")
    
    print("\n🔑 Using the Access Token:")
    print("curl -X GET http://127.0.0.1:5001/auth/test-token \\")
    print("  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN_HERE'")

def show_jwt_features():
    """Show JWT token features and security"""
    
    print("\n🔐 JWT Token Features")
    print("=" * 40)
    
    print("✅ Features:")
    print("• Access tokens expire in 24 hours")
    print("• Refresh tokens expire in 30 days")
    print("• Tokens are signed with HS256 algorithm")
    print("• Tokens contain user ID and expiration")
    print("• Automatic token validation on protected routes")
    
    print("\n🛡️ Security:")
    print("• Passwords hashed with pbkdf2:sha256")
    print("• JWT secret key from environment variables")
    print("• Token-based stateless authentication")
    print("• Automatic session management")
    
    print("\n📝 Token Payload Example:")
    payload_example = {
        "user_id": 1,
        "exp": 1772400000,  # Expiration timestamp
        "iat": 1772313600,  # Issued at timestamp
        "sub": "1"          # Subject (user ID)
    }
    print(json.dumps(payload_example, indent=2))

def cleanup():
    """Clean up test data"""
    with app.app_context():
        test_user = User.query.filter_by(email="demo@planventure.com").first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
            print("\n🧹 Test data cleaned up")

if __name__ == "__main__":
    demonstrate_login_functionality()
    show_api_documentation()
    show_jwt_features()
    cleanup()
    
    print("\n🎉 Login Route Demonstration Complete!")
    print("\n✅ The login route provides:")
    print("• Secure user authentication")
    print("• JWT token generation (access + refresh)")
    print("• Comprehensive error handling")
    print("• Integration with protected endpoints")
    print("• RESTful API design")
    print("• Production-ready security features")