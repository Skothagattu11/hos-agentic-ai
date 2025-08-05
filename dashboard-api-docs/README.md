# Dashboard API Documentation

This folder contains comprehensive documentation for the missing API endpoints required to integrate bio-coach-hub with health-agent-main using the **Unified API Gateway** approach (Option 2).

## Documents Overview

### 1. `MISSING_APIS.md`
Complete list of missing API endpoints with detailed specifications including:
- Endpoint definitions
- Input parameters and validation
- Output response models
- Implementation complexity assessment

### 2. `IMPLEMENTATION_PLAN.md`
Step-by-step implementation guide covering:
- Required new components and services
- Database schema considerations
- External service integration patterns
- Testing strategies

### 3. `DATA_MODELS.md`
Pydantic model definitions for:
- Request/response schemas
- Data transformation patterns
- Error handling models

### 4. `INTEGRATION_ARCHITECTURE.md`
Technical architecture documentation covering:
- Service communication patterns
- Data flow diagrams
- Caching strategies
- Performance considerations

## Current Status

### Existing APIs in Health-Agent-Main
```
✅ POST /api/analyze          # Trigger new analysis
✅ GET  /api/status           # Check analysis status
✅ GET  /api/health           # Health check
✅ GET  /                     # Root endpoint
```

### Missing APIs (Documented in this folder)
```
❌ GET  /api/users                        # List all users
❌ GET  /api/users/{user_id}              # Get specific user profile
❌ GET  /api/users/{user_id}/dashboard    # Complete dashboard data
❌ GET  /api/users/{user_id}/trends       # Historical trends
❌ GET  /api/users/{user_id}/behavior     # Behavior analysis
❌ GET  /api/users/{user_id}/engagement   # Engagement metrics
❌ GET  /api/users/{user_id}/nutrition    # Nutrition plan
❌ GET  /api/users/{user_id}/routine      # Routine plan
❌ GET  /api/users/{user_id}/metrics      # Raw health metrics
```

## Implementation Priority

### Phase 1: Core User APIs
- User listing and profile retrieval
- Basic dashboard data aggregation

### Phase 2: Component-Specific APIs
- Individual analysis component endpoints
- Historical trend data

### Phase 3: Advanced Features
- Real-time updates
- Performance optimization
- Caching implementation

## Next Steps

1. Review all documentation files in this folder
2. Assess implementation effort and timeline
3. Begin implementation following the documented plan
4. Update bio-coach-hub to use new APIs

## Related Files

- `../health_agents/analysis_history_manager.py` - Memory management
- `../coordinator.py` - Analysis orchestration
- `../app.py` - Current FastAPI application
- `../bio-coach-hub/src/lib/mockData.ts` - Target data structure