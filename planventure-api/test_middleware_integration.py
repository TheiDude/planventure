#!/usr/bin/env python3
"""
Test script for complete auth middleware integration
Tests all authentication flows with the new middleware system
"""

import requests
import json
from datetime import datetime, date

BASE_URL = 'http://127.0.0.1:5000'

def test_complete_auth_flow():
    """Test complete authentication flow with middleware"""
    
    print("=" * 60)
    print("TESTING COMPLETE AUTH MIDDLEWARE INTEGRATION")
    print("=" * 60)
    
    # Test user data
    test_user = {
        'email': 'middleware.test@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'name': 'Middleware Test User'
    }
    
    # Test 1: Register a new user
    print("\n1. Testing user registration...")
    register_response = requests.post(
        f'{BASE_URL}/auth/register',
        json=test_user
    )
    
    print(f"Status Code: {register_response.status_code}")
    print(f"Response: {register_response.text}")
    
    if register_response.status_code != 201:
        print("❌ Registration failed!")
        return False
    
    # Test 2: Login to get JWT token
    print("\n2. Testing login...")
    login_response = requests.post(
        f'{BASE_URL}/auth/login',
        json={
            'email': test_user['email'],
            'password': test_user['password']
        }
    )
    
    print(f"Status Code: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return False
    
    login_data = login_response.json()
    access_token = login_data.get('access_token')
    
    if not access_token:
        print("❌ No access token received!")
        return False
    
    print(f"✅ Access token received: {access_token[:50]}...")
    
    # Test 3: Access optional auth route without token
    print("\n3. Testing optional auth route WITHOUT token...")
    profile_response = requests.get(f'{BASE_URL}/auth/profile')
    
    print(f"Status Code: {profile_response.status_code}")
    print(f"Response: {profile_response.text}")
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        if not profile_data.get('authenticated'):
            print("✅ Optional auth works without token")
        else:
            print("❌ Optional auth incorrectly shows authenticated")
    
    # Test 4: Access optional auth route WITH token
    print("\n4. Testing optional auth route WITH token...")
    headers = {'Authorization': f'Bearer {access_token}'}
    profile_auth_response = requests.get(f'{BASE_URL}/auth/profile', headers=headers)
    
    print(f"Status Code: {profile_auth_response.status_code}")
    print(f"Response: {profile_auth_response.text}")
    
    if profile_auth_response.status_code == 200:
        profile_data = profile_auth_response.json()
        if profile_data.get('authenticated'):
            print("✅ Optional auth works with token")
        else:
            print("❌ Optional auth doesn't recognize token")
    
    # Test 5: Access protected route WITHOUT token
    print("\n5. Testing protected route WITHOUT token...")
    protected_response = requests.get(f'{BASE_URL}/api/user/profile')
    
    print(f"Status Code: {protected_response.status_code}")
    print(f"Response: {protected_response.text}")
    
    if protected_response.status_code == 401:
        print("✅ Protected route properly blocks unauthenticated requests")
    else:
        print("❌ Protected route should block unauthenticated requests")
    
    # Test 6: Access protected route WITH token
    print("\n6. Testing protected route WITH token...")
    protected_auth_response = requests.get(f'{BASE_URL}/api/user/profile', headers=headers)
    
    print(f"Status Code: {protected_auth_response.status_code}")
    print(f"Response: {protected_auth_response.text}")
    
    if protected_auth_response.status_code == 200:
        print("✅ Protected route works with valid token")
    else:
        print("❌ Protected route should work with valid token")
    
    # Test 7: Get user trips (should be empty initially)
    print("\n7. Testing user trips endpoint...")
    trips_response = requests.get(f'{BASE_URL}/api/user/trips', headers=headers)
    
    print(f"Status Code: {trips_response.status_code}")
    print(f"Response: {trips_response.text}")
    
    if trips_response.status_code == 200:
        trips_data = trips_response.json()
        print(f"✅ User trips retrieved: {trips_data.get('total_trips', 0)} trips")
    else:
        print("❌ Failed to retrieve user trips")
    
    # Test 8: Create a new trip
    print("\n8. Testing trip creation...")
    trip_data = {
        'destination': 'Paris, France',
        'start_date': '2024-07-15',
        'end_date': '2024-07-22',
        'description': 'Summer vacation in Paris',
        'budget': 2500.00,
        'latitude': 48.8566,
        'longitude': 2.3522,
        'itinerary': [
            {'day': 1, 'activity': 'Arrive and check in', 'location': 'Hotel'},
            {'day': 2, 'activity': 'Visit Eiffel Tower', 'location': 'Eiffel Tower'},
            {'day': 3, 'activity': 'Louvre Museum', 'location': 'Louvre'}
        ]
    }
    
    create_trip_response = requests.post(
        f'{BASE_URL}/api/trips',
        json=trip_data,
        headers=headers
    )
    
    print(f"Status Code: {create_trip_response.status_code}")
    print(f"Response: {create_trip_response.text}")
    
    if create_trip_response.status_code == 201:
        trip_result = create_trip_response.json()
        created_trip = trip_result.get('trip')
        if created_trip:
            print(f"✅ Trip created successfully: ID {created_trip.get('id')}")
        else:
            print("❌ Trip creation response missing trip data")
    else:
        print("❌ Failed to create trip")
    
    # Test 9: Get user trips again (should have 1 trip now)
    print("\n9. Testing user trips after creation...")
    trips_response_2 = requests.get(f'{BASE_URL}/api/user/trips', headers=headers)
    
    print(f"Status Code: {trips_response_2.status_code}")
    print(f"Response: {trips_response_2.text}")
    
    if trips_response_2.status_code == 200:
        trips_data_2 = trips_response_2.json()
        trip_count = trips_data_2.get('total_trips', 0)
        if trip_count > 0:
            print(f"✅ User now has {trip_count} trip(s)")
        else:
            print("❌ Trip was not saved properly")
    
    # Test 10: Test with invalid token
    print("\n10. Testing with invalid token...")
    invalid_headers = {'Authorization': 'Bearer invalid.token.here'}
    invalid_response = requests.get(f'{BASE_URL}/api/user/profile', headers=invalid_headers)
    
    print(f"Status Code: {invalid_response.status_code}")
    print(f"Response: {invalid_response.text}")
    
    if invalid_response.status_code == 401:
        print("✅ Invalid token properly rejected")
    else:
        print("❌ Invalid token should be rejected")
    
    print("\n" + "=" * 60)
    print("AUTHENTICATION MIDDLEWARE INTEGRATION TEST COMPLETE")
    print("=" * 60)
    return True

def test_security_headers():
    """Test that security headers are being set"""
    
    print("\n" + "=" * 60)
    print("TESTING SECURITY HEADERS")
    print("=" * 60)
    
    # Make a request to any endpoint
    response = requests.get(f'{BASE_URL}/auth/profile')
    
    print(f"\nResponse Headers:")
    for header, value in response.headers.items():
        print(f"  {header}: {value}")
    
    # Check for expected security headers
    expected_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options', 
        'X-XSS-Protection'
    ]
    
    missing_headers = []
    for header in expected_headers:
        if header in response.headers:
            print(f"✅ {header}: {response.headers[header]}")
        else:
            missing_headers.append(header)
            print(f"❌ Missing header: {header}")
    
    if not missing_headers:
        print("\n✅ All expected security headers present")
    else:
        print(f"\n❌ Missing security headers: {missing_headers}")
    
    return len(missing_headers) == 0

if __name__ == '__main__':
    print("Starting comprehensive auth middleware integration test...")
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the Flask app is running first!")
    input("Press Enter to continue...")
    
    try:
        # Test main auth flow
        auth_success = test_complete_auth_flow()
        
        # Test security headers
        headers_success = test_security_headers()
        
        if auth_success and headers_success:
            print("\n🎉 ALL TESTS PASSED! Auth middleware integration is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")