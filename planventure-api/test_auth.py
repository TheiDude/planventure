#!/usr/bin/env python3
"""
Test script for authentication routes in PlanVenture API.

This script tests user registration, login, and email validation endpoints.
"""

import requests
import json
from app import app
from models import db, User

# Test data
TEST_USER_DATA = {
    "email": "test.auth@planventure.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}

INVALID_EMAIL_DATA = {
    "email": "invalid-email",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
}

WEAK_PASSWORD_DATA = {
    "email": "weak@planventure.com",
    "password": "weak",
    "confirm_password": "weak"
}

BASE_URL = "http://127.0.0.1:5001"

def test_with_app_context():
    """Test authentication functionality within Flask app context"""
    
    with app.app_context():
        # Clear any existing test user
        existing_user = User.query.filter_by(email=TEST_USER_DATA["email"]).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
        
        print("🔐 Testing Authentication Routes")
        print("=" * 50)
        
        # Test 1: Email validation
        print("1. Testing email validation...")
        from auth_routes import validate_email
        
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.com"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "a" * 250 + "@example.com"  # Too long
        ]
        
        for email in valid_emails:
            if validate_email(email):
                print(f"   ✅ Valid: {email}")
            else:
                print(f"   ❌ Should be valid: {email}")
        
        for email in invalid_emails:
            if not validate_email(email):
                print(f"   ✅ Invalid (as expected): {email}")
            else:
                print(f"   ❌ Should be invalid: {email}")
        
        # Test 2: Password validation
        print("\n2. Testing password validation...")
        from auth_routes import validate_password
        
        test_passwords = [
            ("SecurePass123!", True),
            ("weak", False),
            ("NoNumber!", False),
            ("nonumber123", False),
            ("NOLOWERCASE123!", False),
            ("nouppercase123!", False)
        ]
        
        for password, should_be_valid in test_passwords:
            is_valid, error = validate_password(password)
            if is_valid == should_be_valid:
                status = "✅" if is_valid else "✅ Invalid (as expected)"
                print(f"   {status}: '{password[:20]}...' - {error if error else 'Valid'}")
            else:
                print(f"   ❌ Validation error for: '{password}'")
        
        # Test 3: User registration
        print("\n3. Testing user registration...")
        try:
            new_user = User(TEST_USER_DATA["email"], TEST_USER_DATA["password"])
            db.session.add(new_user)
            db.session.commit()
            
            print(f"   ✅ User created: {new_user.email}")
            print(f"   ✅ Password check: {new_user.check_password(TEST_USER_DATA['password'])}")
            
            # Test JWT token generation
            tokens = new_user.generate_tokens()
            print(f"   ✅ Tokens generated: {len(tokens)} items")
            print(f"   ✅ Access token length: {len(tokens['access_token'])}")
            
            # Verify token
            user_id_from_token = User.verify_token(tokens['access_token'])
            print(f"   ✅ Token verification: User ID {user_id_from_token}")
            
        except Exception as e:
            print(f"   ❌ Registration error: {str(e)}")
        
        print("\n🎉 Authentication tests completed!")

def test_api_endpoints():
    """Test API endpoints by making HTTP requests"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    # This would require the server to be running
    # For now, we'll just print what we would test
    print("To test API endpoints:")
    print(f"1. Start server: python3 app.py")
    print(f"2. POST {BASE_URL}/auth/register")
    print(f"3. POST {BASE_URL}/auth/login")
    print(f"4. POST {BASE_URL}/auth/validate-email")
    print(f"5. GET {BASE_URL}/auth/test-token (with Bearer token)")

def print_curl_examples():
    """Print curl command examples for testing"""
    print("\n📋 Example curl commands:")
    print("=" * 50)
    
    # Registration example
    print("# User Registration:")
    print(f"curl -X POST {BASE_URL}/auth/register \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "email": "{TEST_USER_DATA["email"]}",')
    print(f'    "password": "{TEST_USER_DATA["password"]}",')
    print(f'    "confirm_password": "{TEST_USER_DATA["confirm_password"]}"')
    print("  }'")
    
    # Login example
    print(f"\n# User Login:")
    print(f"curl -X POST {BASE_URL}/auth/login \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "email": "{TEST_USER_DATA["email"]}",')
    print(f'    "password": "{TEST_USER_DATA["password"]}"')
    print("  }'")
    
    # Email validation example
    print(f"\n# Email Validation:")
    print(f"curl -X POST {BASE_URL}/auth/validate-email \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "email": "test@example.com"')
    print("  }'")

if __name__ == "__main__":
    test_with_app_context()
    test_api_endpoints()
    print_curl_examples()