#!/usr/bin/env python3
"""
Integration test for authentication workflow.

This script tests the complete authentication flow including registration,
login, and JWT token usage within the Flask application context.
"""

from app import app
from models import db, User
from auth_routes import validate_email, validate_password
import json

def test_registration_workflow():
    """Test complete user registration workflow"""
    print("📝 Testing Registration Workflow")
    print("=" * 40)
    
    with app.app_context():
        # Clear any existing test user
        test_email = "integration.test@planventure.com"
        existing_user = User.query.filter_by(email=test_email).first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("   🧹 Cleaned up existing test user")
        
        # Test data
        user_data = {
            "email": test_email,
            "password": "TestPass123!",
            "confirm_password": "TestPass123!"
        }
        
        # Step 1: Validate email format
        print("   1. Email validation...")
        is_valid = validate_email(user_data["email"])
        assert is_valid, f"Email validation failed for {user_data['email']}"
        print(f"      ✅ Email format valid: {user_data['email']}")
        
        # Step 2: Validate password strength
        print("   2. Password validation...")
        is_valid, error = validate_password(user_data["password"])
        assert is_valid, f"Password validation failed: {error}"
        print(f"      ✅ Password strength valid")
        
        # Step 3: Check password confirmation
        print("   3. Password confirmation...")
        assert user_data["password"] == user_data["confirm_password"], "Passwords don't match"
        print(f"      ✅ Password confirmation matches")
        
        # Step 4: Create user
        print("   4. User creation...")
        new_user = User(email=user_data["email"], password=user_data["password"])
        db.session.add(new_user)
        db.session.commit()
        print(f"      ✅ User created with ID: {new_user.id}")
        
        # Step 5: Generate tokens
        print("   5. JWT token generation...")
        tokens = new_user.generate_tokens()
        assert "access_token" in tokens, "Access token not generated"
        assert "refresh_token" in tokens, "Refresh token not generated"
        assert "expires_in" in tokens, "Token expiration not set"
        print(f"      ✅ Tokens generated successfully")
        print(f"         Access token: {tokens['access_token'][:30]}...")
        print(f"         Refresh token: {tokens['refresh_token'][:30]}...")
        print(f"         Expires in: {tokens['expires_in']} seconds")
        
        # Step 6: Verify token works
        print("   6. Token verification...")
        user_id_from_token = User.verify_token(tokens["access_token"])
        assert user_id_from_token == new_user.id, "Token verification failed"
        print(f"      ✅ Token verified for user ID: {user_id_from_token}")
        
        return new_user, tokens

def test_login_workflow(existing_user):
    """Test user login workflow"""
    print("\n🔐 Testing Login Workflow")
    print("=" * 40)
    
    with app.app_context():
        # Test login credentials
        login_data = {
            "email": existing_user.email,
            "password": "TestPass123!"
        }
        
        # Step 1: Find user by email
        print("   1. User lookup...")
        user = User.query.filter_by(email=login_data["email"]).first()
        assert user is not None, "User not found"
        print(f"      ✅ User found: {user.email}")
        
        # Step 2: Verify password
        print("   2. Password verification...")
        is_valid = user.check_password(login_data["password"])
        assert is_valid, "Password verification failed"
        print(f"      ✅ Password verified")
        
        # Step 3: Generate new tokens
        print("   3. Token generation...")
        tokens = user.generate_tokens()
        assert "access_token" in tokens, "Access token not generated"
        print(f"      ✅ New tokens generated")
        print(f"         Access token: {tokens['access_token'][:30]}...")
        
        return tokens

def test_authentication_errors():
    """Test authentication error scenarios"""
    print("\n❌ Testing Error Scenarios")
    print("=" * 40)
    
    with app.app_context():
        # Test 1: Invalid email format
        print("   1. Invalid email format...")
        invalid_emails = ["invalid", "@example.com", "test@"]
        for email in invalid_emails:
            is_valid = validate_email(email)
            assert not is_valid, f"Should be invalid: {email}"
        print("      ✅ Invalid emails properly rejected")
        
        # Test 2: Weak passwords
        print("   2. Weak password validation...")
        weak_passwords = ["short", "nouppercase123!", "NOLOWERCASE123!", "NoSpecialChar123"]
        for password in weak_passwords:
            is_valid, error = validate_password(password)
            assert not is_valid, f"Should be invalid: {password}"
        print("      ✅ Weak passwords properly rejected")
        
        # Test 3: Non-existent user login
        print("   3. Non-existent user login...")
        fake_user = User.query.filter_by(email="doesnotexist@example.com").first()
        assert fake_user is None, "Non-existent user should not be found"
        print("      ✅ Non-existent user properly handled")
        
        # Test 4: Wrong password
        print("   4. Wrong password verification...")
        test_user = User.query.first()
        if test_user:
            is_valid = test_user.check_password("WrongPassword123!")
            assert not is_valid, "Wrong password should not validate"
            print("      ✅ Wrong password properly rejected")

def test_user_data_serialization():
    """Test user data serialization for API responses"""
    print("\n📊 Testing Data Serialization")
    print("=" * 40)
    
    with app.app_context():
        user = User.query.first()
        if user:
            # Test to_dict method
            user_dict = user.to_dict()
            
            # Check required fields
            required_fields = ['id', 'email', 'created_at', 'updated_at', 'trip_count']
            for field in required_fields:
                assert field in user_dict, f"Missing field: {field}"
            
            # Check sensitive data is not included
            sensitive_fields = ['password_hash', 'password']
            for field in sensitive_fields:
                assert field not in user_dict, f"Sensitive field exposed: {field}"
            
            print("      ✅ User serialization secure")
            print(f"         Fields: {list(user_dict.keys())}")

def main():
    """Run all authentication tests"""
    print("🧪 PlanVenture Authentication Integration Tests")
    print("=" * 60)
    
    try:
        # Test registration workflow
        user, tokens = test_registration_workflow()
        
        # Test login workflow
        login_tokens = test_login_workflow(user)
        
        # Test error scenarios
        test_authentication_errors()
        
        # Test data serialization
        test_user_data_serialization()
        
        print("\n🎉 All authentication tests passed!")
        print(f"✅ User registration successful")
        print(f"✅ Login workflow functional")
        print(f"✅ JWT token system working")
        print(f"✅ Security validations in place")
        print(f"✅ Error handling proper")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False
    
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)