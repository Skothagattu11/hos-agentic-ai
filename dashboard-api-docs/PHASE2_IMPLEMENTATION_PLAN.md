# Phase 2 Implementation Plan: Analysis Data Extraction API

## Overview

Phase 2 focuses on creating a single, efficient API endpoint to extract date-sensitive analysis data from the `analysis_memory` table. This replaces the need for multiple API calls and provides all analysis data (behavior, nutrition, routine, engagement) in one response.

## Database Schema

### analysis_memory Table Structure
```sql
CREATE TABLE analysis_memory (
    id uuid PRIMARY KEY,
    profile_id text NOT NULL,
    analysis_date timestamptz NOT NULL,
    analysis_type text NOT NULL,
    archetype text,
    previous_analysis_id uuid,
    behavior_analysis jsonb,
    nutrition_plan jsonb,
    routine_plan jsonb,
    user_preferences jsonb,
    health_goals jsonb,
    dietary_restrictions jsonb,
    lifestyle_context jsonb,
    medical_conditions jsonb,
    analysis_insights jsonb,
    health_trends jsonb,
    improvement_areas jsonb,
    success_patterns jsonb,
    engagement_metrics jsonb,
    performance_metrics jsonb,
    extras jsonb,
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL
);
```

## API Endpoint Design

### Single Endpoint
```
GET /api/v1/users/{user_id}/analysis-data?date={date}&limit={limit}&analysis_type={type}
```

### Query Parameters
- `date` (required): YYYY-MM-DD format - filter by analysis_date
- `limit` (optional): Maximum number of analyses (default: 10, max: 100)
- `analysis_type` (optional): Filter by "initial" or "follow_up"

### Database Query
```sql
SELECT 
    id, profile_id, analysis_date, analysis_type, archetype, 
    previous_analysis_id, behavior_analysis, nutrition_plan, 
    routine_plan, user_preferences, health_goals, dietary_restrictions,
    lifestyle_context, medical_conditions, analysis_insights, 
    health_trends, improvement_areas, success_patterns, 
    engagement_metrics, performance_metrics, extras,
    created_at, updated_at
FROM analysis_memory 
WHERE profile_id = $1 AND DATE(analysis_date) = $2
ORDER BY analysis_date DESC, created_at DESC
LIMIT $3;
```

## Response Structure

### Success Response (200)
```json
{
    "user_id": "mbzXA48h4ASzre407KoFMepfyGv1",
    "date": "2025-08-05",
    "total_analyses": 2,
    "analyses": [
        {
            "analysis_id": "da90ee32-e7c7-49c6-9784-95b778bca5a3",
            "analysis_date": "2025-08-05T14:48:03.963349+00:00",
            "analysis_type": "initial",
            "archetype": "Peak Performer",
            "previous_analysis_id": null,
            "created_at": "2025-08-05T14:48:03.963349+00:00",
            "updated_at": "2025-08-05T14:48:03.963349+00:00",
            
            "behavior_analysis": {
                "user_id": "mbzXA48h4ASzre407KoFMepfyGv1",
                "primary_goal": {
                    "goal": "Enhance daily routine consistency and improve sleep quality",
                    "timeline": "30_days",
                    "success_metrics": ["Increase routine consistency to ≥85%"]
                },
                "readiness_level": "Developing",
                "recommendations": ["Establish a fixed daily schedule"],
                "behavioral_signature": {
                    "signature": "Steady Starter",
                    "confidence": 0.8
                },
                "habit_formation_stage": "Initiation",
                "sophistication_assessment": {
                    "score": 35,
                    "category": "Developing",
                    "justification": "The data indicates moderate adherence level..."
                }
            },
            
            "nutrition_plan": {
                "fat": 52,
                "date": "2025-08-05",
                "carbs": 260,
                "protein": 130,
                "summary": "Personalized daily nutrition plan designed to enhance...",
                "calories": 2100
            },
            
            "routine_plan": {
                "date": "2025-08-06",
                "summary": "Today's routine is designed to gradually build...",
                "focus_block": "9:00 AM - 10:00 AM",
                "morning_wakeup": "6:30 AM - 7:00 AM",
                "evening_winddown": "9:00 PM - 9:30 PM",
                "afternoon_recharge": "1:00 PM - 1:30 PM"
            },
            
            "engagement_metrics": {
                "last_login": null,
                "time_spent": null,
                "user_feedback": null,
                "plan_adherence": null,
                "completion_rate": null,
                "interaction_count": null
            },
            
            "user_preferences": {},
            "health_goals": {},
            "dietary_restrictions": {},
            "lifestyle_context": {},
            "medical_conditions": {},
            "analysis_insights": {},
            "health_trends": {},
            "improvement_areas": {},
            "success_patterns": {},
            "performance_metrics": {
                "goal_progress": null,
                "health_score_change": null,
                "sleep_quality_change": null,
                "activity_level_change": null,
                "biomarker_improvements": null
            },
            "extras": {}
        }
    ]
}
```

### Error Responses

#### 400 Bad Request - Invalid Date Format
```json
{
    "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

#### 400 Bad Request - Invalid Analysis Type
```json
{
    "detail": "analysis_type must be 'initial' or 'follow_up'"
}
```

#### 404 Not Found - No Data
```json
{
    "user_id": "user123",
    "date": "2025-08-05", 
    "total_analyses": 0,
    "analyses": []
}
```

#### 500 Internal Server Error
```json
{
    "detail": "Error fetching analysis data: {error_message}"
}
```

## Implementation Components

### 1. Pydantic Models (`phase2_models.py`)
- `AnalysisRecord`: Complete analysis record with all JSON columns
- `AnalysisDataResponse`: API response wrapper

### 2. Service Method (`dashboard_service.py`)
- `get_user_analysis_data()`: Main business logic method
- Handles database querying and response transformation
- Error handling and validation

### 3. API Endpoint (`phase2_endpoints.py`)
- FastAPI route handler with parameter validation
- Date format validation
- Analysis type validation
- Error handling and HTTP status codes

### 4. Database Integration
- Direct Supabase queries via existing database service
- PostgreSQL JSONB handling for flexible JSON column support
- Proper parameterized queries for security

## Frontend Integration

### Single API Call Pattern
```typescript
// Replace 4 separate API calls with 1
const fetchAnalysisData = async (date: string) => {
    const response = await fetch(`/api/v1/users/${userId}/analysis-data?date=${date}`);
    const data = await response.json();
    
    // All tabs now have access to the complete dataset
    setBehaviorData(data.analyses.map(a => a.behavior_analysis));
    setNutritionData(data.analyses.map(a => a.nutrition_plan));
    setRoutineData(data.analyses.map(a => a.routine_plan));
    setEngagementData(data.analyses.map(a => a.engagement_metrics));
};
```

### Tab Component Updates
- Simple plain text/JSON display components
- Handle multiple analyses per day automatically
- Show analysis timestamps and types
- Graceful handling of empty JSON fields

## Benefits

### Performance Benefits
- **90% reduction in API calls** (1 vs 4 per date change)
- **Single database query** instead of multiple
- **Faster page loads** and date navigation
- **Reduced server load** and database connections

### Development Benefits
- **Simpler frontend code** - one data source for all tabs
- **Easier debugging** - complete raw data visibility
- **Future-proof** - automatically includes new JSON columns
- **Consistent data** - all tabs use same dataset timestamp

### User Experience Benefits
- **Faster date switching** with immediate data display
- **Multiple analyses per day** handled automatically
- **Complete analysis history** available
- **Raw AI output** visible for transparency

## Error Handling Strategy

### Database Errors
- Connection failures: Return 500 with generic message
- Query failures: Log detailed error, return 500
- No data found: Return 200 with empty analyses array

### Validation Errors
- Invalid date format: Return 400 with clear message
- Invalid analysis_type: Return 400 with valid options
- Invalid user_id: Return 404 or empty results

### JSON Column Handling
- Empty/null JSONB: Return empty object `{}`
- Malformed JSON: Log warning, return empty object
- Missing columns: Handle gracefully with defaults

## Testing Strategy

### API Testing
- Test with valid date and user_id
- Test with multiple analyses on same date
- Test with no analyses for date
- Test invalid date formats
- Test analysis_type filtering
- Test limit parameter boundaries

### Database Testing
- Test with empty JSONB columns
- Test with malformed JSON data
- Test with missing user_id
- Test date boundary conditions

### Integration Testing
- Test frontend date navigation
- Test tab switching with fetched data
- Test error state handling
- Test loading states

## Caching Strategy

### Cache Key Pattern
- `analysis_data:{user_id}:{date}`
- TTL: 1 hour for historical dates
- TTL: 5 minutes for current date (may be updated)

### Cache Invalidation
- Invalidate on new analysis creation for user
- Invalidate on analysis updates
- Manual cache clear option for debugging

## Future Enhancements (Phase 3+)

### Planned Features
- Date range queries (get multiple dates at once)
- Analysis comparison endpoints
- Aggregated insights across time periods
- Export functionality (CSV, PDF)
- Real-time updates via WebSocket
- Advanced filtering and search

### Scalability Considerations
- Database indexing on (profile_id, analysis_date)
- Query result pagination for high-volume users
- Response compression for large JSON payloads
- Connection pooling optimization

## Security Considerations

### Data Privacy
- User can only access their own analysis data
- No sensitive data exposed in error messages
- Audit logging for data access

### Input Validation
- SQL injection prevention via parameterized queries
- Date format validation
- User ID sanitization
- Request rate limiting

## Documentation Updates

### API Documentation
- Update OpenAPI/Swagger specs
- Add example requests and responses
- Document error codes and meanings
- Include frontend integration examples

### Developer Documentation
- Update CLAUDE.md with Phase 2 commands
- Add troubleshooting guide
- Include database query examples
- Document caching behavior