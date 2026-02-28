# Health Check Endpoints Documentation

The PlanVenture API provides comprehensive health monitoring through multiple endpoints designed for different monitoring and deployment scenarios.

## 📊 Available Endpoints

### 1. `/health` - Comprehensive Health Check
**Purpose**: Detailed system health monitoring for operations teams  
**HTTP Status**: 200 (healthy) | 503 (unhealthy)

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-28T22:48:22.054139Z",
  "uptime_seconds": 125,
  "version": "1.0.0",
  "environment": "development",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time_ms": 2.45
    },
    "auth_middleware": {
      "status": "healthy"
    },
    "cors": {
      "status": "healthy",
      "origins_count": 6
    }
  }
}
```

**Features**:
- ✅ Database connectivity with response time
- ✅ Auth middleware status
- ✅ CORS configuration validation
- ✅ Application uptime tracking
- ✅ Version information
- ✅ Environment detection

### 2. `/status` - Simple Status Check
**Purpose**: Quick "ping" endpoint for load balancers  
**HTTP Status**: Always 200

**Response Example**:
```json
{
  "status": "ok",
  "timestamp": "2026-02-28T22:48:28.298610Z"
}
```

**Use Cases**:
- Load balancer health checks
- Quick availability tests
- Minimal overhead monitoring

### 3. `/ready` - Readiness Probe
**Purpose**: Kubernetes readiness probe to determine if pod can receive traffic  
**HTTP Status**: 200 (ready) | 503 (not ready)

**Response Example**:
```json
{
  "ready": true
}
```

**Dependencies Checked**:
- Database connectivity (critical for readiness)

### 4. `/live` - Liveness Probe  
**Purpose**: Kubernetes liveness probe to determine if pod should be restarted  
**HTTP Status**: Always 200 (unless application is completely dead)

**Response Example**:
```json
{
  "alive": true
}
```

## 🔧 Integration Examples

### Load Balancer Configuration

```nginx
# Nginx upstream health check
upstream planventure_api {
    server 127.0.0.1:5000;
    health_check uri=/status interval=30s;
}
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: planventure-api
spec:
  template:
    spec:
      containers:
      - name: api
        image: planventure-api:latest
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
```

### Monitoring & Alerting

```bash
# Prometheus monitoring
curl -s http://api.planventure.com/health | jq '.status'

# Nagios check
#!/bin/bash
HEALTH=$(curl -s http://api.planventure.com/health)
STATUS=$(echo $HEALTH | jq -r '.status')

if [ "$STATUS" = "healthy" ]; then
    echo "OK - API is healthy"
    exit 0
else
    echo "CRITICAL - API unhealthy: $HEALTH"
    exit 2
fi
```

### Application Monitoring

```python
# Python health check client
import requests
import json

def check_api_health():
    try:
        response = requests.get('http://127.0.0.1:5000/health', timeout=5)
        health_data = response.json()
        
        if health_data['status'] == 'healthy':
            print(f"✅ API healthy - Uptime: {health_data['uptime_seconds']}s")
            return True
        else:
            print(f"❌ API unhealthy: {health_data}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

# Usage
if check_api_health():
    print("Proceeding with API operations...")
else:
    print("API not available, aborting operations")
```

### JavaScript/React Integration

```javascript
// Health check for React frontend
const checkApiHealth = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/status');
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API available:', data);
      return true;
    } else {
      console.warn('⚠️ API health check failed:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ API unreachable:', error);
    return false;
  }
};

// Use in React component
useEffect(() => {
  const interval = setInterval(async () => {
    const isHealthy = await checkApiHealth();
    setApiStatus(isHealthy ? 'online' : 'offline');
  }, 30000); // Check every 30 seconds

  return () => clearInterval(interval);
}, []);
```

## 📈 Response Time Benchmarks

Based on testing, typical response times:

| Endpoint | Avg Response Time | Purpose |
|----------|------------------|---------|
| `/status` | ~2ms | Quick checks |
| `/live` | ~2ms | Liveness probe |
| `/ready` | ~3ms | Readiness probe |
| `/health` | ~5-15ms | Comprehensive check |

## 🚨 Error Scenarios

### Database Unavailable
- `/health` → 503 with detailed error
- `/ready` → 503 (not ready)
- `/status` → 200 (still responds)
- `/live` → 200 (app still running)

### Application Issues
- `/health` → May show specific component failures
- `/ready` → 503 if critical services down
- `/status` → 503 if app can't respond
- `/live` → No response if completely dead

## 💡 Best Practices

1. **Use `/status` for frequent checks** (load balancers, simple monitoring)
2. **Use `/health` for detailed diagnostics** (dashboards, troubleshooting)
3. **Use `/ready` and `/live` for Kubernetes** (container orchestration)
4. **Set appropriate timeouts** (3-5 seconds recommended)
5. **Monitor response times** (slow responses may indicate issues)
6. **Alert on status changes** (healthy → unhealthy transitions)

## 🔍 Troubleshooting

### Health Check Fails
1. Check if Flask server is running on port 5000
2. Verify database connectivity
3. Check auth middleware initialization
4. Review application logs

### Slow Response Times
1. Check database performance
2. Monitor system resources
3. Review network connectivity
4. Consider timeout adjustments

The health check system is designed to be robust and provide clear insights into the application's operational status, making it easier to maintain and monitor your PlanVenture API in production environments.