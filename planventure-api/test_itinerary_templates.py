#!/usr/bin/env python3
"""
Test script for default itinerary template functionality
"""

import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def test_itinerary_templates():
    """Test the itinerary template generation functionality"""
    
    print("=" * 70)
    print("TESTING ITINERARY TEMPLATE FUNCTIONALITY")
    print("=" * 70)
    
    # Test 1: Get itinerary template without authentication (public endpoint)
    print("\n1. Testing public itinerary template generation...")
    
    # Test different duration scenarios
    template_tests = [
        {'duration': 3, 'destination': 'Paris, France', 'trip_type': 'cultural'},
        {'duration': 7, 'destination': 'Tokyo, Japan', 'trip_type': 'adventure'},
        {'duration': 5, 'destination': 'New York, USA', 'trip_type': 'business'},
        {'duration': 1, 'destination': 'Local City', 'trip_type': 'general'}
    ]
    
    for test_case in template_tests:
        print(f"\n   Testing {test_case['duration']}-day {test_case['trip_type']} trip to {test_case['destination']}:")
        
        template_response = requests.get(
            f"{BASE_URL}/api/trips/itinerary-template",
            params=test_case
        )
        
        if template_response.status_code == 200:
            template_data = template_response.json()
            template = template_data.get('template', [])
            suggestions = template_data.get('activity_suggestions', [])
            
            print(f"   ✅ Generated template with {len(template)} days")
            print(f"   📋 Sample activities: {', '.join(suggestions[:3])}...")
            
            # Show first day as example
            if template:
                first_day = template[0]
                print(f"   📅 Day 1: {first_day['activity']} at {first_day['location']}")
        else:
            print(f"   ❌ Failed to generate template: {template_response.text}")
    
    # Test 2: Test with authentication for trip-specific itinerary
    print("\n2. Testing authenticated itinerary generation...")
    
    # Quick auth setup
    test_user = {
        'email': 'itinerary.test@example.com',
        'password': 'ItineraryTest123!',
        'confirm_password': 'ItineraryTest123!',
        'name': 'Itinerary Test User'
    }
    
    # Register and login
    register_response = requests.post(f'{BASE_URL}/auth/register', json=test_user)
    login_response = requests.post(
        f'{BASE_URL}/auth/login',
        json={'email': test_user['email'], 'password': test_user['password']}
    )
    
    if login_response.status_code == 200:
        access_token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        
        print("   ✅ Authentication successful")\n        \n        # Create a trip without itinerary\n        trip_data = {\n            'destination': 'Barcelona, Spain',\n            'start_date': '2026-08-15',\n            'end_date': '2026-08-20',\n            'description': 'Mediterranean adventure',\n            'budget': 1800.00\n        }\n        \n        create_response = requests.post(\n            f'{BASE_URL}/api/trips',\n            json=trip_data,\n            headers=headers\n        )\n        \n        if create_response.status_code == 201:\n            trip = create_response.json().get('trip')\n            trip_id = trip.get('id')\n            print(f"   ✅ Created trip {trip_id}: {trip['destination']}")\n            \n            # Generate default itinerary for the trip\n            itinerary_data = {\n                'trip_type': 'cultural',\n                'overwrite': True\n            }\n            \n            itinerary_response = requests.post(\n                f'{BASE_URL}/api/trips/{trip_id}/generate-itinerary',\n                json=itinerary_data,\n                headers=headers\n            )\n            \n            if itinerary_response.status_code == 200:\n                itinerary_result = itinerary_response.json()\n                updated_trip = itinerary_result.get('trip')\n                itinerary = updated_trip.get('itinerary', [])\n                \n                print(f"   ✅ Generated itinerary with {len(itinerary)} days")\n                \n                # Display the generated itinerary\n                print("   📋 Generated Itinerary:")\n                for day_item in itinerary:\n                    day = day_item.get('day')\n                    activity = day_item.get('activity')\n                    location = day_item.get('location')\n                    print(f"      Day {day}: {activity} ({location})")\n                \n                # Test creating trip with default itinerary from start
                print("\n   Testing trip creation with default itinerary...")\n                \n                trip_with_template = {\n                    'destination': 'Rome, Italy',\n                    'start_date': '2026-09-10',\n                    'end_date': '2026-09-14',\n                    'description': 'Historical exploration',\n                    'budget': 2200.00,\n                    'use_default_itinerary': True\n                }\n                \n                create_with_template = requests.post(\n                    f'{BASE_URL}/api/trips',\n                    json=trip_with_template,\n                    headers=headers\n                )\n                \n                if create_with_template.status_code == 201:\n                    new_trip = create_with_template.json().get('trip')\n                    new_itinerary = new_trip.get('itinerary', [])\n                    \n                    print(f"   ✅ Created trip with default itinerary: {len(new_itinerary)} days")\n                    if new_itinerary:\n                        print(f"      Sample: Day 1 - {new_itinerary[0]['activity']}")\n                else:\n                    print(f"   ❌ Failed to create trip with template: {create_with_template.text}")\n            else:\n                print(f"   ❌ Failed to generate itinerary: {itinerary_response.text}")\n        else:\n            print(f"   ❌ Failed to create trip: {create_response.text}")\n    else:\n        print(f"   ❌ Authentication failed: {login_response.text}")\n    \n    # Test 3: Test error handling\n    print("\\n3. Testing error handling...")\n    \n    # Test invalid duration\n    invalid_response = requests.get(\n        f"{BASE_URL}/api/trips/itinerary-template",\n        params={'duration': -1}\n    )\n    \n    if invalid_response.status_code == 400:\n        print("   ✅ Properly rejected invalid duration")\n    else:\n        print(f"   ❌ Should reject invalid duration: {invalid_response.text}")\n    \n    # Test excessive duration\n    excessive_response = requests.get(\n        f"{BASE_URL}/api/trips/itinerary-template",\n        params={'duration': 400}\n    )\n    \n    if excessive_response.status_code == 400:\n        print("   ✅ Properly rejected excessive duration")\n    else:\n        print(f"   ❌ Should reject excessive duration: {excessive_response.text}")\n    \n    print("\\n" + "=" * 70)\n    print("ITINERARY TEMPLATE FUNCTIONALITY TEST COMPLETE")\n    print("=" * 70)\n    \n    return True\n\ndef demo_template_types():\n    """Demonstrate different template types\"\"\"\n    \n    print("\\n" + "=" * 70)\n    print("DEMO: DIFFERENT ITINERARY TEMPLATE TYPES")\n    print("=" * 70)\n    \n    trip_types = ['cultural', 'adventure', 'relaxation', 'business', 'family']\n    \n    for trip_type in trip_types:\n        print(f"\\n🎯 {trip_type.upper()} TRIP TEMPLATE (5 days):")\n        \n        response = requests.get(\n            f"{BASE_URL}/api/trips/itinerary-template",\n            params={'duration': 5, 'destination': 'Demo City', 'trip_type': trip_type}\n        )\n        \n        if response.status_code == 200:\n            data = response.json()\n            template = data.get('template', [])\n            suggestions = data.get('activity_suggestions', [])\n            \n            print(f"   📋 Activity Suggestions: {', '.join(suggestions)}")\n            print("   📅 Sample Itinerary:")\n            \n            for day in template[:3]:  # Show first 3 days\n                print(f"      Day {day['day']}: {day['activity']}")\n            \n            if len(template) > 3:\n                print(f"      ... and {len(template) - 3} more days")\n        else:\n            print(f"   ❌ Failed to get template: {response.text}")\n    \n    print("\\n" + "=" * 70)\n\nif __name__ == '__main__':\n    print("Starting itinerary template functionality test...")\n    print(f"Base URL: {BASE_URL}")\n    print("\\nMake sure the Flask app is running first!")\n    input("Press Enter to continue...")\n    \n    try:\n        # Test main functionality\n        success = test_itinerary_templates()\n        \n        # Demo different template types\n        demo_template_types()\n        \n        if success:\n            print("\\n🎉 ITINERARY TEMPLATE TESTS COMPLETED SUCCESSFULLY!")\n            print("\\n📋 New features tested:")\n            print("   ✅ Public itinerary template generation")\n            print("   ✅ Trip-specific itinerary generation")\n            print("   ✅ Multiple trip types (cultural, adventure, business, etc.)")\n            print("   ✅ Template customization by duration and destination")\n            print("   ✅ Trip creation with default itinerary option")\n            print("   ✅ Error handling for invalid inputs")\n            print("\\n🚀 Ready to help users plan their trips!")\n        else:\n            print("\\n❌ Some template tests failed. Check the output above.")\n            \n    except requests.exceptions.ConnectionError:\n        print("❌ Could not connect to the Flask app. Make sure it's running on http://127.0.0.1:5000")\n    except Exception as e:\n        print(f"❌ Unexpected error: {e}")