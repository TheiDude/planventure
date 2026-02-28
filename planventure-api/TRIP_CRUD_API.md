# Trip CRUD API Documentation

Complete CRUD operations for trip management in PlanVenture API.

## 🚀 Quick Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/trips` | List user's trips with filtering | Yes |
| POST | `/api/trips` | Create new trip | Yes |
| GET | `/api/trips/<id>` | Get specific trip | Yes |
| PUT | `/api/trips/<id>` | Update entire trip | Yes |
| PATCH | `/api/trips/<id>` | Partial trip update | Yes |
| DELETE | `/api/trips/<id>` | Delete trip | Yes |
| GET | `/api/trips/stats` | Get trip statistics | Yes |

## 🛡️ Authentication

All trip endpoints require authentication via JWT token:
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

Users can only access, modify, and delete their own trips. Attempting to access another user's trips returns 404.

## 📝 Trip Data Model

```json
{
  "id": 1,
  "user_id": 14,
  "destination": "Paris, France",
  "start_date": "2026-06-15",
  "end_date": "2026-06-22",
  "description": "Summer vacation in Paris",
  "budget": 2500.00,
  "status": "planned",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "duration_days": 8,
  "itinerary": [
    {
      "day": 1,
      "activity": "Arrive and check in",
      "location": "Hotel"
    },
    {
      "day": 2,
      "activity": "Visit Eiffel Tower", 
      "location": "Eiffel Tower"
    }
  ],
  "created_at": "2026-02-28T22:03:49.283292",
  "updated_at": "2026-02-28T22:03:49.283293"
}
```

### Field Descriptions

- `id` (int): Unique trip identifier
- `user_id` (int): Owner's user ID
- `destination` (string): Trip destination
- `start_date` (string): Trip start date (YYYY-MM-DD)
- `end_date` (string): Trip end date (YYYY-MM-DD)
- `description` (string, optional): Trip description
- `budget` (float, optional): Trip budget
- `status` (string): Trip status (`planned`, `ongoing`, `completed`, `cancelled`)
- `latitude` (float, optional): Destination latitude (-90 to 90)
- `longitude` (float, optional): Destination longitude (-180 to 180)
- `duration_days` (int): Calculated trip duration in days
- `itinerary` (array, optional): List of itinerary items
- `created_at` (string): Creation timestamp
- `updated_at` (string): Last update timestamp

## 📋 API Endpoints

### 1. List Trips
**GET** `/api/trips`

Retrieve all trips for the authenticated user with optional filtering, sorting, and pagination.

#### Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | int | Page number | 1 |
| `per_page` | int | Items per page (max 100) | 10 |
| `destination` | string | Filter by destination (partial match) | - |
| `status` | string | Filter by status | - |
| `start_date_from` | string | Filter trips starting from date (YYYY-MM-DD) | - |
| `start_date_to` | string | Filter trips starting before date (YYYY-MM-DD) | - |
| `budget_min` | float | Minimum budget filter | - |
| `budget_max` | float | Maximum budget filter | - |
| `sort` | string | Sort field (`destination`, `start_date`, `end_date`, `budget`, `created_at`) | `created_at` |
| `order` | string | Sort order (`asc`, `desc`) | `desc` |

#### Example Request
```bash
curl -X GET "http://127.0.0.1:5000/api/trips?destination=Paris&sort=budget&order=desc&page=1&per_page=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "message": "Trips retrieved successfully",
  "user_id": 14,
  "trips": [...],
  "pagination": {
    "page": 1,
    "per_page": 5,
    "total": 12,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "destination": "Paris",
    "status": null,
    "start_date_from": null,
    "start_date_to": null,
    "budget_min": null,
    "budget_max": null
  },
  "sorting": {
    "field": "budget",
    "order": "desc"
  }
}
```

### 2. Create Trip
**POST** `/api/trips`

Create a new trip for the authenticated user.

#### Required Fields
- `destination` (string): Trip destination
- `start_date` (string): Start date in YYYY-MM-DD format
- `end_date` (string): End date in YYYY-MM-DD format

#### Optional Fields
- `description` (string): Trip description
- `budget` (float): Trip budget (must be positive)
- `latitude` (float): Destination latitude (-90 to 90)
- `longitude` (float): Destination longitude (-180 to 180)
- `itinerary` (array): List of itinerary items
- `status` (string): Trip status (default: `planned`)

#### Example Request
```bash
curl -X POST "http://127.0.0.1:5000/api/trips" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "start_date": "2026-09-15",
    "end_date": "2026-09-22",
    "description": "Cherry blossom season",
    "budget": 3000.00,
    "latitude": 35.6762,
    "longitude": 139.6503,
    "status": "planned",
    "itinerary": [
      {
        "day": 1,
        "activity": "Arrive in Tokyo",
        "location": "Narita Airport"
      },
      {
        "day": 2,
        "activity": "Visit Senso-ji Temple",
        "location": "Asakusa"
      }
    ]
  }'
```

#### Example Response
```json
{
  "message": "Trip created successfully",
  "trip": {
    "id": 15,
    "user_id": 14,
    "destination": "Tokyo, Japan",
    "start_date": "2026-09-15",
    "end_date": "2026-09-22",
    "description": "Cherry blossom season",
    "budget": 3000.0,
    "status": "planned",
    "latitude": 35.6762,
    "longitude": 139.6503,
    "duration_days": 8,
    "itinerary": [...],
    "created_at": "2026-02-28T22:15:30.123456",
    "updated_at": "2026-02-28T22:15:30.123456"
  }
}
```

### 3. Get Specific Trip
**GET** `/api/trips/<id>`

Retrieve a specific trip by ID. Only the trip owner can access it.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:5000/api/trips/15" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "message": "Trip retrieved successfully",
  "trip": {
    "id": 15,
    "user_id": 14,
    "destination": "Tokyo, Japan",
    ...
  }
}
```

### 4. Update Trip (Complete)
**PUT** `/api/trips/<id>`

Replace all trip data with new values. All required fields must be provided.

#### Example Request
```bash
curl -X PUT "http://127.0.0.1:5000/api/trips/15" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Kyoto, Japan",
    "start_date": "2026-10-01",
    "end_date": "2026-10-08",
    "description": "Traditional Japan experience",
    "budget": 3500.00,
    "latitude": 35.0116,
    "longitude": 135.7681,
    "status": "planned"
  }'
```

### 5. Update Trip (Partial)
**PATCH** `/api/trips/<id>`

Update only the provided fields. All fields are optional.

#### Example Request
```bash
curl -X PATCH "http://127.0.0.1:5000/api/trips/15" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ongoing",
    "budget": 4000.00
  }'
```

### 6. Delete Trip
**DELETE** `/api/trips/<id>`

Delete a specific trip. Only the trip owner can delete it.

#### Example Request
```bash
curl -X DELETE "http://127.0.0.1:5000/api/trips/15" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "message": "Trip deleted successfully",
  "deleted_trip": {
    "id": 15,
    "destination": "Tokyo, Japan",
    ...
  }
}
```

### 7. Trip Statistics
**GET** `/api/trips/stats`

Get comprehensive statistics about the user's trips.

#### Example Request
```bash
curl -X GET "http://127.0.0.1:5000/api/trips/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "message": "Trip statistics retrieved successfully",
  "user_id": 14,
  "statistics": {
    "total_trips": 5,
    "status_breakdown": {
      "planned": 3,
      "ongoing": 1,
      "completed": 1,
      "cancelled": 0
    },
    "budget_statistics": {
      "total_budget": 12500.0,
      "average_budget": 2500.0,
      "min_budget": 1200.0,
      "max_budget": 4000.0
    },
    "duration_statistics": {
      "average_duration_days": 7.2
    },
    "timeline_breakdown": {
      "upcoming_trips": 3,
      "current_trips": 1,
      "past_trips": 1
    }
  }
}
```

## ❌ Error Responses

### Validation Errors (400)
```json
{
  "error": "Validation error",
  "message": "start_date is required"
}
```

### Authentication Required (401)
```json
{
  "error": "Authentication required",
  "message": "Please provide a valid access token"
}
```

### Trip Not Found (404)
```json
{
  "error": "Trip not found",
  "message": "Trip with ID 999 not found or you do not have permission to access it"
}
```

### Server Error (500)
```json
{
  "error": "Server error", 
  "message": "Failed to create trip"
}
```

## 🔍 Advanced Filtering Examples

### Filter by Date Range
```bash
# Get trips starting between June 1-30, 2026
curl -X GET "http://127.0.0.1:5000/api/trips?start_date_from=2026-06-01&start_date_to=2026-06-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Budget Range
```bash
# Get trips with budget between $1000-$3000
curl -X GET "http://127.0.0.1:5000/api/trips?budget_min=1000&budget_max=3000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status
```bash
# Get only planned trips
curl -X GET "http://127.0.0.1:5000/api/trips?status=planned" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Complex Filtering with Sorting
```bash
# Get completed trips to destinations containing "Japan", sorted by budget (high to low)
curl -X GET "http://127.0.0.1:5000/api/trips?destination=Japan&status=completed&sort=budget&order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Pagination
```bash
# Get page 2 with 20 trips per page
curl -X GET "http://127.0.0.1:5000/api/trips?page=2&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

Test the complete CRUD functionality:
```bash
python test_trips_crud.py
```

This test script validates:
- ✅ Trip creation with various data types
- ✅ Trip listing with pagination and filtering
- ✅ Individual trip retrieval
- ✅ Complete trip updates (PUT)
- ✅ Partial trip updates (PATCH)
- ✅ Trip deletion
- ✅ Trip statistics
- ✅ Authorization and ownership validation
- ✅ Input validation and error handling

## 📊 Status Values

Valid trip status values:
- `planned` - Trip is being planned (default)
- `ongoing` - Trip is currently happening
- `completed` - Trip has been completed
- `cancelled` - Trip has been cancelled

## 🎯 Tips for Usage

1. **Pagination**: Always use pagination for large trip lists to improve performance
2. **Filtering**: Combine multiple filters for precise results
3. **Sorting**: Use sorting to organize trips by relevance (date, budget, etc.)
4. **Validation**: All dates must be in YYYY-MM-DD format
5. **Authorization**: Users can only access their own trips
6. **Coordinates**: Latitude/longitude are optional but useful for mapping
7. **Itinerary**: Structure itinerary as array of objects for consistency
8. **Statistics**: Use stats endpoint for dashboards and analytics

The Trip CRUD API provides complete functionality for managing travel plans with proper validation, authentication, and error handling! 🚀✈️