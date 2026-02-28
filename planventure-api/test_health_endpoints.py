#!/usr/bin/env python3
"""
Test script for health check endpoints
"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def test_health_endpoints():
    """Test all health check endpoints"""
    
    print("=" * 60)
    print("TESTING HEALTH CHECK ENDPOINTS")
    print("=" * 60)
    
    endpoints = [
        ('/health', 'Comprehensive Health Check'),
        ('/status', 'Simple Status Check'),
        ('/ready', 'Readiness Probe'),
        ('/live', 'Liveness Probe')
    ]
    
    for endpoint, description in endpoints:
        print(f"\n🔍 Testing {description} - {endpoint}")
        
        try:
            start_time = time.time()
            response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Time: {response_time:.2f}ms")
            
            if response.status_code in [200, 503]:  # 503 expected if unhealthy
                try:
                    data = response.json()
                    print(f"   Status: {data.get('status', 'N/A')}")
                    
                    # Pretty print health details for comprehensive endpoint
                    if endpoint == '/health':
                        print("   📊 Health Details:")
                        if 'checks' in data:
                            for check, details in data['checks'].items():
                                status_emoji = "✅" if details.get('status') == 'healthy' else "❌"
                                print(f"      {status_emoji} {check}: {details.get('status')}")
                                if 'response_time_ms' in details:
                                    print(f"         Response time: {details['response_time_ms']}ms")
                        
                        print(f"   ⏱️  Uptime: {data.get('uptime_seconds', 0)} seconds")
                        print(f"   🏷️  Version: {data.get('version', 'N/A')}")
                        print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
                    
                    # Check specific endpoint responses
                    if endpoint == '/ready':
                        ready_status = "✅ Ready" if data.get('ready') else "❌ Not Ready"
                        print(f"   {ready_status}")
                    elif endpoint == '/live':
                        alive_status = "✅ Alive" if data.get('alive') else "❌ Not Alive"
                        print(f"   {alive_status}")
                    
                    print("   ✅ Endpoint working correctly")
                    
                except json.JSONDecodeError:
                    print("   ❌ Invalid JSON response")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed - Server not running?")
        except requests.exceptions.Timeout:
            print("   ❌ Request timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_health_monitoring():
    """Test health endpoint multiple times to check consistency"""
    
    print(f"\n{'='*60}")
    print("TESTING HEALTH MONITORING CONSISTENCY")
    print("="*60)
    
    print("\n🔄 Running 5 consecutive health checks...")
    
    response_times = []
    statuses = []
    
    for i in range(5):
        try:
            start_time = time.time()
            response = requests.get(f'{BASE_URL}/health', timeout=5)
            response_time = (time.time() - start_time) * 1000
            response_times.append(response_time)
            
            data = response.json()
            status = data.get('status', 'unknown')
            statuses.append(status)
            
            print(f"   Check {i+1}: {status} ({response_time:.2f}ms)")
            
            time.sleep(0.1)  # Small delay between requests
            
        except Exception as e:
            print(f"   Check {i+1}: Error - {e}")
            statuses.append('error')
    
    # Summary
    print(f"\n📈 Performance Summary:")
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"   Average response time: {avg_time:.2f}ms")
        print(f"   Min response time: {min_time:.2f}ms")
        print(f"   Max response time: {max_time:.2f}ms")
    
    unique_statuses = set(statuses)
    print(f"   Status consistency: {len(unique_statuses) == 1}")
    print(f"   Statuses observed: {unique_statuses}")

if __name__ == '__main__':
    print("Testing PlanVenture API Health Check Endpoints...")
    print(f"Base URL: {BASE_URL}")
    print("\nEnsure Flask server is running!")
    input("Press Enter to continue...")
    
    try:
        test_health_endpoints()
        test_health_monitoring()
        
        print(f"\n{'🎉'*20}")
        print("HEALTH CHECK TESTING COMPLETE!")
        print("🎉"*20)
        
        print("\n📋 Available Health Endpoints:")
        print("   🔍 /health  - Comprehensive health check with detailed metrics")
        print("   ⚡ /status  - Simple 'ok' status response")  
        print("   🎯 /ready   - Kubernetes readiness probe")
        print("   💓 /live    - Kubernetes liveness probe")
        
        print("\n🔧 Integration Examples:")
        print("   Load Balancer: Use /status for quick checks")
        print("   Monitoring: Use /health for detailed metrics")
        print("   Kubernetes: Use /ready and /live for probes")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")