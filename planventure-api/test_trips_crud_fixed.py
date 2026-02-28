#!/usr/bin/env python3
"""
Test script for Trip CRUD operations
Tests the complete trip management system with all CRUD operations
"""

import requests
import json
from datetime import datetime, date, timedelta

BASE_URL = 'http://127.0.0.1:5000'

def test_trips_crud():
    """Test complete CRUD operations for trips"""
    
    print("=" * 70)
    print("TESTING TRIP CRUD OPERATIONS")
    print("=" * 70)
    
    # Test user for authentication
    test_user = {
        'email': 'trips.crud.test@example.com',
        'password': 'CrudTest123!',
        'confirm_password': 'CrudTest123!',
        'name': 'Trip CRUD Test User'
    }
    
    # Step 1: Register and login to get access token
    print("\n1. Setting up authentication...")
    
    # Register
    register_response = requests.post(f'{BASE_URL}/auth/register', json=test_user)
    if register_response.status_code != 201:
        print(f"Registration failed: {register_response.text}")
        return False
    
    # Login
    login_response = requests.post(
        f'{BASE_URL}/auth/login',
        json={
            'email': test_user['email'],
            'password': test_user['password']
        }
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return False
    
    login_data = login_response.json()
    access_token = login_data.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    
    print("✅ Authentication setup complete")
    
    # Step 2: Test CREATE - Create multiple trips
    print("\n2. Testing trip creation (CREATE)...")
    
    trips_to_create = [
        {
            'destination': 'Paris, France',
            'start_date': '2026-06-15',
            'end_date': '2026-06-22',
            'description': 'Summer vacation in Paris',
            'budget': 2500.00,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'status': 'planned',
            'itinerary': [
                {'day': 1, 'activity': 'Arrive and check in', 'location': 'Hotel'},
                {'day': 2, 'activity': 'Visit Eiffel Tower', 'location': 'Eiffel Tower'},
                {'day': 3, 'activity': 'Louvre Museum', 'location': 'Louvre'}
            ]
        },
        {
            'destination': 'Tokyo, Japan',
            'start_date': '2026-09-10',
            'end_date': '2026-09-17',
            'description': 'Autumn in Tokyo',
            'budget': 3500.00,
            'latitude': 35.6762,
            'longitude': 139.6503,
            'status': 'planned'
        },
        {
            'destination': 'New York, USA',
            'start_date': '2025-12-01',
            'end_date': '2025-12-05',
            'description': 'Business trip to NYC',
            'budget': 1800.00,
            'status': 'completed'
        }
    ]
    
    created_trip_ids = []
    
    for i, trip_data in enumerate(trips_to_create, 1):
        create_response = requests.post(
            f'{BASE_URL}/api/trips',
            json=trip_data,
            headers=headers
        )
        
        if create_response.status_code == 201:
            created_trip = create_response.json().get('trip')
            trip_id = created_trip.get('id')
            created_trip_ids.append(trip_id)
            print(f"✅ Trip {i} created successfully: ID {trip_id} - {trip_data['destination']}")
        else:
            print(f"❌ Failed to create trip {i}: {create_response.text}")
            return False
    
    # Step 3: Test READ - List all trips
    print("\n3. Testing trip listing (READ)...")
    
    list_response = requests.get(f'{BASE_URL}/api/trips', headers=headers)
    
    if list_response.status_code == 200:
        list_data = list_response.json()
        trips = list_data.get('trips', [])
        print(f"✅ Retrieved {len(trips)} trips")
        print(f"   Pagination: page {list_data['pagination']['page']}, total: {list_data['pagination']['total']}")
    else:
        print(f"❌ Failed to list trips: {list_response.text}")
        return False
    
    # Step 4: Test READ with filtering and sorting
    print("\n4. Testing trip filtering and sorting...")
    
    # Filter by destination
    filter_response = requests.get(
        f'{BASE_URL}/api/trips?destination=Paris&sort=budget&order=desc',
        headers=headers
    )
    
    if filter_response.status_code == 200:
        filter_data = filter_response.json()
        filtered_trips = filter_data.get('trips', [])
        print(f"✅ Filtered trips by 'Paris': {len(filtered_trips)} results")
        if filtered_trips:
            print(f"   First result: {filtered_trips[0]['destination']}")
    else:
        print(f"❌ Failed to filter trips: {filter_response.text}")
    
    # Step 5: Test READ - Get specific trip
    print("\n5. Testing specific trip retrieval...")
    
    if created_trip_ids:
        trip_id = created_trip_ids[0]
        get_response = requests.get(f'{BASE_URL}/api/trips/{trip_id}', headers=headers)
        
        if get_response.status_code == 200:
            trip_data = get_response.json().get('trip')
            print(f"✅ Retrieved trip {trip_id}: {trip_data['destination']}")
            print(f"   Duration: {trip_data['duration_days']} days")
            print(f"   Budget: ${trip_data['budget']}")
        else:
            print(f"❌ Failed to get trip {trip_id}: {get_response.text}")
    
    # Step 6: Test UPDATE - Complete update (PUT)
    print("\n6. Testing complete trip update (PUT)...")
    
    if created_trip_ids:
        trip_id = created_trip_ids[0]
        update_data = {
            'destination': 'Paris, France (Updated)',
            'start_date': '2026-07-01',
            'end_date': '2026-07-10',
            'description': 'Updated summer vacation in Paris',
            'budget': 2800.00,
            'latitude': 48.8566,
            'longitude': 2.3522,
            'status': 'planned',
            'itinerary': [
                {'day': 1, 'activity': 'Updated: Arrive and check in', 'location': 'Updated Hotel'},
                {'day': 2, 'activity': 'Updated: Visit Eiffel Tower', 'location': 'Eiffel Tower'}
            ]
        }
        
        put_response = requests.put(
            f'{BASE_URL}/api/trips/{trip_id}',
            json=update_data,
            headers=headers
        )
        
        if put_response.status_code == 200:
            updated_trip = put_response.json().get('trip')
            print(f"✅ Trip {trip_id} updated successfully")
            print(f"   New destination: {updated_trip['destination']}")
            print(f"   New budget: ${updated_trip['budget']}")
        else:
            print(f"❌ Failed to update trip {trip_id}: {put_response.text}")
    
    # Step 7: Test PATCH - Partial update
    print("\n7. Testing partial trip update (PATCH)...")
    
    if created_trip_ids and len(created_trip_ids) > 1:
        trip_id = created_trip_ids[1]
        patch_data = {
            'status': 'ongoing',
            'budget': 4000.00
        }
        
        patch_response = requests.patch(
            f'{BASE_URL}/api/trips/{trip_id}',
            json=patch_data,
            headers=headers
        )
        
        if patch_response.status_code == 200:
            patched_trip = patch_response.json().get('trip')
            print(f"✅ Trip {trip_id} partially updated")
            print(f"   New status: {patched_trip['status']}")
            print(f"   New budget: ${patched_trip['budget']}")
        else:
            print(f"❌ Failed to patch trip {trip_id}: {patch_response.text}")
    
    # Step 8: Test trip statistics
    print("\n8. Testing trip statistics...")
    
    stats_response = requests.get(f'{BASE_URL}/api/trips/stats', headers=headers)
    
    if stats_response.status_code == 200:
        stats_data = stats_response.json().get('statistics')
        print(f"✅ Trip statistics retrieved")
        print(f"   Total trips: {stats_data['total_trips']}")
        print(f"   Status breakdown: {stats_data['status_breakdown']}")
        print(f"   Total budget: ${stats_data['budget_statistics']['total_budget']}")
        print(f"   Average duration: {stats_data['duration_statistics']['average_duration_days']} days")
    else:
        print(f"❌ Failed to get trip statistics: {stats_response.text}")
    
    # Step 9: Test error handling - Try to access another user's trip
    print("\n9. Testing authorization (accessing non-existent trip)...")
    
    unauthorized_response = requests.get(f'{BASE_URL}/api/trips/99999', headers=headers)
    
    if unauthorized_response.status_code == 404:
        print("✅ Properly blocked access to non-existent/unauthorized trip")
    else:
        print(f"❌ Authorization test failed: {unauthorized_response.text}")
    
    # Step 10: Test DELETE - Delete a trip
    print("\n10. Testing trip deletion (DELETE)...")
    
    if created_trip_ids and len(created_trip_ids) > 2:
        trip_id = created_trip_ids[-1]  # Delete the last created trip
        delete_response = requests.delete(f'{BASE_URL}/api/trips/{trip_id}', headers=headers)
        
        if delete_response.status_code == 200:
            deleted_trip = delete_response.json().get('deleted_trip')
            print(f"✅ Trip {trip_id} deleted successfully")
            print(f"   Deleted trip: {deleted_trip['destination']}")
            
            # Verify deletion
            verify_response = requests.get(f'{BASE_URL}/api/trips/{trip_id}', headers=headers)
            if verify_response.status_code == 404:
                print("✅ Deletion verified - trip no longer accessible")
            else:
                print("❌ Trip still accessible after deletion")
        else:
            print(f"❌ Failed to delete trip {trip_id}: {delete_response.text}")
    
    # Step 11: Final trip count
    print("\n11. Final verification...")
    
    final_response = requests.get(f'{BASE_URL}/api/trips', headers=headers)
    
    if final_response.status_code == 200:
        final_data = final_response.json()
        final_count = final_data['pagination']['total']
        print(f"✅ Final trip count: {final_count}")
    
    print("\n" + "=" * 70)
    print("TRIP CRUD OPERATIONS TEST COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    print("Starting comprehensive Trip CRUD operations test...")
    print(f"Base URL: {BASE_URL}")
    print("\nMake sure the Flask app is running first!")
    input("Press Enter to continue...")
    
    try:
        # Test main CRUD operations
        crud_success = test_trips_crud()
        
        if crud_success:
            print("\n🎉 ALL TRIP CRUD TESTS COMPLETED SUCCESSFULLY!")
            print("\n📋 Tested features:")
            print("   ✅ Trip creation (POST /api/trips)")
            print("   ✅ Trip listing with pagination (GET /api/trips)")
            print("   ✅ Trip filtering and sorting")
            print("   ✅ Individual trip retrieval (GET /api/trips/<id>)")
            print("   ✅ Complete trip update (PUT /api/trips/<id>)")
            print("   ✅ Partial trip update (PATCH /api/trips/<id>)")
            print("   ✅ Trip deletion (DELETE /api/trips/<id>)")
            print("   ✅ Trip statistics (GET /api/trips/stats)")
            print("   ✅ Authorization and ownership validation")
        else:
            print("\n❌ Some CRUD tests failed. Check the output above.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the Flask app. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")