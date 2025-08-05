# Integration Architecture for Dashboard APIs

This document outlines the technical architecture for integrating bio-coach-hub with health-agent-main using the Unified API Gateway pattern.

## Architecture Overview

### System Components
1. **Bio-Coach-Hub** (Frontend - React/TypeScript)
2. **Health-Agent-Main** (API Gateway - FastAPI/Python)
3. **Hos-Fapi-Hm-Sahha-Main** (Data Source - FastAPI/Python)
4. **PostgreSQL** (Analysis Storage)
5. **Supabase** (Metrics Storage)

### Integration Pattern: Backend-for-Frontend (BFF)

```
┌─────────────────┐    HTTP/REST     ┌──────────────────────┐
│                 │ ─────────────────▶│                      │
│  Bio-Coach-Hub  │                  │  Health-Agent-Main   │
│   (Frontend)    │◀───────────────── │   (API Gateway)      │
│                 │   JSON Response   │                      │
└─────────────────┘                  └──────────────────────┘
                                               │
                                               │ HTTP/REST
                                               │
                ┌──────────────────────────────┴──────────────────────────────┐
                │                                                             │
                ▼                                                             ▼
┌─────────────────────────────┐                              ┌─────────────────────────────┐
│                             │                              │                             │
│  Hos-Fapi-Hm-Sahha-Main   │                              │      PostgreSQL             │
│    (Metrics API)           │                              │   (Analysis Storage)        │
│                             │                              │                             │
└─────────────────────────────┘                              └─────────────────────────────┘
                │                                                             │
                │                                                             │
                ▼                                                             ▼
┌─────────────────────────────┐                              ┌─────────────────────────────┐
│                             │                              │                             │
│        Supabase             │                              │    Analysis Memory          │
│    (Metrics Storage)        │                              │      User Profiles          │
│                             │                              │   Behavior/Nutrition/       │
└─────────────────────────────┘                              │      Routine Plans          │
                                                              └─────────────────────────────┘
```

---

## SERVICE LAYER ARCHITECTURE

### 1. Health-Agent-Main Service Structure

```python
# New service layer architecture
health_agents/
├── services/
│   ├── __init__.py
│   ├── user_service.py          # User management and orchestration
│   ├── metrics_service.py       # External metrics integration
│   ├── analysis_service.py      # Analysis data retrieval
│   ├── cache_service.py         # Caching layer
│   └── integration_service.py   # External API management
├── clients/
│   ├── __init__.py
│   ├── hos_fapi_client.py      # HTTP client for hos-fapi-hm-sahha-main
│   └── database_client.py       # Enhanced database operations
├── models/
│   ├── __init__.py
│   ├── dashboard_models.py      # API request/response models
│   ├── integration_models.py    # External API models
│   └── database_models.py       # Database entity models
└── utils/
    ├── __init__.py
    ├── data_transformer.py     # Data transformation utilities
    ├── error_handler.py        # Error handling utilities
    └── validator.py            # Data validation utilities
```

### 2. Service Interaction Pattern

```python
# Request flow through service layers
@app.get("/api/users/{user_id}/dashboard")
async def get_dashboard(user_id: str, params: DashboardParams):
    # 1. Request validation (handled by FastAPI + Pydantic)
    
    # 2. Service orchestration
    user_service = UserService()
    dashboard_data = await user_service.get_dashboard_data(user_id, params)
    
    # 3. Response serialization (handled by Pydantic)
    return DashboardResponse(**dashboard_data)

# UserService orchestrates multiple data sources
class UserService:
    def __init__(self):
        self.metrics_service = MetricsService()
        self.analysis_service = AnalysisService()
        self.cache_service = CacheService()
    
    async def get_dashboard_data(self, user_id: str, params: DashboardParams):
        # Check cache first
        cache_key = f"dashboard:{user_id}:{params.days}"
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            return cached_data
        
        # Orchestrate data collection
        tasks = [
            self.analysis_service.get_user_profile(user_id),
            self.metrics_service.get_current_metrics(user_id),
            self.metrics_service.get_trends(user_id, params.days),
            self.analysis_service.get_latest_analysis(user_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results and handle errors
        dashboard_data = self.combine_dashboard_data(results)
        
        # Cache the result
        await self.cache_service.set(cache_key, dashboard_data, ttl=300)
        
        return dashboard_data
```

---

## DATA FLOW PATTERNS

### 1. Single API Call Pattern (Dashboard)

```
Bio-Coach-Hub Request:
GET /api/users/123/dashboard

Health-Agent-Main Execution:
├── 1. Validate user_id and parameters
├── 2. Check cache for existing dashboard data
├── 3. If cache miss, orchestrate data collection:
│   ├── a. Get user profile from PostgreSQL
│   ├── b. Get current metrics from hos-fapi-hm-sahha-main
│   ├── c. Get trend data from hos-fapi-hm-sahha-main
│   └── d. Get latest analysis from PostgreSQL
├── 4. Combine all data sources
├── 5. Cache the combined result
└── 6. Return unified dashboard response

Bio-Coach-Hub receives complete dashboard data in single response
```

### 2. Component-Specific Pattern (Behavior Analysis)

```
Bio-Coach-Hub Request:
GET /api/users/123/behavior

Health-Agent-Main Execution:
├── 1. Validate user_id
├── 2. Query analysis_memory table for behavior_analysis JSON
├── 3. Parse and validate JSON structure
├── 4. Transform to BehaviorAnalysisResponse model
└── 5. Return structured behavior data

Bio-Coach-Hub receives formatted behavior analysis data
```

### 3. Aggregated Data Pattern (User Listing)

```
Bio-Coach-Hub Request:
GET /api/users?limit=50&search=sarah

Health-Agent-Main Execution:
├── 1. Query all unique profile_ids from analysis_memory
├── 2. Apply search filters
├── 3. For each user (in parallel):
│   ├── a. Get latest analysis data from PostgreSQL
│   └── b. Get today's metrics from hos-fapi-hm-sahha-main
├── 4. Combine user data with pagination
└── 5. Return user list with metadata

Bio-Coach-Hub receives paginated user list with search results
```

---

## ERROR HANDLING STRATEGY

### 1. Error Classification

```python
class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"        # 400 - Bad request data
    NOT_FOUND_ERROR = "not_found"               # 404 - Resource not found
    EXTERNAL_API_ERROR = "external_api_error"   # 503 - External service failure
    DATABASE_ERROR = "database_error"           # 500 - Database connectivity
    TIMEOUT_ERROR = "timeout_error"             # 504 - Request timeout
    RATE_LIMIT_ERROR = "rate_limit_error"       # 429 - Too many requests
    INTERNAL_ERROR = "internal_server_error"    # 500 - Unexpected error
```

### 2. Graceful Degradation Pattern

```python
async def get_dashboard_data_with_fallback(user_id: str):
    dashboard_data = {
        "user_profile": None,
        "current_metrics": None,
        "trends": [],
        "latest_analysis": None
    }
    
    # Critical data (must succeed)
    try:
        dashboard_data["user_profile"] = await get_user_profile(user_id)
    except Exception as e:
        # User profile is critical - fail the request
        raise UserNotFoundError(f"User {user_id} not found")
    
    # Optional data (graceful degradation)
    try:
        dashboard_data["current_metrics"] = await get_current_metrics(user_id)
    except ExternalAPIError:
        # Use fallback/cached metrics or None
        dashboard_data["current_metrics"] = await get_cached_metrics(user_id)
        logging.warning(f"Using cached metrics for user {user_id}")
    
    try:
        dashboard_data["trends"] = await get_trends(user_id)
    except Exception:
        # Trends are optional - return empty array
        dashboard_data["trends"] = []
        logging.warning(f"Trends unavailable for user {user_id}")
    
    return dashboard_data
```

### 3. Circuit Breaker Pattern

```python
from circuitbreaker import circuit

class MetricsService:
    @circuit(failure_threshold=5, recovery_timeout=30)
    async def get_metrics_from_hos_fapi(self, user_id: str):
        """Circuit breaker protects against cascading failures"""
        response = await self.hos_fapi_client.get_user_metrics(user_id)
        return response
    
    async def get_current_metrics(self, user_id: str):
        try:
            return await self.get_metrics_from_hos_fapi(user_id)
        except CircuitBreakerOpenException:
            # Circuit breaker is open - return cached data
            logging.warning("hos-fapi circuit breaker open, using cached data")
            return await self.get_cached_metrics(user_id)
```

---

## CACHING STRATEGY

### 1. Multi-Level Caching Architecture

```
┌─────────────────┐    L1 Cache     ┌──────────────────┐
│                 │   (In-Memory)   │                  │
│  Bio-Coach-Hub  │◀──────────────▶ │ Health-Agent-    │
│                 │                 │ Main (FastAPI)   │
└─────────────────┘                 │                  │
                                    │  L2 Cache        │
                                    │ (Redis/Memory)   │
                                    └──────────────────┘
                                             │
                                             │ L3 Cache
                                             │ (Database Query Cache)
                                             ▼
                                    ┌──────────────────┐
                                    │                  │
                                    │   Data Sources   │
                                    │ (PostgreSQL +    │
                                    │  Hos-Fapi)       │
                                    └──────────────────────
```

### 2. Cache Configuration

```python
class CacheConfig:
    """Cache TTL configuration in seconds"""
    USER_PROFILE = 900      # 15 minutes
    DASHBOARD_DATA = 300    # 5 minutes
    CURRENT_METRICS = 120   # 2 minutes
    TRENDS_DATA = 3600      # 1 hour
    ANALYSIS_DATA = 86400   # 24 hours (rarely changes)
    USER_LIST = 300         # 5 minutes

class CacheService:
    def __init__(self):
        self.memory_cache = {}  # Simple in-memory cache
        # TODO: Add Redis client for production
    
    async def get(self, key: str):
        """Get cached value with TTL check"""
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del self.memory_cache[key]
        return None
    
    async def set(self, key: str, value: any, ttl: int):
        """Set cached value with TTL"""
        expiry = datetime.now() + timedelta(seconds=ttl)
        self.memory_cache[key] = (value, expiry)
```

### 3. Cache Invalidation Strategy

```python
class CacheInvalidation:
    """Cache invalidation rules"""
    
    def on_new_analysis(self, user_id: str):
        """Invalidate user-specific caches when new analysis is created"""
        keys_to_invalidate = [
            f"dashboard:{user_id}:*",
            f"user_profile:{user_id}",
            f"behavior:{user_id}",
            f"nutrition:{user_id}",
            f"routine:{user_id}",
            f"user_list:*"  # User list includes analysis data
        ]
        self.invalidate_pattern(keys_to_invalidate)
    
    def on_metrics_update(self, user_id: str):
        """Invalidate metrics-related caches"""
        keys_to_invalidate = [
            f"dashboard:{user_id}:*",
            f"current_metrics:{user_id}",
            f"trends:{user_id}:*"
        ]
        self.invalidate_pattern(keys_to_invalidate)
```

---

## PERFORMANCE OPTIMIZATION

### 1. Database Query Optimization

```sql
-- Required indexes for optimal performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_memory_profile_date 
ON analysis_memory(profile_id, analysis_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_memory_composite 
ON analysis_memory(profile_id, analysis_type, analysis_date DESC);

-- Optimized query for user listing
WITH latest_analysis AS (
    SELECT DISTINCT ON (profile_id) 
           profile_id, 
           analysis_date, 
           archetype,
           behavior_analysis IS NOT NULL as has_behavior,
           nutrition_plan IS NOT NULL as has_nutrition,
           routine_plan IS NOT NULL as has_routine
    FROM analysis_memory 
    ORDER BY profile_id, analysis_date DESC
)
SELECT profile_id, analysis_date, archetype, 
       has_behavior, has_nutrition, has_routine
FROM latest_analysis
LIMIT $1 OFFSET $2;
```

### 2. Parallel Processing Pattern

```python
async def get_multiple_users_data(user_ids: List[str]):
    """Process multiple users in parallel with controlled concurrency"""
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    async def get_user_with_semaphore(user_id: str):
        async with semaphore:
            return await get_user_data(user_id)
    
    tasks = [get_user_with_semaphore(user_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and log errors
    valid_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f"Failed to get data for user {user_ids[i]}: {result}")
        else:
            valid_results.append(result)
    
    return valid_results
```

### 3. Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Optimize response size with field selection
class UserSummaryOptimized(BaseModel):
    """Optimized user summary with only essential fields"""
    id: str
    name: str
    archetype: str
    overall_score: int
    # Exclude heavy fields like full analysis data
```

---

## MONITORING AND OBSERVABILITY

### 1. Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration', ['endpoint'])
EXTERNAL_API_CALLS = Counter('external_api_calls_total', 'External API calls', ['service', 'status'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['cache_type'])
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')

# Middleware for automatic metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(endpoint=request.url.path).observe(time.time() - start_time)
    
    return response
```

### 2. Structured Logging

```python
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage in services
class UserService:
    async def get_dashboard_data(self, user_id: str, params: DashboardParams):
        logger.info(
            "dashboard_request_started",
            user_id=user_id,
            days=params.days,
            request_id=generate_request_id()
        )
        
        try:
            data = await self._orchestrate_data_collection(user_id, params)
            
            logger.info(
                "dashboard_request_completed",
                user_id=user_id,
                data_sources=len(data.keys()),
                cache_hit=data.get('_from_cache', False)
            )
            
            return data
            
        except Exception as e:
            logger.error(
                "dashboard_request_failed",
                user_id=user_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
```

### 3. Health Check Endpoints

```python
from fastapi import status

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/health/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check():
    """Detailed health check with dependency status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {}
    }
    
    # Check database connectivity
    try:
        await check_database_connection()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check external API connectivity
    try:
        await check_hos_fapi_connection()
        health_status["services"]["hos_fapi"] = "healthy"
    except Exception as e:
        health_status["services"]["hos_fapi"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest
    return Response(generate_latest(), media_type="text/plain")
```

---

## SECURITY CONSIDERATIONS

### 1. Input Validation

```python
from pydantic import validator, Field
from typing import Pattern
import re

class SecureUserParams(BaseModel):
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$', max_length=50)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        # Additional validation beyond regex
        if not v or v.isspace():
            raise ValueError('User ID cannot be empty or whitespace')
        if '..' in v or '/' in v:
            raise ValueError('User ID contains invalid characters')
        return v
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/users")
@limiter.limit("30/minute")  # 30 requests per minute per IP
async def list_users(request: Request):
    # Implementation
    pass

@app.get("/api/users/{user_id}/dashboard")
@limiter.limit("60/minute")  # 60 requests per minute per IP
async def get_dashboard(request: Request, user_id: str):
    # Implementation
    pass
```

### 3. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

# Configure CORS for bio-coach-hub integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Bio-coach-hub development
        "https://your-bio-coach-hub-domain.com"  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)
```

---

## DEPLOYMENT ARCHITECTURE

### 1. Container Configuration

```dockerfile
# Dockerfile for health-agent-main with dashboard APIs
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Environment Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  health-agent-main:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/health_analysis
      - HOS_FAPI_BASE_URL=http://hos-fapi-hm-sahha-main:8001
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - CACHE_TTL_DASHBOARD=300
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - hos-fapi-hm-sahha-main
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  bio-coach-hub:
    build: ./bio-coach-hub
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://health-agent-main:8000
    depends_on:
      - health-agent-main
```

This architecture provides a robust, scalable foundation for integrating bio-coach-hub with health-agent-main while maintaining high performance, reliability, and maintainability.