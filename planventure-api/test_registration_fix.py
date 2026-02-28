#!/usr/bin/env python3
"""
Test script for the registration API endpoint.

This script demonstrates proper usage of the /auth/register endpoint
and shows how to handle the password confirmation validation.
"""

import requests
import json
from app import app

def test_registration_api():
    """Test the registration API with various scenarios"""
    
    print("🧪 Testing Registration API Endpoint")
    print("=" * 50)
    
    # Test cases for registration
    test_cases = [
        {
            "name": "Valid Registration",
            "data": {
                "email": "valid.user@planventure.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            },
            "expected_status": 201
        },
        {
            "name": "Passwords Don't Match",
            "data": {
                "email": "mismatch@planventure.com",
                "password": "ValidPass123!",
                "confirm_password": "DifferentPass123!"  # Different password
            },
            "expected_status": 400
        },
        {
            "name": "Weak Password",
            "data": {
                "email": "weak@planventure.com",
                "password": "weak",
                "confirm_password": "weak"
            },
            "expected_status": 400
        },
        {
            "name": "Invalid Email",
            "data": {
                "email": "invalid-email",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            },
            "expected_status": 400
        },
        {
            "name": "Missing Fields",
            "data": {
                "email": "missing@planventure.com"
                # Missing password fields
            },
            "expected_status": 400
        }
    ]
    
    with app.test_client() as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"{i}. Testing: {test_case['name']}")
            
            try:
                response = client.post(
                    '/auth/register',
                    data=json.dumps(test_case['data']),
                    content_type='application/json'
                )
                
                response_data = response.get_json()
                
                print(f"   Status: {response.status_code} (expected: {test_case['expected_status']})")
                
                if response.status_code == test_case['expected_status']:
                    print("   ✅ Test passed")
                else:
                    print("   ❌ Test failed")
                
                if response.status_code == 201:
                    # Success case
                    print(f"   ✅ User created: {response_data['user']['email']}")
                    print(f"   ✅ Token received: {len(response_data['access_token'])} chars")
                else:
                    # Error case
                    print(f"   📝 Error: {response_data.get('message', 'No message')}")
                
            except Exception as e:
                print(f"   ❌ Request failed: {str(e)}")
            
            print()

def show_correct_usage():
    """Show examples of correct API usage"""
    
    print("📋 Correct Usage Examples")
    print("=" * 50)
    
    print("✅ Valid Registration Request:")
    valid_request = {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"  # Must match exactly
    }
    
    print("JSON Payload:")
    print(json.dumps(valid_request, indent=2))
    
    print("\n📝 curl command:")
    print("curl -X POST http://127.0.0.1:5001/auth/register \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "email": "{valid_request["email"]}",')
    print(f'    "password": "{valid_request["password"]}",')
    print(f'    "confirm_password": "{valid_request["confirm_password"]}"')
    print("  }'")
    
    print("\n⚠️  Common Issues:")
    print("• Password and confirm_password must match exactly")
    print("• Password must be at least 8 characters")
    print("• Password must contain: uppercase, lowercase, number, special char")
    print("• Email must be valid format")
    print("• All fields are required")

def show_password_requirements():
    """Show password validation requirements"""
    
    print("\n🔐 Password Requirements")
    print("=" * 30)
    print("✓ At least 8 characters long")
    print("✓ At least one uppercase letter (A-Z)")
    print("✓ At least one lowercase letter (a-z)")
    print("✓ At least one digit (0-9)")
    print("✓ At least one special character (!@#$%^&*()_+-=[]{}...)")
    print("✓ Maximum 128 characters")
    print("✓ Password and confirm_password must match exactly")
    
    print("\n✅ Valid password examples:")
    valid_passwords = [
        "SecurePass123!",
        "MyPassword1@",
        "StrongPass2024#",
        "UserAccount99$"
    ]
    
    for pwd in valid_passwords:
        print(f"   • {pwd}")
    
    print("\n❌ Invalid password examples:")
    invalid_passwords = [
        ("weak", "Too short"),
        ("nouppercase123!", "No uppercase letter"),
        ("NOLOWERCASE123!", "No lowercase letter"),
        ("NoNumber!", "No digit"),
        ("NoSpecialChar123", "No special character")
    ]
    
    for pwd, reason in invalid_passwords:
        print(f"   • {pwd} - {reason}")

if __name__ == "__main__":
    # Reset database for clean testing
    from models import db, User
    
    with app.app_context():
        # Clear any existing test users
        test_emails = [
            "valid.user@planventure.com",
            "mismatch@planventure.com", 
            "weak@planventure.com",
            "missing@planventure.com"
        ]
        
        for email in test_emails:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                db.session.delete(existing_user)
        
        db.session.commit()
    
    # Run tests
    test_registration_api()
    show_correct_usage()
    show_password_requirements()