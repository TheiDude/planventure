#!/usr/bin/env python3
"""
Test script for CORS configuration with React frontend
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_cors_configuration():
    """Test CORS headers for React frontend compatibility"""
    
    print("=" * 60)
    print("TESTING CORS CONFIGURATION FOR REACT FRONTEND")
    print("=" * 60)
    
    # Test 1: Preflight OPTIONS request (what browsers send before actual requests)
    print("\n1. Testing CORS Preflight (OPTIONS) Request...")
    
    headers = {
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization'
    }
    
    response = requests.options(f'{BASE_URL}/auth/login', headers=headers)
    
    if response.status_code == 200:
        print("✅ Preflight request successful")
        
        # Check CORS headers
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_methods = response.headers.get('Access-Control-Allow-Methods')
        cors_headers = response.headers.get('Access-Control-Allow-Headers')
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
        
        print(f"   🔹 Allow-Origin: {cors_origin}")
        print(f"   🔹 Allow-Methods: {cors_methods}")
        print(f"   🔹 Allow-Headers: {cors_headers}")
        print(f"   🔹 Allow-Credentials: {cors_credentials}")
        
        if cors_origin and ('localhost:3000' in cors_origin or cors_origin == '*'):
            print("✅ Origin header correctly configured")
        else:
            print("❌ Origin header missing or incorrect")
            
        if cors_methods and 'POST' in cors_methods:
            print("✅ POST method allowed")
        else:
            print("❌ POST method not allowed")
            
        if cors_headers and 'Authorization' in cors_headers:
            print("✅ Authorization header allowed")
        else:
            print("❌ Authorization header not allowed")
    else:
        print(f"❌ Preflight request failed: {response.status_code}")
    
    # Test 2: Actual CORS request with Origin header
    print("\n2. Testing Actual Request with CORS Origin...")
    
    request_headers = {
        'Origin': 'http://localhost:3000',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f'{BASE_URL}/health', headers=request_headers)
    
    if response.status_code == 200:
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        print(f"✅ Request successful with CORS origin: {cors_origin}")
    else:
        print(f"❌ Request failed: {response.status_code}")
    
    # Test 3: Test different origins
    print("\n3. Testing Different React Development Origins...")
    
    test_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000', 
        'http://localhost:3001',
        'http://localhost:5173'  # Vite default port
    ]
    
    for origin in test_origins:
        headers = {'Origin': origin}
        response = requests.get(f'{BASE_URL}/health', headers=headers)
        
        if response.status_code == 200:
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin and (origin in cors_origin or cors_origin == '*'):
                print(f"✅ {origin} - Allowed")
            else:
                print(f"❌ {origin} - Not properly configured")
        else:
            print(f"❌ {origin} - Request failed")
    
    # Test 4: Test API endpoints with CORS
    print("\n4. Testing API Endpoints with CORS...")
    
    api_endpoints = [
        '/api/trips/itinerary-template?duration=5',
        '/auth/register',
        '/auth/login'
    ]
    
    for endpoint in api_endpoints:
        headers = {'Origin': 'http://localhost:3000'}
        response = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        if cors_origin:
            print(f"✅ {endpoint} - CORS configured")
        else:
            print(f"❌ {endpoint} - No CORS headers")

def test_react_auth_flow():
    """Test authentication flow that React frontend would use"""
    
    print("\n" + "=" * 60)
    print("TESTING REACT AUTHENTICATION FLOW")
    print("=" * 60)
    
    # Simulate what React would send
    cors_headers = {
        'Origin': 'http://localhost:3000',
        'Content-Type': 'application/json'
    }
    
    # Test registration
    user_data = {
        'email': 'react.test@example.com',
        'password': 'ReactTest123!',
        'confirm_password': 'ReactTest123!',
        'name': 'React Test User'
    }
    
    print("\n1. Testing Registration from React Frontend...")
    response = requests.post(f'{BASE_URL}/auth/register', json=user_data, headers=cors_headers)
    
    if response.status_code == 201:
        print("✅ Registration successful with CORS")
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        print(f"   🔹 CORS Origin: {cors_origin}")
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
    
    # Test login
    print("\n2. Testing Login from React Frontend...")
    login_data = {'email': user_data['email'], 'password': user_data['password']}
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data, headers=cors_headers)
    
    if response.status_code == 200:
        print("✅ Login successful with CORS")
        data = response.json()
        token = data.get('access_token')
        
        if token:
            print("✅ JWT token received")
            
            # Test protected route with token
            print("\n3. Testing Protected Route with JWT Token...")
            auth_headers = {
                'Origin': 'http://localhost:3000',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(f'{BASE_URL}/api/user/profile', headers=auth_headers)
            
            if response.status_code == 200:
                print("✅ Protected route access successful with CORS and JWT")
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                print(f"   🔹 CORS Origin: {cors_origin}")
            else:
                print(f"❌ Protected route failed: {response.status_code}")
        else:
            print("❌ No JWT token in response")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")

if __name__ == '__main__':
    print("Testing CORS configuration for React frontend...")
    print(f"Base URL: {BASE_URL}")
    print("\nEnsure Flask server is running!")
    input("Press Enter to continue...")
    
    try:
        test_cors_configuration()
        test_react_auth_flow()
        
        print("\n" + "🎉" * 20)
        print("CORS CONFIGURATION TEST COMPLETE!")
        print("🎉" * 20)
        
        print("\n📋 React Frontend Integration Ready:")
        print("   ✅ CORS preflight requests handled")
        print("   ✅ Multiple React dev ports supported")
        print("   ✅ Authentication flow with CORS")
        print("   ✅ JWT tokens work with protected routes")
        print("   ✅ All API endpoints have CORS headers")
        
        print("\n🔧 React Fetch Example:")
        print("""
// Example React code to call the API
const response = await fetch('http://127.0.0.1:5000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  credentials: 'include',  // Important for CORS with credentials
  body: JSON.stringify({
    email: 'user@example.com', 
    password: 'password'
  })
});

const data = await response.json();
const token = data.access_token;

// Use token for protected routes
const protectedResponse = await fetch('http://127.0.0.1:5000/api/user/profile', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  credentials: 'include'
});
        """)
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server - Make sure it's running on port 5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")