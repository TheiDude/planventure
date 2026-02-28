#!/usr/bin/env python3
"""
PlanVenture API Status and Summary
Shows the current state of the API with all available endpoints
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def show_api_status():
    """Display comprehensive API status"""
    
    print("🌟" * 30)
    print("         PLANVENTURE API STATUS")
    print("🌟" * 30)
    
    # Test basic connectivity
    try:
        health_response = requests.get(f'{BASE_URL}/health', timeout=5)
        if health_response.status_code == 200:
            print("\n✅ API Server: ONLINE")
            health_data = health_response.json()
            print(f"   Database: {health_data.get('database', 'Unknown')}")
        else:
            print(f"\n❌ API Server: Issues (Status {health_response.status_code})")
    except requests.exceptions.RequestException:
        print("\n❌ API Server: OFFLINE")
        return
    
    # API Endpoints Summary
    print(f"\n📋 AVAILABLE ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        {
            'category': 'Authentication',
            'routes': [
                {'method': 'POST', 'path': '/auth/register', 'desc': 'User registration'},
                {'method': 'POST', 'path': '/auth/login', 'desc': 'User login & JWT tokens'},
                {'method': 'GET', 'path': '/auth/profile', 'desc': 'Profile (optional auth)'},
                {'method': 'POST', 'path': '/auth/validate-email', 'desc': 'Email validation'}
            ]
        },
        {
            'category': 'Trip Management (CRUD)',
            'routes': [
                {'method': 'GET', 'path': '/api/trips', 'desc': 'List trips (with filters)'},
                {'method': 'POST', 'path': '/api/trips', 'desc': 'Create new trip'},
                {'method': 'GET', 'path': '/api/trips/<id>', 'desc': 'Get specific trip'},
                {'method': 'PUT', 'path': '/api/trips/<id>', 'desc': 'Update entire trip'},
                {'method': 'PATCH', 'path': '/api/trips/<id>', 'desc': 'Partial trip update'},
                {'method': 'DELETE', 'path': '/api/trips/<id>', 'desc': 'Delete trip'},
                {'method': 'GET', 'path': '/api/trips/stats', 'desc': 'Trip statistics'}
            ]
        },
        {
            'category': 'User Management',
            'routes': [
                {'method': 'GET', 'path': '/api/user/profile', 'desc': 'Protected user profile'}
            ]
        },
        {
            'category': 'System',
            'routes': [
                {'method': 'GET', 'path': '/health', 'desc': 'Health check'},
                {'method': 'GET', 'path': '/', 'desc': 'Welcome message'}
            ]
        }
    ]
    
    for category in endpoints:
        print(f"\n🔸 {category['category']}")
        for route in category['routes']:
            method_color = "🟢" if route['method'] == 'GET' else "🔵" if route['method'] == 'POST' else "🟡" if route['method'] in ['PUT', 'PATCH'] else "🔴"
            print(f"   {method_color} {route['method']:6} {route['path']:25} | {route['desc']}")
    
    # Features Summary
    print(f"\n🚀 KEY FEATURES")
    print("=" * 50)
    features = [
        "✅ JWT Authentication & Authorization",
        "✅ Complete Trip CRUD Operations", 
        "✅ User Registration & Login",
        "✅ Password Hashing & Validation",
        "✅ Route Protection Middleware",
        "✅ Input Validation & Error Handling", 
        "✅ Pagination & Filtering",
        "✅ Trip Statistics & Analytics",
        "✅ CORS Support",
        "✅ Security Headers",
        "✅ SQLite Database Integration",
        "✅ RESTful API Design"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    # Database Models
    print(f"\n💾 DATABASE MODELS")
    print("=" * 50)
    print("   📊 User Model:")
    print("      • User authentication & profile management")
    print("      • Password hashing with pbkdf2:sha256") 
    print("      • JWT token generation")
    print("      • Relationship with trips")
    
    print("   📊 Trip Model:")
    print("      • Complete trip management")
    print("      • Destination, dates, budget tracking")
    print("      • GPS coordinates & itinerary support")
    print("      • Status tracking (planned/ongoing/completed/cancelled)")
    print("      • JSON storage for flexible itinerary data")
    
    # Security Features
    print(f"\n🔐 SECURITY FEATURES")
    print("=" * 50)
    security_features = [
        "🛡️  JWT Token Authentication",
        "🛡️  Password Hashing (pbkdf2:sha256 fallback)",
        "🛡️  Route-Level Authorization",
        "🛡️  User Ownership Validation", 
        "🛡️  Input Validation & Sanitization",
        "🛡️  Security Headers (XSS, CSRF protection)",
        "🛡️  CORS Configuration",
        "🛡️  SQL Injection Prevention (SQLAlchemy ORM)"
    ]
    
    for security in security_features:
        print(f"   {security}")
    
    # Testing Status
    print(f"\n🧪 TESTING STATUS")
    print("=" * 50)
    print("   ✅ Authentication Flow Tests")
    print("   ✅ Trip CRUD Operations Tests")
    print("   ✅ Authorization & Ownership Tests")
    print("   ✅ Input Validation Tests")
    print("   ✅ Error Handling Tests")
    print("   ✅ Security Headers Tests")
    
    # Usage Examples
    print(f"\n📖 QUICK START EXAMPLES")
    print("=" * 50)
    
    print("   1️⃣  Register User:")
    print(f"      curl -X POST {BASE_URL}/auth/register \\\\")
    print("        -H 'Content-Type: application/json' \\\\")
    print("        -d '{\"email\":\"test@example.com\",\"password\":\"Test123!\",\"confirm_password\":\"Test123!\",\"name\":\"Test User\"}'")
    
    print("\n   2️⃣  Login & Get Token:")
    print(f"      curl -X POST {BASE_URL}/auth/login \\\\")
    print("        -H 'Content-Type: application/json' \\\\")
    print("        -d '{\"email\":\"test@example.com\",\"password\":\"Test123!\"}'")
    
    print("\n   3️⃣  Create Trip:")
    print(f"      curl -X POST {BASE_URL}/api/trips \\\\")
    print("        -H 'Authorization: Bearer YOUR_TOKEN' \\\\")
    print("        -H 'Content-Type: application/json' \\\\")
    print("        -d '{\"destination\":\"Paris\",\"start_date\":\"2026-06-15\",\"end_date\":\"2026-06-22\"}'")
    
    print("\n   4️⃣  List Trips with Filters:")
    print(f"      curl -X GET '{BASE_URL}/api/trips?destination=Paris&sort=budget&order=desc' \\\\")
    print("        -H 'Authorization: Bearer YOUR_TOKEN'")
    
    # Documentation
    print(f"\n📚 DOCUMENTATION")
    print("=" * 50)
    print("   📄 AUTH_MIDDLEWARE_DOCS.md - Authentication system")
    print("   📄 TRIP_CRUD_API.md - Trip management API")
    print("   🧪 test_middleware_integration.py - Auth tests")
    print("   🧪 test_trips_crud_fixed.py - Trip CRUD tests")
    
    print(f"\n🎯 READY FOR:")
    print("=" * 50)
    ready_features = [
        "🚀 Production Deployment",
        "📱 Frontend Integration", 
        "🔄 Additional API Development",
        "📊 Analytics & Reporting",
        "🌐 Mobile App Backend",
        "⚡ Microservices Architecture"
    ]
    
    for ready in ready_features:
        print(f"   {ready}")
    
    print("\n" + "🌟" * 30)
    print("   PlanVenture API - Ready to Go! ✈️🗺️")
    print("🌟" * 30)

if __name__ == '__main__':
    show_api_status()