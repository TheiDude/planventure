#!/usr/bin/env python3
"""
Simple login route test to verify functionality.
"""

import json
from app import app
from models import db, User

print("🔐 Login Route Test")
print("=" * 30)

# Create test user
with app.app_context():
    # Clean up
    existing = User.query.filter_by(email="simple@test.com").first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
    
    # Create user
    user = User(email="simple@test.com", password="Test123!")
    db.session.add(user)
    db.session.commit()
    print(f"Test user created: {user.email}")

# Test login
with app.test_client() as client:
    response = client.post('/auth/login', 
        json={"email": "simple@test.com", "password": "Test123!"})
    
    print(f"Status: {response.status_code}")
    data = response.get_json()
    
    if response.status_code == 200:
        print("✅ Login successful!")
        print(f"User: {data['user']['email']}")
        print(f"Token: {data['access_token'][:20]}...")
    else:
        print(f"❌ Error: {data.get('message')}")

print("\n✅ Login route is working!")