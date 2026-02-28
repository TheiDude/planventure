# GitHub Copilot Instructions - PlanVenture API

This document provides context and instructions for GitHub Copilot when working on the PlanVenture API project.

## 📋 Project Overview

PlanVenture is a travel planning API built with Flask that provides user authentication and comprehensive trip management functionality. The API follows RESTful principles with JWT-based authentication and complete CRUD operations for trip planning.

## 🛠️ Tech Stack

### Backend Framework
- **Flask 2.3.3** - Core web framework
- **Flask-SQLAlchemy 3.1.1** - ORM for database operations
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing support
- **Werkzeug 2.3.7** - WSGI utilities and password hashing

### Authentication & Security
- **PyJWT 2.8.0** - JWT token generation and validation
- **pbkdf2:sha256** - Password hashing with scrypt fallback
- **Custom Auth Middleware** - Route protection and user context management

### Database
- **SQLite** - Development database
- **SQLAlchemy ORM** - Database abstraction layer

### Development Tools
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for testing

## 📁 Project Structure

```
planventure-api/
├── app.py                          # Main Flask application
├── models.py                       # Database models (User, Trip)
├── auth_routes.py                  # Authentication endpoints
├── trip_routes.py                  # Trip CRUD endpoints
├── auth_middleware.py              # Route protection middleware
├── jwt_utils.py                    # JWT token utilities
├── run_server.py                   # Server startup script
├── requirements.txt                # Python dependencies
├── test_middleware_integration.py  # Auth system tests
├── test_trips_crud_fixed.py       # Trip CRUD tests
├── api_status.py                   # API status overview
├── AUTH_MIDDLEWARE_DOCS.md         # Auth documentation
├── TRIP_CRUD_API.md               # Trip API documentation
└── instance/
    └── planventure.db             # SQLite database file
```

## 🚀 Start/Stop Instructions

### Start Development Server
```bash
# Navigate to project directory
cd planventure-api

# Activate virtual environment (if not already active)
source ../venv/bin/activate  # or ../venv-1/bin/activate

# Start server with full initialization
python run_server.py

# Alternative: Direct Flask app start
python app.py
```

### Stop Server
```bash
# Ctrl+C in terminal, or kill by port:
lsof -ti:5000 | xargs kill -9
```

### Database Initialization
```bash
# Initialize database tables
python init_db.py

# Or via Flask shell:
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 🔌 API Routes

### Authentication Endpoints
```
POST   /auth/register              # User registration with validation
POST   /auth/login                 # User login with JWT token generation
GET    /auth/profile               # Profile access (optional auth)
POST   /auth/validate-email        # Email validation utility
```

### Trip Management (CRUD)
```
GET    /api/trips                  # List trips (pagination, filtering, sorting)
POST   /api/trips                  # Create new trip
GET    /api/trips/<id>             # Get specific trip by ID
PUT    /api/trips/<id>             # Update entire trip (replace all fields)
PATCH  /api/trips/<id>             # Partial trip update (specific fields)
DELETE /api/trips/<id>             # Delete trip by ID
GET    /api/trips/stats            # Trip statistics and analytics
```

### Itinerary Template System
```
GET    /api/trips/itinerary-template              # Public template generation (no auth)
POST   /api/trips/<id>/generate-itinerary         # Generate itinerary for existing trip (auth required)
```

### User Management
```
GET    /api/user/profile           # Protected user profile endpoint
```

### Health & Monitoring Endpoints
```
GET    /health                     # Comprehensive health check with detailed metrics
GET    /status                     # Simple status check for load balancers 
GET    /ready                      # Readiness probe for Kubernetes
GET    /live                       # Liveness probe for Kubernetes
```

### System Endpoints
```
GET    /                           # Welcome message
```

## 🗃️ Database Models

### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
```

### Trip Model
```python
class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    budget = db.Column(db.Float)
    status = db.Column(db.String(20), default='planned')  # planned, ongoing, completed, cancelled
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    itinerary_json = db.Column(db.Text)  # JSON string for flexible itinerary storage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Enhanced methods for itinerary template generation
    def generate_default_itinerary_template(self, trip_type='general'):
        """Generate smart itinerary template based on trip duration and type"""
    
    def get_itinerary_suggestions_by_type(self, trip_type):
        """Get activity suggestions based on trip type"""
        
    def set_itinerary(self, itinerary_data):
        """Set itinerary with validation"""
```

## 🎯 Advanced Features

### Itinerary Template System

The API provides intelligent itinerary generation with 6 different trip types:

**Trip Types & Activity Suggestions:**
- **Cultural**: Art galleries, museums, festivals, traditional craft workshops, local cooking classes
- **Adventure**: Hiking, water sports, mountain biking, rock climbing, wildlife watching  
- **Business**: Business meetings, conferences, networking events, coworking spaces
- **Relaxation**: Spa activities, beach time, wellness activities, scenic drives
- **Family**: Family parks, kid-friendly attractions, educational tours, interactive museums
- **General**: Popular attractions, local experiences, shopping, dining, sightseeing

**Template Generation Features:**
- **Duration-based structure**: Intelligent daily activity planning
- **Smart day progression**: Arrival → Activities → Departure
- **Customizable framework**: Flexible templates for personalization
- **Public access**: No authentication required for basic templates
- **User-specific generation**: Authenticated users can generate for existing trips

```python
# Public template generation (no auth required)
@trips_bp.route('/itinerary-template', methods=['GET'])
def get_itinerary_template():
    duration = request.args.get('duration', type=int)
    destination = request.args.get('destination')
    trip_type = request.args.get('trip_type', 'general')
    
    # Generate template logic...

# Authenticated trip enhancement 
@trips_bp.route('/<int:trip_id>/generate-itinerary', methods=['POST'])
@require_auth
def generate_trip_itinerary(trip_id):
    # Generate and save to existing trip...
```

### Enhanced Health Monitoring

**Four-tier health check system for different monitoring needs:**

1. **`/health`** - Comprehensive diagnostics (5-15ms)
   - Database connectivity with response times
   - Auth middleware status
   - CORS configuration validation
   - Application uptime tracking
   - Component-level health reporting

2. **`/status`** - Simple availability check (~2ms)
   - Lightweight "ping" for load balancers
   - Always returns 200 with timestamp
   - Minimal overhead for frequent checks

3. **`/ready`** - Kubernetes readiness probe (~3ms)
   - Database dependency validation
   - Returns 200 when ready for traffic
   - Returns 503 when not ready

4. **`/live`** - Kubernetes liveness probe (~2ms)  
   - Basic application responsiveness
   - Always returns 200 unless completely dead
   - Used for container restart decisions

```python
# Health check with comprehensive diagnostics
@app.route('/health')
def health_check():
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - app.start_time),
        "version": "1.0.0",
        "checks": {
            "database": {"status": "healthy", "response_time_ms": 2.45},
            "auth_middleware": {"status": "healthy"},
            "cors": {"status": "healthy", "origins_count": 6}
        }
    }
```

### CORS Configuration for React Integration

**Complete frontend integration support:**

```python
# Enhanced CORS setup for multiple React environments
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
CORS(app, 
     origins=cors_origins,
     methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     supports_credentials=True,
     expose_headers=['Authorization']
)
```

**Supported React Development Environments:**
- **Create React App**: localhost:3000, 127.0.0.1:3000
- **Alternative CRA ports**: localhost:3001, 127.0.0.1:3001  
- **Vite**: localhost:5173, 127.0.0.1:5173
- **Custom ports**: Configurable via CORS_ORIGINS environment variable

### Advanced Trip Management Features

**Filtering & Pagination:**
```bash
# Advanced trip filtering examples
/api/trips?destination=Paris&status=planned&sort=budget&order=desc&page=1&per_page=10
/api/trips?start_date_after=2026-06-01&budget_min=1000&budget_max=5000
/api/trips?search=europe&sort=created_at&order=asc
```

**Trip Statistics:**
```bash
# Get user trip analytics
GET /api/trips/stats
{
  "total_trips": 15,
  "trips_by_status": {"planned": 5, "completed": 8, "ongoing": 2},
  "total_budget": 45000.0,
  "average_budget": 3000.0,
  "destinations_visited": ["Paris", "Tokyo", "New York"],
  "trip_duration_stats": {"min": 3, "max": 14, "average": 7.2}
}
```

## 🔐 Authentication Patterns

### Route Protection
```python
# Require authentication
@require_auth
def protected_endpoint():
    user = get_current_user()  # Get authenticated user
    return jsonify({'user_id': user.id})

# Optional authentication
@optional_auth
def optional_endpoint():
    if g.is_authenticated:
        user = get_current_user()
        return jsonify({'authenticated': True, 'user': user.to_dict()})
    return jsonify({'authenticated': False})

# Admin required
@admin_required
def admin_endpoint():
    user = get_current_user()  # Guaranteed to be admin
    return jsonify({'admin_access': True})
```

### JWT Token Usage
```python
# Generate tokens (in auth_routes.py)
access_token, refresh_token = user.generate_tokens()

# Validate tokens (in auth_middleware.py)
user_id = validate_token(token)
```

## 📝 Development Best Practices

### Code Organization
- **Blueprints**: Use Flask blueprints for route organization (`auth_bp`, `trips_bp`)
- **Models**: Keep database models in separate `models.py` file
- **Middleware**: Centralized authentication in `auth_middleware.py`
- **Utilities**: JWT functions in dedicated `jwt_utils.py`

### Authentication
- Always use `@require_auth` decorator for protected endpoints
- Use `@optional_auth` for endpoints that work with or without auth
- Access current user via `get_current_user()` helper function
- Check user ownership for resource access: `Trip.query.filter_by(id=trip_id, user_id=user_id)`

### Database Operations
```python
# Always use try/except with rollback
try:
    db.session.add(object)
    db.session.commit()
    return jsonify({'success': True}), 201
except Exception as e:
    db.session.rollback()
    return jsonify({'error': 'Database error'}), 500
```

### Input Validation
```python
# Validate required fields
required_fields = ['destination', 'start_date', 'end_date']
for field in required_fields:
    if field not in data or not data[field]:
        return jsonify({'error': f'{field} is required'}), 400

# Validate data types and ranges
try:
    budget = float(data['budget'])
    if budget < 0:
        raise ValueError("Budget must be positive")
except (ValueError, TypeError):
    return jsonify({'error': 'Invalid budget'}), 400
```

### Response Format
```python
# Success responses
return jsonify({
    'message': 'Operation successful',
    'data': result_data
}), 200

# Error responses
return jsonify({
    'error': 'Error category',
    'message': 'Detailed error message'
}), status_code
```

## 🧪 Testing Patterns

### Authentication Tests
```python
# Test user registration and login
test_user = {
    'email': 'test@example.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'name': 'Test User'
}

# Get access token
login_response = requests.post(f'{BASE_URL}/auth/login', json=credentials)
access_token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}
```

### CRUD Operation Tests
```python
# Create resource
create_response = requests.post(f'{BASE_URL}/api/trips', json=trip_data, headers=headers)

# Read resource
get_response = requests.get(f'{BASE_URL}/api/trips/{trip_id}', headers=headers)

# Update resource (PUT for complete, PATCH for partial)
update_response = requests.put(f'{BASE_URL}/api/trips/{trip_id}', json=update_data, headers=headers)

# Delete resource
delete_response = requests.delete(f'{BASE_URL}/api/trips/{trip_id}', headers=headers)
```

## 🔄 Common Development Tasks

### Adding New Protected Route
```python
@app.route('/api/new-endpoint')
@require_auth
def new_endpoint():
    user = get_current_user()
    # Implementation here
    return jsonify({'result': data})
```

### Adding Trip Filtering
```python
# In trip_routes.py, add to list_trips() function
status = request.args.get('status')
if status:
    query = query.filter(Trip.status == status)
```

### Database Migration Pattern
```python
# For schema changes, always backup and test
with app.app_context():
    # Add new columns
    db.engine.execute('ALTER TABLE trip ADD COLUMN new_field TEXT')
    db.session.commit()
```

## 🌍 Environment Variables

```bash
# Required environment variables
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-change-in-production
DATABASE_URL=sqlite:///instance/planventure.db

# CORS Configuration for React Frontend Development
# Include common React development ports and both localhost/127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173

# Optional
FLASK_ENV=development
FLASK_DEBUG=True
API_HOST=127.0.0.1
API_PORT=5000
```

## 🧪 Comprehensive Testing Suite

The project includes extensive test coverage across all major components:

### Test Scripts Overview

1. **`test_middleware_integration.py`** - Authentication system testing
   - User registration and login flows
   - JWT token generation and validation
   - Protected route access patterns
   - Middleware functionality verification

2. **`test_trips_crud_fixed.py`** - Trip management testing
   - Complete CRUD operations (Create, Read, Update, Delete)
   - Advanced filtering and pagination
   - User ownership validation
   - Error handling and edge cases

3. **`test_itinerary_simple.py`** - Itinerary template testing
   - Public template generation (no auth required)
   - Authenticated template generation for existing trips
   - Multiple trip type testing (cultural, adventure, business, etc.)
   - Duration-based template structure validation

4. **`test_cors_config.py`** - React integration testing
   - CORS preflight request handling
   - Multiple React development port support
   - Authentication flow with CORS headers
   - Credentials handling for JWT tokens

5. **`test_health_endpoints.py`** - Health monitoring testing
   - All four health endpoint types (/health, /status, /ready, /live)
   - Performance benchmarking and response times
   - Component-level health diagnostics
   - Error scenario handling

### Running the Complete Test Suite

```bash
cd planventure-api

# Run all tests sequentially
python3 test_middleware_integration.py    # Auth system
python3 test_trips_crud_fixed.py         # Trip CRUD  
python3 test_itinerary_simple.py         # Itinerary templates
python3 test_cors_config.py               # CORS integration
python3 test_health_endpoints.py          # Health monitoring

# Quick test verification
curl http://127.0.0.1:5000/health | python3 -m json.tool
```

### Test Coverage Areas

- ✅ **Authentication Flow**: Registration, login, token management, protected routes
- ✅ **Trip Operations**: Full CRUD with filtering, pagination, sorting, statistics
- ✅ **Itinerary Generation**: Public templates, authenticated generation, 6 trip types
- ✅ **React Integration**: CORS preflight, multiple ports, credentials, headers
- ✅ **Health Monitoring**: All endpoint types, performance, error scenarios
- ✅ **Error Handling**: Validation, authentication, database, network errors
- ✅ **Security Features**: User ownership, input validation, JWT security

## 📊 API Usage Examples

### Complete User Flow
```bash
# 1. Register user
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123!","confirm_password":"Pass123!","name":"User"}'

# 2. Login and get token
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Pass123!"}'

# 3. Create trip
curl -X POST http://127.0.0.1:5000/api/trips \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"destination":"Paris","start_date":"2026-06-15","end_date":"2026-06-22"}'

# 4. List trips with filtering
curl -X GET "http://127.0.0.1:5000/api/trips?destination=Paris&sort=budget&order=desc" \
  -H "Authorization: Bearer TOKEN"
```

### Itinerary Template Examples
```bash
# 1. Generate public template (no authentication required)
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=7&destination=Tokyo&trip_type=cultural"

# 2. Generate template for different trip types
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=5&trip_type=adventure"
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=3&trip_type=business"
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=10&trip_type=relaxation"

# 3. Generate itinerary for existing trip (requires authentication)
curl -X POST http://127.0.0.1:5000/api/trips/123/generate-itinerary \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"trip_type": "family"}'
```

### Health Monitoring Examples
```bash
# Comprehensive health check with detailed metrics
curl http://127.0.0.1:5000/health | python3 -m json.tool

# Simple status check for load balancers
curl http://127.0.0.1:5000/status

# Kubernetes readiness probe
curl http://127.0.0.1:5000/ready

# Kubernetes liveness probe  
curl http://127.0.0.1:5000/live
```

### Advanced Trip Filtering Examples
```bash
# Filter by multiple criteria with pagination
curl -H "Authorization: Bearer TOKEN" \
  "http://127.0.0.1:5000/api/trips?status=planned&budget_min=1000&budget_max=5000&page=1&per_page=10"

# Search trips with sorting
curl -H "Authorization: Bearer TOKEN" \
  "http://127.0.0.1:5000/api/trips?search=europe&sort=start_date&order=asc"

# Get trip statistics
curl -H "Authorization: Bearer TOKEN" \
  "http://127.0.0.1:5000/api/trips/stats"
```

### React Integration Examples
```bash
# Test CORS preflight for React app
curl -X OPTIONS -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  http://127.0.0.1:5000/auth/login -v

# Test authenticated request with CORS headers
curl -X GET http://127.0.0.1:5000/api/user/profile \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

## ⚠️ Security Considerations

- **Never** commit secrets to version control
- **Always** validate user ownership before allowing resource access
- **Use** HTTPS in production
- **Implement** rate limiting for authentication endpoints
- **Validate** and sanitize all user input
- **Use** parameterized queries (SQLAlchemy handles this)

## 🐛 Common Issues & Solutions

### Port Already in Use
```bash
lsof -ti:5000 | xargs kill -9
```

### Database Connection Issues
```python
# Check database file permissions and path
ls -la instance/planventure.db

# Reinitialize if needed
python init_db.py
```

### JWT Token Issues
```python
# Check token expiration and format
# Ensure JWT_SECRET_KEY is consistent
# Verify Authorization header format: "Bearer TOKEN"
```

## 📚 Documentation Files

- `README.md` - Comprehensive project guide with all features and setup instructions
- `REACT_INTEGRATION_GUIDE.md` - Complete React frontend integration documentation
- `HEALTH_ENDPOINTS.md` - Health monitoring system documentation with examples
- `AUTH_MIDDLEWARE_DOCS.md` - Complete authentication system documentation
- `TRIP_CRUD_API.md` - Trip management API reference
- `test_middleware_integration.py` - Authentication flow examples and testing
- `test_trips_crud_fixed.py` - Trip CRUD operation examples and testing
- `test_itinerary_simple.py` - Itinerary template generation testing
- `test_cors_config.py` - CORS configuration and React integration testing
- `test_health_endpoints.py` - Health monitoring endpoints testing

## 🎯 Project Goals & Architecture

This API is designed to be:
- **Secure**: JWT authentication with proper authorization
- **Scalable**: Modular blueprint architecture
- **Testable**: Comprehensive test coverage
- **Maintainable**: Clear separation of concerns
- **RESTful**: Following REST API conventions
- **Documented**: Extensive documentation and examples

When extending this API, maintain these principles and follow the established patterns for consistency and maintainability.