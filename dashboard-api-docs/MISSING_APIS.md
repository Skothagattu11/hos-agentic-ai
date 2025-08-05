# Missing API Endpoints for Bio-Coach-Hub Integration

This document provides comprehensive specifications for all missing API endpoints required to integrate bio-coach-hub frontend with health-agent-main backend.

## API Endpoint Categories

### 1. User Management APIs
### 2. Dashboard Data APIs  
### 3. Component-Specific APIs
### 4. Metrics Integration APIs
### 5. Historical Data APIs

---

## 1. USER MANAGEMENT APIs

### 1.1 List All Users
**Endpoint**: `GET /api/users`

**Purpose**: Provide user list for bio-coach-hub Index.tsx dashboard

**Input Parameters**:
```json
{
  "limit": "integer, optional, default=100, max=1000",
  "offset": "integer, optional, default=0",
  "search": "string, optional, search by name or archetype",
  "archetype": "string, optional, filter by specific archetype"
}
```

**Output Response**:
```json
{
  "users": [
    {
      "id": "string, user profile ID",
      "name": "string, user display name",
      "age": "integer, user age",
      "archetype": "string, one of 6 supported archetypes",
      "overall_score": "integer, 0-100 health score",
      "last_analysis_date": "datetime, ISO format",
      "today_metrics": {
        "steps": "integer",
        "resting_hr": "integer",
        "sleep_efficiency": "float, 0-100",
        "calories_consumed": "integer",
        "calories_burned": "integer"
      },
      "analysis_count": "integer, total analyses performed"
    }
  ],
  "total_count": "integer, total users available",
  "has_more": "boolean, whether more results exist"
}
```

**Implementation Requirements**:
- Query all unique profile_ids from analysis_memory table
- For each user, get latest analysis data
- Call hos-fapi-hm-sahha-main for today's metrics
- Combine and format response
- Add pagination support
- Implement search/filter capabilities

**Complexity**: Medium
**Dependencies**: analysis_history_manager.py, hos-fapi client integration

---

### 1.2 Get Specific User Profile
**Endpoint**: `GET /api/users/{user_id}`

**Purpose**: Provide complete user profile for bio-coach-hub UserProfile.tsx page

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "include_trends": "boolean, query parameter, default=false",
  "days": "integer, query parameter, default=30, max=365"
}
```

**Output Response**:
```json
{
  "id": "string, user profile ID",
  "name": "string, user display name", 
  "age": "integer, user age",
  "archetype": "string, current archetype",
  "overall_score": "integer, latest overall health score",
  "profile_created": "datetime, when profile was first created",
  "last_analysis": "datetime, most recent analysis",
  "analysis_summary": {
    "total_analyses": "integer",
    "initial_analyses": "integer", 
    "follow_up_analyses": "integer",
    "archetypes_used": ["string, list of archetypes used"]
  },
  "current_metrics": {
    "steps": "integer",
    "calories_consumed": "integer",
    "calories_burned": "integer", 
    "resting_hr": "integer",
    "hrv": "integer",
    "sleep_debt": "float, hours",
    "sleep_efficiency": "float, percentage",
    "routine_rating": "float, 1-5 scale"
  },
  "goals": {
    "steps": "integer, daily step goal",
    "calories": "integer, daily calorie goal"
  },
  "trends": "array, optional, included if include_trends=true, 30-day historical data"
}
```

**Implementation Requirements**:
- Validate user_id exists in analysis_memory
- Get user's latest analysis data from PostgreSQL
- Call hos-fapi-hm-sahha-main for current metrics
- Optionally include historical trends
- Handle case where user has no analysis data
- Return 404 if user doesn't exist

**Complexity**: Medium
**Dependencies**: analysis_history_manager.py, hos-fapi client, user validation

---

## 2. DASHBOARD DATA APIs

### 2.1 Complete Dashboard Data
**Endpoint**: `GET /api/users/{user_id}/dashboard`

**Purpose**: Single endpoint for bio-coach-hub to get all dashboard data in one call

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "days": "integer, query parameter, default=30, historical data range"
}
```

**Output Response**:
```json
{
  "user_profile": {
    "id": "string",
    "name": "string",
    "age": "integer", 
    "archetype": "string",
    "overall_score": "integer"
  },
  "current_metrics": {
    "steps": "integer",
    "calories_consumed": "integer", 
    "calories_burned": "integer",
    "routine_rating": "float",
    "resting_hr": "integer",
    "hrv": "integer",
    "sleep_debt": "float",
    "sleep_efficiency": "float"
  },
  "goals": {
    "steps": "integer",
    "calories": "integer"
  },
  "trends": [
    {
      "date": "string, YYYY-MM-DD",
      "steps": "integer",
      "calories_consumed": "integer",
      "calories_burned": "integer", 
      "routine_rating": "float",
      "resting_hr": "integer",
      "hrv": "integer",
      "sleep_debt": "float",
      "sleep_efficiency": "float",
      "overall_score": "integer"
    }
  ],
  "latest_analysis": {
    "analysis_date": "datetime",
    "analysis_type": "string, initial|follow_up",
    "archetype": "string",
    "has_behavior_analysis": "boolean",
    "has_nutrition_plan": "boolean", 
    "has_routine_plan": "boolean",
    "has_engagement_metrics": "boolean"
  }
}
```

**Implementation Requirements**:
- Orchestrate multiple data sources (PostgreSQL + hos-fapi-hm-sahha-main)
- Combine user profile, metrics, trends, and analysis data
- Handle missing data gracefully
- Implement caching for performance
- Ensure consistent date ranges across data sources
- Optimize for single API call from frontend

**Complexity**: High
**Dependencies**: All user management APIs, metrics integration, trends calculation

---

## 3. COMPONENT-SPECIFIC APIs

### 3.1 Behavior Analysis Data
**Endpoint**: `GET /api/users/{user_id}/behavior`

**Purpose**: Data for bio-coach-hub BehaviorAnalysis.tsx component

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "analysis_id": "string, query parameter, optional, specific analysis ID"
}
```

**Output Response**:
```json
{
  "analysis_date": "datetime, when analysis was performed",
  "analysis_type": "string, initial|follow_up",
  "consistency_score": "integer, 0-100 behavioral consistency",
  "adherence_rate": "integer, 0-100 plan adherence percentage", 
  "preferred_workout_time": "string, e.g., '6:00 AM'",
  "motivation_factors": [
    "string, list of motivation factors identified"
  ],
  "challenges": [
    "string, list of behavioral challenges identified"
  ],
  "strengths": [
    "string, list of behavioral strengths identified"
  ],
  "behavioral_patterns": {
    "workout_consistency": "float, 0-1 score",
    "nutrition_adherence": "float, 0-1 score", 
    "sleep_regularity": "float, 0-1 score",
    "stress_management": "float, 0-1 score"
  },
  "recommendations": [
    {
      "category": "string, behavior category",
      "priority": "string, high|medium|low",
      "suggestion": "string, specific recommendation",
      "confidence": "float, 0-1 AI confidence score"
    }
  ]
}
```

**Implementation Requirements**:
- Extract behavior_analysis JSON from analysis_memory table
- Parse and structure the behavior analysis data
- Handle case where no behavior analysis exists
- Provide default analysis_id (latest) if not specified
- Validate user access permissions

**Complexity**: Low-Medium
**Dependencies**: analysis_history_manager.py, JSON parsing

---

### 3.2 Engagement Analysis Data
**Endpoint**: `GET /api/users/{user_id}/engagement`

**Purpose**: Data for bio-coach-hub EngagementAnalysis.tsx component

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "days": "integer, query parameter, default=14, engagement trend period"
}
```

**Output Response**:
```json
{
  "analysis_date": "datetime",
  "app_usage_minutes": "integer, daily average app usage",
  "weekly_logins": "integer, login frequency per week",
  "feature_usage": {
    "routine_tracking": "integer, 0-100 usage percentage",
    "nutrition_logging": "integer, 0-100 usage percentage",
    "progress_reviews": "integer, 0-100 usage percentage", 
    "goal_setting": "integer, 0-100 usage percentage"
  },
  "engagement_trend": [
    {
      "date": "string, YYYY-MM-DD",
      "score": "integer, 0-100 daily engagement score"
    }
  ],
  "engagement_insights": {
    "most_used_feature": "string, feature name",
    "engagement_pattern": "string, description of usage pattern",
    "improvement_areas": ["string, list of suggested improvements"]
  }
}
```

**Implementation Requirements**:
- Extract engagement_metrics JSON from analysis_memory table
- Calculate engagement trends over specified period
- Generate engagement insights and patterns
- Handle users with limited engagement data
- Provide meaningful defaults for new users

**Complexity**: Medium
**Dependencies**: analysis_history_manager.py, trend calculation logic

---

### 3.3 Nutrition Plan Data
**Endpoint**: `GET /api/users/{user_id}/nutrition`

**Purpose**: Data for bio-coach-hub NutritionPlan.tsx component

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "analysis_id": "string, query parameter, optional, specific analysis ID"
}
```

**Output Response**:
```json
{
  "generated_date": "datetime, when plan was created",
  "analysis_type": "string, initial|follow_up",
  "daily_calorie_target": "integer, total daily calories",
  "macros": {
    "protein": "integer, percentage of total calories",
    "carbs": "integer, percentage of total calories", 
    "fats": "integer, percentage of total calories"
  },
  "meals": [
    {
      "time": "string, meal time e.g., '7:00 AM'",
      "name": "string, meal name",
      "calories": "integer, meal calories",
      "description": "string, meal description and ingredients",
      "macros": {
        "protein": "integer, grams",
        "carbs": "integer, grams",
        "fats": "integer, grams"
      }
    }
  ],
  "nutrition_guidelines": [
    "string, list of nutrition recommendations"
  ],
  "dietary_considerations": [
    "string, list of dietary restrictions or preferences"
  ],
  "hydration_target": "integer, daily water intake in ml"
}
```

**Implementation Requirements**:
- Extract nutrition_plan JSON from analysis_memory table
- Parse and structure nutrition plan data
- Calculate macro breakdowns per meal
- Handle missing nutrition plans gracefully
- Validate nutritional data consistency

**Complexity**: Low-Medium
**Dependencies**: analysis_history_manager.py, nutrition data validation

---

### 3.4 Routine Plan Data
**Endpoint**: `GET /api/users/{user_id}/routine`

**Purpose**: Data for bio-coach-hub RoutinePlan.tsx component

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "analysis_id": "string, query parameter, optional, specific analysis ID"
}
```

**Output Response**:
```json
{
  "generated_date": "datetime, when routine was created",
  "analysis_type": "string, initial|follow_up",
  "routine_type": "string, e.g., strength, cardio, mixed",
  "total_duration": "integer, total routine duration in minutes",
  "exercises": [
    {
      "name": "string, exercise name",
      "type": "string, exercise category",
      "duration": "integer, duration in minutes",
      "sets": "integer, optional, number of sets",
      "reps": "integer, optional, repetitions per set",
      "intensity": "string, Low|Moderate|High",
      "instructions": "string, detailed exercise instructions",
      "equipment": "string, required equipment or 'bodyweight'",
      "muscle_groups": ["string, list of targeted muscle groups"]
    }
  ],
  "weekly_schedule": [
    {
      "day": "string, day of week",
      "routine_type": "string, type of routine for that day",
      "duration": "integer, expected duration",
      "intensity": "string, overall intensity"
    }
  ],
  "progression_plan": [
    {
      "week": "integer, week number",
      "changes": "string, planned progression changes",
      "intensity_adjustment": "string, intensity modifications"
    }
  ],
  "recovery_guidelines": [
    "string, list of recovery recommendations"
  ]
}
```

**Implementation Requirements**:
- Extract routine_plan JSON from analysis_memory table
- Parse and structure exercise routine data
- Calculate total durations and intensity levels
- Handle different routine types and progressions
- Validate exercise data completeness

**Complexity**: Low-Medium
**Dependencies**: analysis_history_manager.py, routine data validation

---

## 4. METRICS INTEGRATION APIs

### 4.1 Raw Health Metrics
**Endpoint**: `GET /api/users/{user_id}/metrics`

**Purpose**: Get raw health metrics from hos-fapi-hm-sahha-main for MetricCards.tsx

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "date": "string, query parameter, optional, YYYY-MM-DD, default=today",
  "metric_types": "string, query parameter, optional, comma-separated list"
}
```

**Output Response**:
```json
{
  "date": "string, YYYY-MM-DD, date of metrics",
  "scores": {
    "readiness": "integer, 0-100",
    "sleep": "integer, 0-100", 
    "activity": "integer, 0-100",
    "mental_wellbeing": "integer, 0-100"
  },
  "biomarkers": {
    "steps": "integer",
    "distance": "float, kilometers",
    "calories_burned": "integer",
    "active_minutes": "integer",
    "resting_heart_rate": "integer",
    "heart_rate_variability": "integer",
    "sleep_duration": "float, hours",
    "sleep_efficiency": "float, percentage",
    "deep_sleep": "float, hours",
    "rem_sleep": "float, hours"
  },
  "archetype_scores": [
    {
      "name": "string, archetype name",
      "score": "float, archetype alignment score"
    }
  ],
  "data_completeness": {
    "scores_available": "boolean",
    "biomarkers_available": "boolean", 
    "archetypes_available": "boolean"
  }
}
```

**Implementation Requirements**:
- Implement HTTP client for hos-fapi-hm-sahha-main
- Call multiple hos-fapi endpoints to get complete metrics
- Handle missing data and partial responses
- Combine scores, biomarkers, and archetype data
- Implement error handling for external API failures
- Add response caching for performance

**Complexity**: High
**Dependencies**: HTTP client implementation, hos-fapi-hm-sahha-main integration

---

## 5. HISTORICAL DATA APIs

### 5.1 Health Trends Data
**Endpoint**: `GET /api/users/{user_id}/trends`

**Purpose**: Historical trend data for ScoreTrends.tsx and MetricsTrends.tsx components

**Input Parameters**:
```json
{
  "user_id": "string, path parameter, required",
  "start_date": "string, query parameter, optional, YYYY-MM-DD",
  "end_date": "string, query parameter, optional, YYYY-MM-DD",
  "days": "integer, query parameter, default=30, overrides date range",
  "metrics": "string, query parameter, optional, comma-separated list of metrics"
}
```

**Output Response**:
```json
{
  "date_range": {
    "start_date": "string, YYYY-MM-DD",
    "end_date": "string, YYYY-MM-DD", 
    "total_days": "integer"
  },
  "trends": [
    {
      "date": "string, YYYY-MM-DD",
      "scores": {
        "overall": "integer, 0-100",
        "readiness": "integer, 0-100",
        "sleep": "integer, 0-100",
        "activity": "integer, 0-100", 
        "mental_wellbeing": "integer, 0-100"
      },
      "metrics": {
        "steps": "integer",
        "calories_consumed": "integer",
        "calories_burned": "integer",
        "routine_rating": "float, 1-5",
        "resting_hr": "integer",
        "hrv": "integer", 
        "sleep_debt": "float",
        "sleep_efficiency": "float"
      },
      "data_quality": {
        "completeness": "float, 0-1, percentage of available data",
        "sources": ["string, list of data sources for this date"]
      }
    }
  ],
  "trend_analysis": {
    "improving_metrics": ["string, list of improving metric names"],
    "declining_metrics": ["string, list of declining metric names"],
    "stable_metrics": ["string, list of stable metric names"],
    "data_gaps": ["string, dates with missing data"]
  }
}
```

**Implementation Requirements**:
- Query historical data from both PostgreSQL and hos-fapi-hm-sahha-main
- Combine analysis scores with raw metrics over time
- Handle missing data points gracefully
- Calculate trend directions and data quality metrics
- Optimize for large date ranges
- Implement intelligent data aggregation

**Complexity**: High
**Dependencies**: Historical data queries, trend calculation algorithms, data quality assessment

---

## IMPLEMENTATION COMPLEXITY SUMMARY

### Low Complexity (1-2 days)
- `GET /api/users/{user_id}/behavior` - Extract existing JSON data
- `GET /api/users/{user_id}/nutrition` - Extract existing JSON data  
- `GET /api/users/{user_id}/routine` - Extract existing JSON data

### Medium Complexity (3-5 days)
- `GET /api/users` - User listing with aggregation
- `GET /api/users/{user_id}` - Complete user profile
- `GET /api/users/{user_id}/engagement` - Engagement analysis with trends

### High Complexity (1-2 weeks)
- `GET /api/users/{user_id}/dashboard` - Complete data orchestration
- `GET /api/users/{user_id}/metrics` - External API integration
- `GET /api/users/{user_id}/trends` - Historical data analysis

## DEPENDENCIES TO IMPLEMENT

### New Components Required
1. **HosFapiClient** - HTTP client for hos-fapi-hm-sahha-main integration
2. **UserService** - User management and data orchestration
3. **MetricsService** - Raw health metrics integration
4. **TrendsService** - Historical data analysis
5. **CacheService** - Response caching for performance

### Configuration Requirements
- hos-fapi-hm-sahha-main endpoint configuration
- Authentication/authorization for external API calls
- Caching configuration and TTL settings
- Error handling and retry policies

### Testing Requirements
- Unit tests for each new service
- Integration tests for external API calls
- End-to-end tests for complete workflows
- Performance tests for data aggregation endpoints