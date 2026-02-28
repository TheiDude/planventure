#!/usr/bin/env python3
"""
Test edge cases that might have caused the original registration error.

This script tests various scenarios that could trigger the 
"An error occurred while creating your account" message.
"""

import json
from app import app
from models import db, User

def test_edge_cases():
    """Test various edge cases for registration"""
    
    print("🔍 Testing Registration Edge Cases")
    print("=" * 50)
    
    edge_cases = [
        {
            "name": "Normal Registration",
            "data": {
                "email": "normal@test.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            }
        },
        {
            "name": "Very Long Email",
            "data": {
                "email": "a" * 200 + "@verylongemail.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            }
        },
        {
            "name": "Special Characters in Email",
            "data": {
                "email": "test+tag@sub.domain.co.uk",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            }
        },
        {
            "name": "Maximum Password Length",
            "data": {
                "email": "maxpass@test.com",
                "password": "A1!" + "a" * 124,  # 127 chars
                "confirm_password": "A1!" + "a" * 124
            }
        },
        {
            "name": "Duplicate Registration",
            "data": {
                "email": "duplicate@test.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!"
            },
            "prepare": lambda: register_user("duplicate@test.com", "FirstPass123!")
        },
        {
            "name": "Empty String Fields",
            "data": {
                "email": "",
                "password": "",
                "confirm_password": ""
            }
        },
        {
            "name": "None Values",
            "data": {
                "email": None,
                "password": None,
                "confirm_password": None
            }
        },
        {
            "name": "Missing Fields",
            "data": {
                "email": "missing@test.com"
                # Missing password fields
            }
        },
        {
            "name": "Extra Fields",
            "data": {
                "email": "extra@test.com",
                "password": "ValidPass123!",
                "confirm_password": "ValidPass123!",
                "extra_field": "should_be_ignored",
                "malicious_field": "<script>alert('xss')</script>"
            }
        }
    ]
    
    with app.test_client() as client:
        for i, case in enumerate(edge_cases, 1):
            print(f"\n{i}. Testing: {case['name']}")
            
            # Run preparation if needed
            if 'prepare' in case:
                try:
                    case['prepare']()
                    print("   Preparation completed")
                except Exception as e:
                    print(f"   Preparation failed: {e}")
            
            try:
                response = client.post(
                    '/auth/register',
                    data=json.dumps(case['data']),
                    content_type='application/json'
                )
                
                response_data = response.get_json()
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 201:
                    print(f"   ✅ Success: {response_data['user']['email']}")
                else:
                    print(f"   ❌ Error: {response_data.get('message', 'Unknown error')}")
                
            except Exception as e:
                print(f"   💥 Exception: {str(e)}")

def register_user(email, password):
    """Helper function to register a user"""
    with app.app_context():
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return user
        return existing_user

def test_concurrent_registrations():
    """Test what happens with concurrent registrations of same email"""
    
    print(f"\n🔄 Testing Concurrent Registration Scenario")
    print("-" * 50)
    
    # Clean up first
    with app.app_context():
        existing_user = User.query.filter_by(email="concurrent@test.com").first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
    
    test_data = {
        "email": "concurrent@test.com",
        "password": "ConcurrentTest123!",
        "confirm_password": "ConcurrentTest123!"
    }
    
    with app.test_client() as client:
        # First registration
        print("First registration attempt...")
        response1 = client.post(
            '/auth/register',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"   Status: {response1.status_code}")
        if response1.status_code == 201:
            print("   ✅ First registration successful")
        
        # Immediate second registration (duplicate)
        print("Second registration attempt (duplicate)...")
        response2 = client.post(
            '/auth/register',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"   Status: {response2.status_code}")
        response2_data = response2.get_json()
        print(f"   Message: {response2_data.get('message', 'No message')}")

def cleanup_test_users():
    """Clean up all test users"""
    print(f"\n🧹 Cleaning up test users...")
    
    test_emails = [
        "normal@test.com",
        "maxpass@test.com", 
        "duplicate@test.com",
        "missing@test.com",
        "extra@test.com",
        "concurrent@test.com",
        "diagnostic@test.com",
        "api.diagnostic@test.com"
    ]
    
    with app.app_context():
        deleted_count = 0
        for email in test_emails:
            user = User.query.filter_by(email=email).first()
            if user:
                db.session.delete(user)
                deleted_count += 1
        
        if deleted_count > 0:
            db.session.commit()
            print(f"   Cleaned up {deleted_count} test users")
        else:
            print("   No test users to clean up")

if __name__ == "__main__":
    test_edge_cases()
    test_concurrent_registrations()
    cleanup_test_users()
    
    print(f"\n🎯 If you're still getting registration errors:")
    print("• Check your JSON payload format")
    print("• Ensure password and confirm_password match exactly") 
    print("• Verify all required fields are present")
    print("• Check server logs for detailed error messages")
    print("• The enhanced error handling now provides more specific error details")