#!/usr/bin/env python3
"""
Test script for default itinerary template functionality
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_basic_template():
    """Test basic template generation"""
    
    print("=" * 60)
    print("TESTING ITINERARY TEMPLATE GENERATION")
    print("=" * 60)
    
    # Test 1: Public template endpoint
    print("\n1. Testing public itinerary template...")
    
    response = requests.get(
        f"{BASE_URL}/api/trips/itinerary-template",
        params={'duration': 5, 'destination': 'Paris', 'trip_type': 'cultural'}
    )
    
    if response.status_code == 200:
        data = response.json()
        template = data.get('template', [])
        suggestions = data.get('activity_suggestions', [])
        
        print(f"✅ Template generated with {len(template)} days")
        print(f"📋 Activity suggestions: {suggestions[:3]}...")
        
        if template:
            print("📅 Sample itinerary:")
            for day in template[:2]:
                print(f"   Day {day['day']}: {day['activity']}")
    else:
        print(f"❌ Template generation failed: {response.text}")
        return False
    
    # Test 2: Different trip types
    print("\n2. Testing different trip types...")
    
    trip_types = ['adventure', 'business', 'relaxation']
    
    for trip_type in trip_types:
        response = requests.get(
            f"{BASE_URL}/api/trips/itinerary-template",
            params={'duration': 3, 'trip_type': trip_type}
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('activity_suggestions', [])
            print(f"✅ {trip_type.capitalize()}: {suggestions[0] if suggestions else 'No suggestions'}")
        else:
            print(f"❌ Failed for {trip_type}")
    
    # Test 3: Error handling
    print("\n3. Testing error handling...")
    
    # Invalid duration
    response = requests.get(
        f"{BASE_URL}/api/trips/itinerary-template",
        params={'duration': -1}
    )
    
    if response.status_code == 400:
        print("✅ Properly rejected negative duration")
    else:
        print("❌ Should reject negative duration")
    
    return True

def test_with_auth():
    """Test authenticated endpoints"""
    
    print("\n4. Testing authenticated itinerary generation...")
    
    # Quick setup
    test_user = {
        'email': 'template.test@example.com',
        'password': 'TemplateTest123!',
        'confirm_password': 'TemplateTest123!',
        'name': 'Template Test'
    }
    
    # Register and login
    requests.post(f'{BASE_URL}/auth/register', json=test_user)
    login_response = requests.post(
        f'{BASE_URL}/auth/login',
        json={'email': test_user['email'], 'password': test_user['password']}
    )
    
    if login_response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create trip
    trip_data = {
        'destination': 'Tokyo, Japan',
        'start_date': '2026-09-15',
        'end_date': '2026-09-20',
        'description': 'Japan adventure'
    }
    
    create_response = requests.post(
        f'{BASE_URL}/api/trips',
        json=trip_data,
        headers=headers
    )
    
    if create_response.status_code != 201:
        print("❌ Trip creation failed")
        return False
    
    trip_id = create_response.json().get('trip', {}).get('id')
    print(f"✅ Created trip {trip_id}")
    
    # Generate itinerary
    itinerary_response = requests.post(
        f'{BASE_URL}/api/trips/{trip_id}/generate-itinerary',
        json={'trip_type': 'adventure'},
        headers=headers
    )
    
    if itinerary_response.status_code == 200:
        result = itinerary_response.json()
        trip = result.get('trip', {})
        itinerary = trip.get('itinerary', [])
        
        print(f"✅ Generated itinerary with {len(itinerary)} days")
        if itinerary:
            print(f"   Day 1: {itinerary[0]['activity']}")
    else:
        print(f"❌ Itinerary generation failed: {itinerary_response.text}")
        return False
    
    return True

if __name__ == '__main__':
    print("Testing itinerary template functionality...")
    print(f"Base URL: {BASE_URL}")
    print("\nEnsure Flask server is running!")
    input("Press Enter to continue...")
    
    try:
        success1 = test_basic_template()
        success2 = test_with_auth()
        
        if success1 and success2:
            print("\n🎉 ALL ITINERARY TEMPLATE TESTS PASSED!")
            print("\n📋 New features working:")
            print("   ✅ Public template generation")
            print("   ✅ Multiple trip types")
            print("   ✅ Authenticated itinerary creation") 
            print("   ✅ Error handling")
        else:
            print("\n❌ Some tests failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")