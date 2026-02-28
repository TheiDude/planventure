# React Frontend Integration Guide

This document provides complete instructions for integrating a React frontend with the PlanVenture API.

## ✅ CORS Configuration Complete

The Flask API is now configured with comprehensive CORS support for React development:

### Supported Origins
- `http://localhost:3000` - Create React App default
- `http://localhost:3001` - Alternative CRA port  
- `http://localhost:5173` - Vite default port
- `http://127.0.0.1:3000` - IP-based access
- `http://127.0.0.1:3001` - Alternative IP port
- `http://127.0.0.1:5173` - Vite IP access

### CORS Features Enabled
- ✅ **Preflight requests** (OPTIONS) handled automatically
- ✅ **Credentials support** for authenticated requests
- ✅ **Custom headers** (Authorization, Content-Type) allowed
- ✅ **All HTTP methods** (GET, POST, PUT, PATCH, DELETE) supported
- ✅ **Exposed headers** for JWT token access

## 🚀 React Setup Instructions

### 1. Environment Configuration

The Flask API uses these environment variables (already configured):

```env
# CORS Configuration for React Frontend Development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173
```

### 2. API Base URL

Use this base URL in your React application:
```javascript
const API_BASE_URL = 'http://127.0.0.1:5000';
```

### 3. React HTTP Client Setup

#### Option A: Using Fetch API

Create an API client utility:

```javascript
// src/utils/apiClient.js
const API_BASE_URL = 'http://127.0.0.1:5000';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Important for CORS
      ...options,
    };

    // Add Authorization header if token exists
    if (this.token) {
      config.headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Authentication methods
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      this.token = data.access_token;
    }
    
    return data;
  }

  async logout() {
    localStorage.removeItem('access_token');
    this.token = null;
  }

  // Trip management methods
  async getTrips(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/trips?${queryString}`);
  }

  async createTrip(tripData) {
    return this.request('/api/trips', {
      method: 'POST',
      body: JSON.stringify(tripData),
    });
  }

  async updateTrip(tripId, tripData) {
    return this.request(`/api/trips/${tripId}`, {
      method: 'PUT',
      body: JSON.stringify(tripData),
    });
  }

  async deleteTrip(tripId) {
    return this.request(`/api/trips/${tripId}`, {
      method: 'DELETE',
    });
  }

  // Itinerary template methods
  async getItineraryTemplate(params) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/trips/itinerary-template?${queryString}`);
  }

  async generateItinerary(tripId, options) {
    return this.request(`/api/trips/${tripId}/generate-itinerary`, {
      method: 'POST',
      body: JSON.stringify(options),
    });
  }
}

export default new ApiClient();
```

#### Option B: Using Axios

```bash
npm install axios
```

```javascript
// src/utils/axiosConfig.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  withCredentials: true, // Important for CORS
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      // Redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default API;
```

### 4. React Components Examples

#### Authentication Component

```javascript
// src/components/Auth/LoginForm.js
import React, { useState } from 'react';
import apiClient from '../../utils/apiClient';

function LoginForm({ onLoginSuccess }) {
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await apiClient.login(credentials);
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={credentials.email}
          onChange={(e) => setCredentials({
            ...credentials,
            email: e.target.value
          })}
          required
        />
      </div>
      
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={credentials.password}
          onChange={(e) => setCredentials({
            ...credentials,
            password: e.target.value
          })}
          required
        />
      </div>

      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}

export default LoginForm;
```

#### Trip Management Component

```javascript
// src/components/Trips/TripList.js
import React, { useState, useEffect } from 'react';
import apiClient from '../../utils/apiClient';

function TripList() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const data = await apiClient.getTrips();
      setTrips(data.trips);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createTrip = async (tripData) => {
    try {
      const data = await apiClient.createTrip(tripData);
      setTrips([...trips, data.trip]);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) return <div>Loading trips...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>My Trips</h2>
      {trips.map((trip) => (
        <div key={trip.id} className="trip-card">
          <h3>{trip.destination}</h3>
          <p>{trip.start_date} to {trip.end_date}</p>
          <p>{trip.description}</p>
        </div>
      ))}
      
      {/* Add trip creation form here */}
    </div>
  );
}

export default TripList;
```

#### Itinerary Template Component

```javascript
// src/components/Trips/ItineraryTemplate.js
import React, { useState } from 'react';
import apiClient from '../../utils/apiClient';

function ItineraryTemplate() {
  const [params, setParams] = useState({
    duration: 5,
    destination: '',
    trip_type: 'general'
  });
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(false);

  const tripTypes = [
    'general', 'cultural', 'adventure', 
    'business', 'relaxation', 'family'
  ];

  const generateTemplate = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getItineraryTemplate(params);
      setTemplate(data);
    } catch (err) {
      console.error('Template generation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Generate Itinerary Template</h2>
      
      <form onSubmit={(e) => { e.preventDefault(); generateTemplate(); }}>
        <div>
          <label>Destination:</label>
          <input
            type="text"
            value={params.destination}
            onChange={(e) => setParams({
              ...params,
              destination: e.target.value
            })}
            placeholder="e.g., Paris, France"
          />
        </div>

        <div>
          <label>Duration (days):</label>
          <input
            type="number"
            min="1"
            max="30"
            value={params.duration}
            onChange={(e) => setParams({
              ...params,
              duration: parseInt(e.target.value)
            })}
          />
        </div>

        <div>
          <label>Trip Type:</label>
          <select
            value={params.trip_type}
            onChange={(e) => setParams({
              ...params,
              trip_type: e.target.value
            })}
          >
            {tripTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate Template'}
        </button>
      </form>

      {template && (
        <div className="template-result">
          <h3>Itinerary Template</h3>
          <div className="template-itinerary">
            {template.template.map((day) => (
              <div key={day.day} className="day-card">
                <h4>Day {day.day}</h4>
                <p><strong>{day.activity}</strong></p>
                <p><em>{day.location}</em></p>
                <small>{day.notes}</small>
              </div>
            ))}
          </div>

          <div className="activity-suggestions">
            <h4>Activity Suggestions:</h4>
            <ul>
              {template.activity_suggestions.map((activity, index) => (
                <li key={index}>{activity}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default ItineraryTemplate;
```

## 🔧 Development Setup

### 1. Start Flask API Server

```bash
cd planventure-api
python3 app.py
# Server runs on http://127.0.0.1:5000
```

### 2. Create React App

```bash
npx create-react-app planventure-frontend
cd planventure-frontend
npm start
# React app runs on http://localhost:3000
```

### 3. Environment Variables

Create `.env.local` in your React app:

```env
REACT_APP_API_URL=http://127.0.0.1:5000
```

## 🚨 Common Issues & Solutions

### CORS Errors
- ✅ **Fixed**: All CORS configuration is properly set up
- **Verify**: Flask server is running on port 5000
- **Check**: React app origin is in allowed CORS origins

### Authentication Issues
- **Token Storage**: Use `localStorage` or `sessionStorage`
- **Token Format**: Always prefix with `Bearer `
- **Token Expiry**: Handle 401 responses gracefully

### Network Errors
- **Localhost vs 127.0.0.1**: Use consistent addressing
- **Port Conflicts**: Ensure Flask runs on 5000, React on 3000
- **Firewall**: Check local firewall settings

## 📋 API Endpoints Summary

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile (optional auth)

### Trip Management
- `GET /api/trips` - List user trips
- `POST /api/trips` - Create new trip
- `GET /api/trips/{id}` - Get specific trip
- `PUT /api/trips/{id}` - Update trip
- `DELETE /api/trips/{id}` - Delete trip

### Itinerary Templates
- `GET /api/trips/itinerary-template` - Public template generation
- `POST /api/trips/{id}/generate-itinerary` - Generate for existing trip

## 🎉 Ready for Development!

Your Flask API is now fully configured for React frontend integration with:

- ✅ Comprehensive CORS support
- ✅ Multiple development ports supported  
- ✅ JWT authentication ready
- ✅ Full CRUD operations available
- ✅ Itinerary template generation
- ✅ Error handling configured

Start building your React frontend and enjoy seamless API integration!