#!/usr/bin/env python3
"""
Quick fix example for the "Passwords do not match" error.

This shows exactly how to make a successful registration request.
"""

import json
from app import app

def demonstrate_fix():
    """Show the exact fix for password mismatch error"""
    
    print("🔧 Fix for 'Passwords do not match' error")
    print("=" * 50)
    
    print("❌ This will cause the error:")
    bad_request = {
        "email": "test@example.com",
        "password": "MyPassword123!",
        "confirm_password": "MyPassword123"  # Missing exclamation mark!
    }
    
    print("JSON Payload (INCORRECT):")
    print(json.dumps(bad_request, indent=2))
    
    print("\n✅ This is the correct format:")
    good_request = {
        "email": "test@example.com", 
        "password": "MyPassword123!",
        "confirm_password": "MyPassword123!"  # Exact match!
    }
    
    print("JSON Payload (CORRECT):")
    print(json.dumps(good_request, indent=2))
    
    print("\n🧪 Testing both requests:")
    
    with app.test_client() as client:
        # Test the bad request
        print("\n1. Testing incorrect request...")
        response = client.post(
            '/auth/register',
            data=json.dumps(bad_request),
            content_type='application/json'
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 201:
            error_data = response.get_json()
            print(f"   ❌ Error: {error_data['message']}")
        
        # Test the good request
        print("\n2. Testing correct request...")
        response = client.post(
            '/auth/register',
            data=json.dumps(good_request),
            content_type='application/json'
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            success_data = response.get_json()
            print(f"   ✅ Success: {success_data['message']}")
            print(f"   ✅ User created: {success_data['user']['email']}")
        else:
            error_data = response.get_json()
            print(f"   ❌ Unexpected error: {error_data['message']}")

def show_curl_examples():
    """Show working curl commands"""
    
    print("\n🌐 Working curl examples:")
    print("=" * 30)
    
    print("# This will work:")
    print("curl -X POST http://127.0.0.1:5001/auth/register \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "email": "newuser@planventure.com",')
    print('    "password": "SecurePass123!",')
    print('    "confirm_password": "SecurePass123!"')
    print("  }'")
    
    print("\n# This will fail with 'Passwords do not match':")
    print("curl -X POST http://127.0.0.1:5001/auth/register \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "email": "newuser@planventure.com",')
    print('    "password": "SecurePass123!",')
    print('    "confirm_password": "SecurePass123"')  # Missing !
    print("  }'")

if __name__ == "__main__":
    # Clean up any existing test user first
    from models import db, User
    
    with app.app_context():
        existing_user = User.query.filter_by(email="test@example.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
    
    demonstrate_fix()
    show_curl_examples()