# Implementation Plan for Dashboard APIs

This document provides a comprehensive step-by-step implementation plan for adding the missing API endpoints to health-agent-main.

## Overview

**Goal**: Transform health-agent-main from analysis-only service to full dashboard backend supporting bio-coach-hub frontend.

**Approach**: Unified API Gateway pattern where health-agent-main orchestrates data from multiple sources.

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
### Phase 2: User Management APIs (Week 2)  
### Phase 3: Component-Specific APIs (Week 3)
### Phase 4: Advanced Features (Week 4)

---

## PHASE 1: Core Infrastructure

**Duration**: 5-7 days
**Priority**: Critical - Foundation for all other APIs

### 1.1 External API Client Integration

#### Create HosFapiClient Service
**File**: `health_agents/hos_fapi_client.py`

**Requirements**:
- HTTP client using `httpx` library
- Async/await support for non-blocking calls
- Connection pooling and timeout handling
- Retry logic with exponential backoff
- Error handling and logging

**Implementation Steps**:
1. Add `httpx` to requirements.txt
2. Create base HTTP client class
3. Implement authentication if required
4. Add method for each hos-fapi endpoint
5. Implement comprehensive error handling
6. Add connection testing and health checks

**Configuration Needed**:
```python
# Environment variables
HOS_FAPI_BASE_URL=http://localhost:8001
HOS_FAPI_TIMEOUT=30
HOS_FAPI_MAX_RETRIES=3
HOS_FAPI_RETRY_BASE_DELAY=1.0
```

**Testing Requirements**:
- Unit tests with mocked HTTP responses
- Integration tests with actual hos-fapi-hm-sahha-main
- Error scenario testing (timeouts, 404s, 500s)
- Performance testing under load

### 1.2 User Service Layer

#### Create UserService Class  
**File**: `health_agents/user_service.py`

**Requirements**:
- Data orchestration from multiple sources
- User profile management
- Analysis data aggregation
- Caching integration
- Error handling with graceful degradation

**Implementation Steps**:
1. Create base UserService class
2. Integrate with existing AnalysisHistoryManager
3. Add HosFapiClient integration
4. Implement data combination logic
5. Add validation and error handling
6. Create user profile models

**Dependencies**:
- `analysis_history_manager.py` (existing)
- `hos_fapi_client.py` (new)
- Pydantic models (new)

### 1.3 Response Models

#### Create Pydantic Models
**File**: `health_agents/dashboard_models.py`

**Requirements**:
- Type-safe response models
- Data validation and serialization
- Consistent API response format
- Error response models

**Models Needed**:
```python
class UserProfile(BaseModel)
class DashboardData(BaseModel)
class BehaviorAnalysis(BaseModel)
class NutritionPlan(BaseModel)
class RoutinePlan(BaseModel)
class HealthMetrics(BaseModel)
class TrendData(BaseModel)
class APIError(BaseModel)
```

### 1.4 Caching Layer

#### Implement Response Caching
**File**: `health_agents/cache_service.py`

**Requirements**:
- In-memory caching for frequently accessed data
- TTL-based cache expiration
- Cache invalidation strategies
- Memory usage monitoring

**Implementation Options**:
- Python `cachetools` library
- Redis integration (optional, for production)
- Custom LRU cache implementation

---

## PHASE 2: User Management APIs

**Duration**: 3-5 days
**Priority**: High - Required for basic dashboard functionality

### 2.1 User Listing Endpoint

#### Implement GET /api/users
**File**: Update `app.py`

**Implementation Steps**:
1. Create user listing route handler
2. Query unique users from analysis_memory table
3. Aggregate user data from multiple sources
4. Implement pagination support
5. Add search and filtering capabilities
6. Optimize for performance with database indexes

**Database Queries Needed**:
```sql
-- Get all unique profile_ids with latest analysis
SELECT DISTINCT profile_id, 
       MAX(analysis_date) as last_analysis,
       COUNT(*) as analysis_count
FROM analysis_memory 
GROUP BY profile_id;
```

**Performance Considerations**:
- Database indexing on profile_id and analysis_date
- Limit concurrent external API calls
- Implement request batching for hos-fapi calls
- Add response caching (5-minute TTL)

### 2.2 Individual User Profile

#### Implement GET /api/users/{user_id}
**File**: Update `app.py`

**Implementation Steps**:
1. Create user profile route handler
2. Validate user_id exists
3. Get user analysis history
4. Fetch current metrics from hos-fapi
5. Combine and format response
6. Handle missing data gracefully

**Data Sources**:
- Analysis history: PostgreSQL (analysis_memory table)
- Current metrics: hos-fapi-hm-sahha-main API
- User profile: Derived from analysis data

**Error Handling**:
- 404 for non-existent users
- Partial data when external APIs fail
- Graceful degradation with meaningful error messages

---

## PHASE 3: Component-Specific APIs

**Duration**: 5-7 days
**Priority**: Medium - Required for complete dashboard functionality

### 3.1 Simple Data Extraction APIs

#### Implement Analysis Component Endpoints
- `GET /api/users/{user_id}/behavior`
- `GET /api/users/{user_id}/nutrition`
- `GET /api/users/{user_id}/routine`

**Implementation Strategy**:
1. Extract JSON data from analysis_memory table
2. Parse and validate JSON structure
3. Format for frontend consumption
4. Add data quality indicators
5. Handle missing or corrupt data

**JSON Parsing Logic**:
```python
def parse_behavior_analysis(analysis_json: str) -> BehaviorAnalysis:
    data = json.loads(analysis_json)
    # Validate required fields
    # Transform data structure
    # Handle missing fields with defaults
    return BehaviorAnalysis(**data)
```

### 3.2 Engagement Analysis API

#### Implement GET /api/users/{user_id}/engagement
**File**: Update `app.py`

**Implementation Steps**:
1. Extract engagement_metrics from analysis_memory
2. Calculate engagement trends over time
3. Generate engagement insights
4. Provide usage pattern analysis
5. Handle users with limited data

**Calculation Logic**:
- Daily engagement scores from analysis history
- Feature usage percentages
- Trend analysis over specified period
- Pattern recognition for usage insights

### 3.3 Dashboard Aggregation API

#### Implement GET /api/users/{user_id}/dashboard
**File**: Update `app.py`

**Implementation Steps**:
1. Orchestrate calls to all data sources
2. Combine user profile, metrics, and analysis data
3. Optimize for single API call performance
4. Implement comprehensive error handling
5. Add response caching

**Data Orchestration Pattern**:
```python
async def get_dashboard_data(user_id: str):
    # Parallel execution of data fetching
    tasks = [
        get_user_profile(user_id),
        get_current_metrics(user_id),
        get_analysis_data(user_id),
        get_trends_data(user_id)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results with error handling
    return combine_dashboard_data(results)
```

---

## PHASE 4: Advanced Features

**Duration**: 5-7 days
**Priority**: Low - Enhancement features

### 4.1 Historical Trends API

#### Implement GET /api/users/{user_id}/trends
**File**: Update `app.py`

**Implementation Steps**:
1. Query historical data from multiple sources
2. Combine time-series data from PostgreSQL and hos-fapi
3. Handle data gaps and inconsistencies
4. Calculate trend analysis (improving/declining metrics)
5. Optimize for large date ranges

**Data Aggregation Strategy**:
- Use database window functions for efficient queries
- Implement data interpolation for missing points
- Calculate moving averages and trend directions
- Provide data quality indicators

### 4.2 Raw Metrics Integration

#### Implement GET /api/users/{user_id}/metrics
**File**: Update `app.py`

**Implementation Steps**:
1. Integrate with hos-fapi-hm-sahha-main endpoints
2. Handle multiple metric types and date ranges
3. Combine scores, biomarkers, and archetype data
4. Implement data completeness indicators
5. Add intelligent caching strategies

**External API Integration**:
```python
async def get_user_metrics(user_id: str, date: str):
    # Call multiple hos-fapi endpoints
    scores = await hos_fapi.get_scores(user_id, date)
    biomarkers = await hos_fapi.get_biomarkers(user_id, date)
    archetypes = await hos_fapi.get_archetypes(user_id, date)
    
    # Combine and validate data
    return combine_metrics_data(scores, biomarkers, archetypes)
```

### 4.3 Performance Optimization

#### Implement Caching and Optimization
**Files**: Various

**Optimization Areas**:
1. Database query optimization
2. Response caching implementation
3. Parallel API call execution
4. Connection pooling
5. Memory usage optimization

**Caching Strategy**:
- User profiles: 15-minute TTL
- Dashboard data: 5-minute TTL
- Historical trends: 1-hour TTL
- Static analysis data: 24-hour TTL

---

## DATABASE CONSIDERATIONS

### Required Indexes
```sql
-- Performance indexes for user queries
CREATE INDEX idx_analysis_memory_profile_date 
ON analysis_memory(profile_id, analysis_date DESC);

CREATE INDEX idx_analysis_memory_profile_type 
ON analysis_memory(profile_id, analysis_type);

-- Composite index for user listing
CREATE INDEX idx_analysis_memory_composite 
ON analysis_memory(profile_id, analysis_date DESC, analysis_type);
```

### Data Migration Needs
- No schema changes required
- Existing data is compatible
- Consider data cleanup for better performance

---

## TESTING STRATEGY

### Unit Testing
**Framework**: `pytest` with `pytest-asyncio`

**Test Coverage Requirements**:
- All service classes (>90% coverage)
- All API endpoints (>95% coverage)
- Error handling scenarios (100% coverage)
- Data transformation logic (100% coverage)

### Integration Testing
**Requirements**:
- Test with actual PostgreSQL database
- Mock hos-fapi-hm-sahha-main responses
- Test complete API workflows
- Validate response schemas

### Performance Testing
**Tools**: `pytest-benchmark`, `locust`

**Performance Targets**:
- User listing: <500ms for 100 users
- Dashboard data: <1000ms per user
- Trends data: <2000ms for 30-day range
- Cache hit ratio: >80% for repeated requests

### End-to-End Testing
**Requirements**:
- Test bio-coach-hub integration
- Validate complete user workflows
- Test error scenarios and recovery
- Verify data consistency

---

## DEPLOYMENT CONSIDERATIONS

### Environment Configuration
```env
# New environment variables needed
HOS_FAPI_BASE_URL=http://localhost:8001
HOS_FAPI_TIMEOUT=30
HOS_FAPI_MAX_RETRIES=3
CACHE_TTL_USER_PROFILE=900
CACHE_TTL_DASHBOARD=300
CACHE_TTL_TRENDS=3600
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Monitoring and Logging
**Requirements**:
- API endpoint metrics
- External API call monitoring
- Database query performance
- Cache hit/miss ratios
- Error rate tracking

### Scalability Considerations
**Horizontal Scaling**:
- Stateless API design
- External cache for multi-instance deployment
- Database connection pooling
- Load balancer health checks

**Vertical Scaling**:
- Memory usage optimization
- Database query optimization
- Connection pool tuning
- Cache size optimization

---

## ROLLBACK PLAN

### Safe Deployment Strategy
1. **Phase 1**: Deploy infrastructure without breaking changes
2. **Phase 2**: Add new endpoints while maintaining existing functionality
3. **Phase 3**: Gradual endpoint rollout with feature flags
4. **Phase 4**: Full integration testing before production

### Rollback Triggers
- API response time >5 seconds
- Error rate >5%
- Database connection issues
- External API integration failures

### Rollback Procedure
1. Disable new endpoints via feature flags
2. Revert to previous application version
3. Clear cached data if necessary
4. Verify core functionality restored

---

## SUCCESS METRICS

### Technical Metrics
- API response times within targets
- Error rates <1% for all endpoints
- Cache hit ratio >80%
- Database query performance optimized

### Business Metrics
- Successful bio-coach-hub integration
- Complete dashboard functionality
- User data accuracy and consistency
- System reliability and uptime

### Quality Metrics
- Test coverage >90%
- Code review approval rate 100%
- Documentation completeness
- Performance benchmark compliance