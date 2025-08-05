# Phase 1 Dashboard API Testing Guide

This guide provides comprehensive instructions for testing the Phase 1 Dashboard API endpoints.

## Prerequisites

### 1. Install Dependencies
```bash
cd health-agent-main
pip install -r requirements.txt
```

### 2. Environment Setup
Ensure your `.env` file contains the required variables:

```env
# Database Configuration (existing)
DATABASE_URL=postgresql://username:password@localhost:5432/health_analysis
OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration (shared database)
SUPABASE_URL=https://your-project.supabase.co  
SUPABASE_KEY=your_supabase_anonymous_key

# Phase 1 Dashboard API Configuration
HOS_FAPI_BASE_URL=https://hos-fapi-hm-sahha.onrender.com
HOS_FAPI_TIMEOUT=30
HOS_FAPI_MAX_RETRIES=3
HOS_FAPI_RETRY_BASE_DELAY=2.0

# Optional: Cache configuration
CACHE_TTL_USER_PROFILE=900      # 15 minutes
CACHE_TTL_DASHBOARD=300         # 5 minutes  
CACHE_TTL_METRICS=180           # 3 minutes
```

### 3. Start the Server
```bash
cd health-agent-main
python app.py
```

The server will start at `http://localhost:8000`

---

## API Endpoint Testing

### **Test 1: Service Info Endpoint**
**Purpose**: Verify the API is running and configured correctly

```bash
curl -X GET "http://localhost:8000/api/v1/info" \
     -H "Content-Type: application/json" | jq
```

**Expected Response**:
```json
{
  "service": "health-agent-main-dashboard",
  "version": "1.0.0-phase1",
  "phase": "1",
  "environment": "development",
  "features_enabled": [
    "basic_user_listing",
    "user_profiles",
    "health_monitoring",
    "hybrid_data_access",
    "caching"
  ],
  "external_services": {
    "hos_fapi_url": "https://hos-fapi-hm-sahha.onrender.com",
    "supabase_project": "your-project-id"
  },
  "supported_archetypes": [
    "Foundation Builder",
    "Transformation Seeker",
    "Systematic Improver",
    "Peak Performer",
    "Resilience Rebuilder",
    "Connected Explorer"
  ]
}
```

**Success Criteria**: ✅ Returns 200 status with service configuration

---

### **Test 2: Health Check Endpoint**
**Purpose**: Verify all service connections are working

```bash
curl -X GET "http://localhost:8000/api/v1/health" \
     -H "Content-Type: application/json" | jq
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T12:00:00Z",
  "services": {
    "supabase_database": "healthy",
    "hos_fapi_api": "healthy",
    "analysis_memory": "healthy"
  },
  "statistics": {
    "total_users": 25,
    "users_with_analysis": 20,
    "users_with_health_data": 23
  },
  "cache_performance": {
    "hit_rate_percent": 0.0,
    "total_requests": 0,
    "cache_hits": 0
  }
}
```

**Success Criteria**: 
- ✅ Returns 200 status with "healthy" or "degraded" status
- ✅ All services show "healthy" status (or error details if issues exist)
- ✅ Statistics show actual user counts from database

**Troubleshooting**:
- If `supabase_database: "error"` → Check SUPABASE_URL and SUPABASE_KEY
- If `hos_fapi_api: "unhealthy"` → Verify https://hos-fapi-hm-sahha.onrender.com is accessible
- If `analysis_memory: "error"` → Check existing analysis_history_manager configuration

---

### **Test 3: User Listing Endpoint**
**Purpose**: Retrieve paginated list of users

```bash
# Basic user listing
curl -X GET "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" | jq

# With pagination parameters
curl -X GET "http://localhost:8000/api/v1/users?limit=5&offset=0" \
     -H "Content-Type: application/json" | jq
```

**Expected Response**:
```json
{
  "users": [
    {
      "id": "user123",
      "name": "John Doe",
      "age": 30,
      "total_analyses": 5,
      "last_analysis_date": "2025-08-05T10:30:00Z",
      "latest_archetype": "Peak Performer",
      "has_health_data": true,
      "overall_score": 85
    }
  ],
  "total_count": 25,
  "has_more": true
}
```

**Success Criteria**:
- ✅ Returns 200 status with user array
- ✅ Users have valid profile IDs from your database
- ✅ Analysis data (archetype, analysis count) matches database
- ✅ Health scores are present (from hos-fapi or direct Supabase)
- ✅ Pagination works correctly (has_more, total_count)

**Performance Test**:
```bash
# Test with larger limit
curl -X GET "http://localhost:8000/api/v1/users?limit=50" \
     -H "Content-Type: application/json" | jq '.users | length'
```

---

### **Test 4: Individual User Profile**
**Purpose**: Get detailed user information

```bash
# Replace USER_ID with an actual user ID from the listing
USER_ID="mbzXA48h4ASzre407KoFMepfyGv1"

curl -X GET "http://localhost:8000/api/v1/users/${USER_ID}" \
     -H "Content-Type: application/json" | jq
```

**Expected Response**:
```json
{
  "id": "user123",
  "name": "John Doe",
  "age": 30,
  "profile_created": "2025-07-01T00:00:00Z",
  "analysis_summary": {
    "total_analyses": 5,
    "initial_analyses": 2,
    "follow_up_analyses": 3,
    "last_analysis_date": "2025-08-05T10:30:00Z",
    "latest_archetype": "Peak Performer"
  },
  "current_health_scores": {
    "overall": 85,
    "readiness": 82,
    "sleep": 78,
    "activity": 90,
    "mental_wellbeing": 85
  },
  "data_availability": {
    "has_analysis_data": true,
    "has_health_scores": true,
    "has_biomarkers": false,
    "last_data_update": "2025-08-05T08:00:00Z"
  }
}
```

**Success Criteria**:
- ✅ Returns 200 status with complete user profile
- ✅ Analysis summary shows correct counts and latest archetype
- ✅ Health scores are populated (null values are acceptable if no data)
- ✅ Data availability flags are accurate

**Error Test**:
```bash
# Test with non-existent user ID
curl -X GET "http://localhost:8000/api/v1/users/nonexistent" \
     -H "Content-Type: application/json" | jq
```
Should return 404 with error details.

---

## Cache Testing

### **Test 5: Cache Performance**
**Purpose**: Verify caching is working correctly

```bash
# Get cache statistics
curl -X GET "http://localhost:8000/api/v1/cache/stats" \
     -H "Content-Type: application/json" | jq
```

**Cache Performance Test**:
```bash
# Make the same request multiple times to test caching
USER_ID="mbzXA48h4ASzre407KoFMepfyGv1"

echo "First request (cache miss):"
time curl -s "http://localhost:8000/api/v1/users/${USER_ID}" > /dev/null

echo "Second request (cache hit):"
time curl -s "http://localhost:8000/api/v1/users/${USER_ID}" > /dev/null

echo "Third request (cache hit):"
time curl -s "http://localhost:8000/api/v1/users/${USER_ID}" > /dev/null

# Check cache stats
curl -s "http://localhost:8000/api/v1/cache/stats" | jq '.cache_stats.hit_rate_percent'
```

**Success Criteria**:
- ✅ Second and third requests are faster than first
- ✅ Cache hit rate increases with repeated requests
- ✅ Cache stats show non-zero hit counts

---

## Error Handling Testing

### **Test 6: External API Failure Simulation**

**Simulate hos-fapi-hm-sahha unavailability**:
1. Temporarily change HOS_FAPI_BASE_URL to invalid URL in .env
2. Restart server
3. Test user endpoints

```bash
# Should still work with direct database fallback
curl -X GET "http://localhost:8000/api/v1/users?limit=3" | jq
```

**Success Criteria**:
- ✅ Users are still returned (via direct database queries)
- ✅ Health scores may be null but no errors
- ✅ Health check shows "degraded" status

### **Test 7: Database Connection Issues**

**Test with invalid Supabase credentials**:
1. Temporarily modify SUPABASE_URL in .env
2. Restart server
3. Test endpoints

```bash
curl -X GET "http://localhost:8000/api/v1/health" | jq
```

**Success Criteria**:
- ✅ Health check returns 503 status or "error" status
- ✅ Error messages are informative
- ✅ Service doesn't crash

---

## Performance Testing

### **Test 8: Concurrent Requests**

```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -s "http://localhost:8000/api/v1/users?limit=10" > /dev/null &
done
wait

echo "All requests completed. Check cache stats:"
curl -s "http://localhost:8000/api/v1/cache/stats" | jq
```

### **Test 9: Large Dataset**

```bash
# Test with maximum limit
curl -X GET "http://localhost:8000/api/v1/users?limit=100" \
     -H "Content-Type: application/json" | jq '.users | length'
```

**Success Criteria**:
- ✅ Response time under 5 seconds for 100 users
- ✅ No timeout errors
- ✅ Cache hit rate improves with repeated requests

---

## Integration Testing with Bio-Coach-Hub

### **Test 10: Frontend Integration**

If you have bio-coach-hub running locally:

```bash
# Test CORS headers
curl -X OPTIONS "http://localhost:8000/api/v1/users" \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -v
```

**Frontend API Test** (in bio-coach-hub):
```javascript
// Replace mockData import with real API calls
const API_BASE_URL = 'http://localhost:8000/api/v1';

async function fetchUsers() {
  try {
    const response = await fetch(`${API_BASE_URL}/users?limit=20`);
    const data = await response.json();
    console.log('Users fetched:', data.users.length);
    return data;
  } catch (error) {
    console.error('API Error:', error);
  }
}

async function fetchUserProfile(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`);
    const data = await response.json();
    console.log('User profile:', data);
    return data;
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

---

## Monitoring and Logging

### **Test 11: Log Verification**

Check the application logs for proper operation:

```bash
# Monitor logs while making requests
tail -f health_analysis_api.log | grep -E "(Dashboard|Phase1|ERROR)"
```

**Expected Log Entries**:
- ✅ "Dashboard API Phase 1 endpoints included"
- ✅ "External hos-fapi API connection successful"
- ✅ "Successfully listed X users"
- ✅ "Successfully retrieved user profile: USER_ID"
- ✅ "Health check completed: healthy"

---

## Troubleshooting Common Issues

### Issue 1: Import Errors
```
ImportError: No module named 'dashboard_api'
```
**Solution**: 
- Ensure you're running from the correct directory
- Install dependencies: `pip install -r requirements.txt`
- Check Python path includes the dashboard-api folder

### Issue 2: Supabase Connection Failed
```
"supabase_database": "error: Authentication error"
```
**Solution**:
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check Supabase project is active
- Verify database access permissions

### Issue 3: External API Timeout
```
"hos_fapi_api": "unhealthy"
```
**Solution**:
- Check https://hos-fapi-hm-sahha.onrender.com is accessible
- Increase HOS_FAPI_TIMEOUT if needed
- Verify network connectivity

### Issue 4: No Users Returned
```json
{"users": [], "total_count": 0, "has_more": false}
```
**Solution**:
- Check if profiles table has data
- Verify analysis_memory table has records
- Check database connection credentials

---

## Success Checklist

After running all tests, verify:

- ✅ **Service Status**: /api/v1/info returns correct configuration
- ✅ **Health Check**: All services show "healthy" status
- ✅ **User Listing**: Returns actual users from database
- ✅ **User Profiles**: Complete profiles with analysis + health data
- ✅ **Error Handling**: Graceful fallback when external API fails
- ✅ **Caching**: Performance improves with repeated requests
- ✅ **CORS**: Frontend can successfully call APIs
- ✅ **Logging**: Proper log entries for monitoring

## Next Steps

Once Phase 1 testing is complete:

1. **Deploy to Render**: Test with HTTPS endpoints
2. **Update bio-coach-hub**: Replace mockData with real API calls
3. **Performance Optimization**: Monitor response times under load
4. **Phase 2 Planning**: Implement dashboard aggregation endpoint

---

## Quick Test Script

Create a simple test script to run all basic tests:

```bash
#!/bin/bash
# test_phase1_apis.sh

API_BASE="http://localhost:8000/api/v1"

echo "=== Phase 1 Dashboard API Testing ==="

echo "1. Testing service info..."
curl -s "${API_BASE}/info" | jq -r '.service' || echo "❌ Info endpoint failed"

echo "2. Testing health check..."
HEALTH=$(curl -s "${API_BASE}/health" | jq -r '.status')
echo "Health status: $HEALTH"

echo "3. Testing user listing..."
USER_COUNT=$(curl -s "${API_BASE}/users?limit=5" | jq -r '.users | length')
echo "Users returned: $USER_COUNT"

if [ "$USER_COUNT" -gt 0 ]; then
    echo "4. Testing user profile..."
    USER_ID=$(curl -s "${API_BASE}/users?limit=1" | jq -r '.users[0].id')
    echo "Testing user: $USER_ID"
    curl -s "${API_BASE}/users/${USER_ID}" | jq -r '.id' || echo "❌ User profile failed"
fi

echo "5. Testing cache stats..."
curl -s "${API_BASE}/cache/stats" | jq -r '.cache_stats.hit_rate_percent' || echo "❌ Cache stats failed"

echo "=== Testing Complete ==="
```

Run with: `chmod +x test_phase1_apis.sh && ./test_phase1_apis.sh`