# PlanVenture API Authentication Middleware

Complete authentication system with JWT tokens, route protection, and user management.

## 🚀 Quick Start

1. **Start the server:**
   ```bash
   python run_server.py
   ```

2. **Test the system:**
   ```bash
   python test_middleware_integration.py
   ```

## 🔐 Authentication Flow

### 1. User Registration
```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "name": "John Doe"
  }'
```

### 2. User Login
```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com", 
    "password": "SecurePassword123"
  }'
```

Response includes `access_token` and `refresh_token`.

### 3. Using Protected Routes
Include the token in the Authorization header:
```bash
curl -X GET http://127.0.0.1:5000/api/user/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛡️ Route Protection

### Decorators Available

#### `@require_auth`
- **Purpose**: Requires valid JWT token
- **Behavior**: Returns 401 if no token or invalid token
- **User Context**: Automatically sets `g.current_user` and `g.current_user_id`

```python
@app.route('/api/user/profile')
@require_auth
def get_user_profile():
    user = get_current_user()  # Helper function
    return jsonify({'user': user.to_dict()})
```

#### `@optional_auth` 
- **Purpose**: Authentication is optional
- **Behavior**: Sets `g.is_authenticated` (True/False)
- **User Context**: Only sets user context if valid token provided

```python
@app.route('/auth/profile')
@optional_auth
def get_profile():
    if g.is_authenticated:
        user = get_current_user()
        return jsonify({'user': user.to_dict()})
    return jsonify({'message': 'Not authenticated'})
```

#### `@admin_required`
- **Purpose**: Requires admin user (is_admin=True)
- **Behavior**: Returns 401 if not authenticated, 403 if not admin
- **User Context**: Same as `@require_auth` plus admin check

```python
@app.route('/api/admin/users')
@admin_required
def admin_panel():
    return jsonify({'admin_data': 'sensitive_info'})
```

## 📋 Available Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | User registration |
| POST | `/auth/login` | None | User login |
| GET | `/auth/validate-email` | None | Email validation |
| GET | `/auth/profile` | Optional | Profile with optional auth |

### Protected API
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/user/profile` | Required | Get user profile |
| GET | `/api/user/trips` | Required | Get user's trips |
| POST | `/api/trips` | Required | Create new trip |

## 🔧 Helper Functions

The middleware provides several helper functions:

### `get_current_user()`
```python
@require_auth
def some_route():
    user = get_current_user()  # Returns User object
    return jsonify({'name': user.name})
```

### `get_current_user_id()`
```python
@require_auth  
def some_route():
    user_id = get_current_user_id()  # Returns user ID integer
    return jsonify({'user_id': user_id})
```

### `is_authenticated()`
```python
@optional_auth
def some_route():
    if is_authenticated():  # Returns boolean
        return jsonify({'status': 'authenticated'})
    return jsonify({'status': 'guests'})
```

## 🛡️ Security Features

### Automatic Security Headers
The middleware automatically adds:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY` 
- `X-XSS-Protection: 1; mode=block`

### Route Patterns
- **Public routes**: `/`, `/auth/*`, `/health`, `/docs`
- **Protected routes**: All others require authentication

### Token Validation
- Automatic JWT validation on every request
- Proper error responses (401 Unauthorized, 403 Forbidden)
- User context automatically loaded

## 📊 Example Trip Management

### Create a Trip
```bash
curl -X POST http://127.0.0.1:5000/api/trips \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "start_date": "2024-06-01", 
    "end_date": "2024-06-07",
    "description": "Cherry blossom season",
    "budget": 3000.00,
    "latitude": 35.6762,
    "longitude": 139.6503,
    "itinerary": [
      {"day": 1, "activity": "Arrive in Tokyo", "location": "Narita Airport"},
      {"day": 2, "activity": "Visit Senso-ji Temple", "location": "Asakusa"}
    ]
  }'
```

### Get User Trips
```bash
curl -X GET http://127.0.0.1:5000/api/user/trips \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔄 Integration in Your Routes

### Basic Protected Route
```python
from auth_middleware import require_auth, get_current_user

@app.route('/api/my-route')
@require_auth
def my_protected_route():
    user = get_current_user()
    return jsonify({
        'message': f'Hello {user.name}!',
        'user_id': user.id
    })
```

### Optional Authentication
```python
from auth_middleware import optional_auth, is_authenticated, get_current_user

@app.route('/api/optional-route')
@optional_auth  
def my_optional_route():
    if is_authenticated():
        user = get_current_user()
        return jsonify({'message': f'Welcome back, {user.name}!'})
    return jsonify({'message': 'Welcome, guest!'})
```

### Admin Only Route
```python
from auth_middleware import admin_required, get_current_user

@app.route('/api/admin/sensitive')
@admin_required
def admin_only():
    admin_user = get_current_user()
    return jsonify({
        'message': 'Admin access granted',
        'admin': admin_user.email
    })
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_middleware_integration.py
```

Tests include:
- User registration and login
- Protected route access (with/without tokens)
- Optional authentication routes  
- Trip creation and retrieval
- Invalid token handling
- Security headers verification

## ⚙️ Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database
DATABASE_URL=sqlite:///instance/planventure.db
```

### Middleware Initialization
```python
from auth_middleware import AuthMiddleware

app = Flask(__name__)
# ... configure app ...

# Initialize auth middleware
auth_middleware = AuthMiddleware(app)
```

The middleware is now fully integrated and ready to protect your routes! 🎉

## 🚨 Error Handling

### Common Response Codes
- **200**: Success
- **201**: Created (registration, trip creation)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (invalid/missing token)
- **403**: Forbidden (admin required, not admin)
- **500**: Internal Server Error

### Example Error Response
```json
{
  "error": "Authentication required",
  "message": "Valid JWT token must be provided"
}
```