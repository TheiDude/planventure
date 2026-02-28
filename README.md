# 🌍 PlanVenture API

A comprehensive travel planning API built with Flask that provides user authentication, trip management, and intelligent itinerary generation capabilities.

## 📋 Overview

PlanVenture API is a RESTful backend service designed to power travel planning applications. It offers secure user authentication, complete trip CRUD operations, intelligent itinerary template generation, and seamless React frontend integration through comprehensive CORS support.

### ✨ Key Features

- 🔐 **Secure Authentication** - JWT-based user authentication with middleware protection
- 🗂️ **Trip Management** - Full CRUD operations with advanced filtering and pagination
- 🎯 **Smart Itinerary Generation** - AI-powered template creation based on trip type and duration
- 🌐 **React Integration Ready** - Complete CORS configuration for frontend development
- 📊 **Health Monitoring** - Production-ready health checks and monitoring endpoints
- 🛡️ **Security First** - Comprehensive input validation and secure password handling
- 📖 **Developer Friendly** - Extensive documentation and testing utilities

## 🚀 Tech Stack

### Backend Framework
- **Flask 2.3.3** - Lightweight and flexible web framework
- **Flask-SQLAlchemy 3.1.1** - Database ORM and management
- **Flask-CORS 4.0.0** - Cross-origin resource sharing support
- **Werkzeug 2.3.7** - WSGI utilities and security features

### Authentication & Security
- **PyJWT 2.8.0** - JSON Web Token implementation
- **Custom Auth Middleware** - Route protection and user context
- **Password Hashing** - Secure pbkdf2:sha256 with scrypt fallback

### Database
- **SQLite** - Lightweight database for development
- **SQLAlchemy ORM** - Database abstraction and modeling

### Development Tools
- **python-dotenv** - Environment variable management
- **requests** - HTTP client for testing

## 🏗️ Project Structure

```
planventure/
├── README.md                          # This comprehensive guide
├── REACT_INTEGRATION_GUIDE.md         # React frontend integration docs
├── planventure-api/                   # Main API directory
│   ├── app.py                         # Flask application entry point
│   ├── models.py                      # Database models (User, Trip)
│   ├── auth_routes.py                 # Authentication endpoints
│   ├── trip_routes.py                 # Trip CRUD endpoints
│   ├── auth_middleware.py             # Authentication middleware
│   ├── jwt_utils.py                   # JWT token utilities
│   ├── requirements.txt               # Python dependencies
│   ├── .env                           # Environment configuration
│   ├── .sample.env                    # Environment template
│   ├── instance/                      # Database directory
│   │   └── planventure.db            # SQLite database file
│   ├── HEALTH_ENDPOINTS.md           # Health monitoring documentation
│   ├── AUTH_MIDDLEWARE_DOCS.md       # Authentication system docs
│   ├── TRIP_CRUD_API.md              # Trip management API docs
│   └── tests/                         # Test scripts
│       ├── test_middleware_integration.py
│       ├── test_trips_crud_fixed.py
│       ├── test_itinerary_simple.py
│       ├── test_cors_config.py
│       └── test_health_endpoints.py
```

## ⚡ Quick Start

### Prerequisites

- Python 3.9+ 
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd planventure
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
cd planventure-api
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .sample.env .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

6. **Start the server**
```bash
python3 app.py
```

The API will be available at `http://127.0.0.1:5000`

### Quick Test

```bash
# Check API health
curl http://127.0.0.1:5000/health

# Test registration
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!","confirm_password":"SecurePass123!","name":"Test User"}'

# Test public itinerary template
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=5&destination=Paris&trip_type=cultural"
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `planventure-api` directory:

```env
# Security Keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///instance/planventure.db

# CORS Configuration for React Frontend
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173

# Flask Environment
FLASK_ENV=development
FLASK_DEBUG=True

# API Configuration
API_HOST=127.0.0.1
API_PORT=5000
```

### Production Configuration

For production deployment:

1. Generate strong secret keys
2. Use a production database (PostgreSQL recommended)
3. Set `FLASK_ENV=production`
4. Configure specific CORS origins
5. Enable SSL/HTTPS
6. Set up proper logging

## 📡 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | User registration | No |
| `/auth/login` | POST | User login | No |
| `/auth/profile` | GET | Get user profile | Optional |
| `/auth/validate-email` | POST | Email validation | No |

### Trip Management

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/trips` | GET | List user trips | Yes |
| `/api/trips` | POST | Create new trip | Yes |
| `/api/trips/<id>` | GET | Get specific trip | Yes |
| `/api/trips/<id>` | PUT | Update entire trip | Yes |
| `/api/trips/<id>` | PATCH | Partial trip update | Yes |
| `/api/trips/<id>` | DELETE | Delete trip | Yes |
| `/api/trips/stats` | GET | Trip statistics | Yes |

### Itinerary Templates

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/trips/itinerary-template` | GET | Generate public template | No |
| `/api/trips/<id>/generate-itinerary` | POST | Generate for existing trip | Yes |

### Health & Monitoring

| Endpoint | Method | Description | Purpose |
|----------|--------|-------------|---------|
| `/health` | GET | Comprehensive health check | Operations monitoring |
| `/status` | GET | Simple status check | Load balancer |
| `/ready` | GET | Readiness probe | Kubernetes |
| `/live` | GET | Liveness probe | Kubernetes |

### Example API Usage

#### User Registration & Authentication

```bash
# Register new user
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "name": "John Doe"
  }'

# Login user
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Response includes access_token for authenticated requests
```

#### Trip Management

```bash
# Create trip (requires authentication token)
curl -X POST http://127.0.0.1:5000/api/trips \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris, France",
    "start_date": "2026-06-15",
    "end_date": "2026-06-22",
    "description": "European summer vacation",
    "budget": 2500.00
  }'

# List trips with filtering
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://127.0.0.1:5000/api/trips?destination=Paris&sort=budget&order=desc&page=1&per_page=10"

# Get trip statistics
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "http://127.0.0.1:5000/api/trips/stats"
```

#### Itinerary Generation

```bash
# Generate public template (no auth required)
curl "http://127.0.0.1:5000/api/trips/itinerary-template?duration=7&destination=Tokyo&trip_type=cultural"

# Generate itinerary for existing trip (requires auth)
curl -X POST http://127.0.0.1:5000/api/trips/123/generate-itinerary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"trip_type": "adventure"}'
```

## 🎯 Features Deep Dive

### 🔐 Authentication System

- **JWT Token-based** authentication with access and refresh tokens
- **Middleware protection** for routes requiring authentication
- **Optional authentication** support for flexible endpoints
- **Secure password hashing** with industry-standard algorithms
- **User context management** throughout request lifecycle

### 🗂️ Trip Management

- **Complete CRUD operations** with proper HTTP methods
- **Advanced filtering** by destination, dates, budget, status
- **Pagination support** for large datasets
- **Sorting capabilities** with multiple criteria
- **User ownership validation** ensuring data security
- **Rich metadata** including coordinates, itineraries, status tracking

### 🎯 Smart Itinerary Generation

- **6 Trip Types Supported**:
  - **Cultural**: Museums, galleries, festivals, workshops
  - **Adventure**: Hiking, water sports, extreme activities  
  - **Business**: Meetings, conferences, networking
  - **Relaxation**: Spas, beaches, wellness activities
  - **Family**: Kid-friendly attractions, educational tours
  - **General**: Popular attractions, local experiences

- **Duration-based Structure**: Intelligent daily activity planning
- **Destination-aware**: Location-specific activity suggestions
- **Customizable Templates**: Flexible framework for personalization

### 🌐 React Integration

- **Comprehensive CORS** support for all major React development environments
- **Multiple port support**: 3000, 3001, 5173 (Vite), and more
- **Credentials support** for JWT authentication
- **Pre-configured headers** for seamless integration
- **Detailed integration guide** with code examples

### 📊 Health Monitoring

- **Multi-tier health checks** for different monitoring needs
- **Component-level diagnostics** (database, auth, CORS)
- **Performance metrics** with response time tracking
- **Kubernetes-ready probes** for container orchestration
- **Production monitoring** with appropriate HTTP status codes

## 🧪 Testing

The project includes comprehensive test suites for all major components:

### Run All Tests

```bash
cd planventure-api

# Test authentication system
python3 test_middleware_integration.py

# Test trip CRUD operations  
python3 test_trips_crud_fixed.py

# Test itinerary templates
python3 test_itinerary_simple.py

# Test CORS configuration
python3 test_cors_config.py

# Test health endpoints
python3 test_health_endpoints.py
```

### Test Coverage

- ✅ **Authentication Flow**: Registration, login, protected routes
- ✅ **Trip Operations**: Create, read, update, delete, filtering
- ✅ **Itinerary Generation**: Public templates, authenticated generation
- ✅ **CORS Integration**: Preflight requests, headers, credentials
- ✅ **Health Monitoring**: All endpoint types, error scenarios
- ✅ **Error Handling**: Validation, authentication, database errors

## 🚀 React Frontend Integration

The API is fully configured for React frontend development. See [REACT_INTEGRATION_GUIDE.md](REACT_INTEGRATION_GUIDE.md) for:

- Complete setup instructions
- CORS configuration details
- Authentication flow examples
- API client utilities
- React component examples
- Error handling patterns

### Supported React Environments

- **Create React App** (localhost:3000)
- **Next.js** (localhost:3000)
- **Vite** (localhost:5173)
- **Custom Development Servers** (configurable ports)

## 🛡️ Security Features

### Authentication Security
- JWT tokens with configurable expiration
- Secure password hashing (pbkdf2:sha256)
- Request rate limiting considerations
- User session management

### API Security
- Input validation and sanitization
- SQL injection protection (SQLAlchemy ORM)
- CORS security with origin validation
- Security headers (XSS, content type, framing)

### Deployment Security
- Environment variable configuration
- Secret key management
- HTTPS recommendations
- Database security best practices

## 📈 Performance & Monitoring

### Health Check Benchmarks
- `/status`: ~2ms (lightweight ping)
- `/live`: ~2ms (liveness probe)
- `/ready`: ~3ms (readiness check)
- `/health`: ~5-15ms (comprehensive diagnostics)

### Database Performance
- SQLite for development (fast, lightweight)
- Connection pooling ready
- Query optimization patterns
- Migration support via SQLAlchemy

### Monitoring Integration
- Structured JSON responses
- HTTP status codes following RFC standards
- Response time tracking
- Component-level health reporting

## 🚢 Deployment

### Development Deployment

```bash
cd planventure-api
python3 app.py
# Server runs on http://127.0.0.1:5000
```

### Production Deployment Options

#### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY planventure-api/ .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]
```

#### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: planventure-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: planventure-api
  template:
    metadata:
      labels:
        app: planventure-api
    spec:
      containers:
      - name: api
        image: planventure-api:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /live
            port: 5000
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
```

#### Traditional Server (nginx + gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Nginx configuration
upstream planventure_api {
    server 127.0.0.1:5000;
    health_check uri=/status;
}

server {
    listen 80;
    server_name api.planventure.com;
    
    location / {
        proxy_pass http://planventure_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `python3 test_*.py`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings for new functions and classes
- Include type hints where appropriate
- Write tests for new functionality

### Testing Requirements

- All new features must include tests
- Maintain or improve test coverage
- Test both success and error scenarios
- Validate API responses and error handling

## 📚 Documentation

- **API Endpoints**: Complete endpoint documentation in this README
- **Authentication**: Detailed auth flow in `AUTH_MIDDLEWARE_DOCS.md`
- **Trip Management**: CRUD operations guide in `TRIP_CRUD_API.md`
- **Health Monitoring**: Health check details in `HEALTH_ENDPOINTS.md`
- **React Integration**: Frontend guide in `REACT_INTEGRATION_GUIDE.md`

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Ensure database directory exists
mkdir -p instance

# Recreate database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### CORS Issues with React
```bash
# Verify CORS origins in .env
grep CORS_ORIGINS .env

# Test CORS preflight
curl -X OPTIONS -H "Origin: http://localhost:3000" http://127.0.0.1:5000/auth/login -v
```

#### Authentication Problems
```bash
# Test token generation
python3 -c "from jwt_utils import generate_token; print('Token test:', generate_token({'user_id': 1}))"

# Verify middleware
python3 test_middleware_integration.py
```

#### Port Already in Use
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
export API_PORT=5001
python3 app.py
```

### Getting Help

- Check the health endpoint: `curl http://127.0.0.1:5000/health`
- Run the test suites to identify issues
- Review the comprehensive documentation
- Check application logs for detailed error messages

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask development team for the excellent framework
- SQLAlchemy contributors for robust ORM functionality
- JWT.io for token standard documentation
- React team for frontend integration patterns

---

**PlanVenture API** - Empowering travel planning applications with robust, secure, and intelligent backend services. 🌍✈️

Built with ❤️ using Flask, SQLAlchemy, and modern API best practices.