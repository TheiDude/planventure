#!/usr/bin/env python3
"""
JWT functionality test script for PlanVenture API.

This script demonstrates JWT token generation, validation, and usage.
"""

from app import app
from models import db, User
from jwt_utils import (
    generate_token, 
    validate_token, 
    create_token_response,
    extract_token_from_header
)

def test_jwt_functionality():
    """Test all JWT functions"""
    with app.app_context():
        print("🔐 Testing JWT Token Generation & Validation")
        print("=" * 50)
        
        # Test basic token generation
        print("1. Testing token generation...")
        test_user_id = 123
        token = generate_token(test_user_id)
        print(f"✅ Token generated: {token[:30]}...")
        
        # Test token validation
        print("\n2. Testing token validation...")
        payload = validate_token(token)
        if payload and payload.get('user_id') == test_user_id:
            print(f"✅ Token valid - User ID: {payload['user_id']}")
            print(f"   Expires: {payload.get('exp')}")
        else:
            print("❌ Token validation failed")
        
        # Test token response creation
        print("\n3. Testing token response creation...")
        token_response = create_token_response(test_user_id)
        print("✅ Token response created:")
        print(f"   - Access token: {token_response['access_token'][:30]}...")
        print(f"   - Refresh token: {token_response['refresh_token'][:30]}...")
        print(f"   - Token type: {token_response['token_type']}")
        print(f"   - Expires in: {token_response['expires_in']} seconds")
        
        # Test header extraction
        print("\n4. Testing header extraction...")
        auth_header = f"Bearer {token}"
        extracted_token = extract_token_from_header(auth_header)
        if extracted_token == token:
            print("✅ Token extracted from header successfully")
        else:
            print("❌ Token extraction failed")
        
        # Test User model JWT methods
        print("\n5. Testing User model JWT methods...")
        test_user = User("test@example.com", "password123")
        user_tokens = test_user.generate_tokens()
        print(f"✅ User tokens generated: {len(user_tokens)} items")
        
        # Test token verification via User model
        user_id_verified = User.verify_token(user_tokens['access_token'])
        if user_id_verified == test_user.id:
            print(f"✅ User token verification successful - ID: {user_id_verified}")
        else:
            print("❌ User token verification failed")
        
        print("\n🎉 All JWT tests completed!")

if __name__ == "__main__":
    test_jwt_functionality()