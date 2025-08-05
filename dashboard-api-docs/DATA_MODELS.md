# Data Models for Dashboard APIs

This document defines all Pydantic models required for the dashboard API endpoints. These models ensure type safety, data validation, and consistent API responses.

## Model Categories

### 1. Request Models
### 2. Response Models  
### 3. Component Models
### 4. Integration Models
### 5. Error Models

---

## 1. REQUEST MODELS

### 1.1 Query Parameter Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class UserListParams(BaseModel):
    """Query parameters for GET /api/users"""
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of users to return")
    offset: int = Field(default=0, ge=0, description="Number of users to skip")
    search: Optional[str] = Field(default=None, max_length=100, description="Search by name or archetype")
    archetype: Optional[str] = Field(default=None, description="Filter by specific archetype")
    
    @validator('search')
    def validate_search(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Search term must be at least 2 characters')
        return v.strip() if v else None

class UserProfileParams(BaseModel):
    """Query parameters for GET /api/users/{user_id}"""
    include_trends: bool = Field(default=False, description="Include historical trend data")
    days: int = Field(default=30, ge=1, le=365, description="Number of days for trend data")

class DashboardParams(BaseModel):
    """Query parameters for GET /api/users/{user_id}/dashboard"""
    days: int = Field(default=30, ge=1, le=365, description="Historical data range in days")

class TrendsParams(BaseModel):
    """Query parameters for GET /api/users/{user_id}/trends"""
    start_date: Optional[date] = Field(default=None, description="Start date for trend data")
    end_date: Optional[date] = Field(default=None, description="End date for trend data")
    days: int = Field(default=30, ge=1, le=365, description="Number of days (overrides date range)")
    metrics: Optional[str] = Field(default=None, description="Comma-separated list of metrics")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v

class MetricsParams(BaseModel):
    """Query parameters for GET /api/users/{user_id}/metrics"""
    date: Optional[date] = Field(default=None, description="Specific date for metrics")
    metric_types: Optional[str] = Field(default=None, description="Comma-separated list of metric types")

class EngagementParams(BaseModel):
    """Query parameters for GET /api/users/{user_id}/engagement"""
    days: int = Field(default=14, ge=1, le=90, description="Engagement trend period in days")
```

---

## 2. RESPONSE MODELS

### 2.1 Core User Models

```python
class ArchetypeEnum(str, Enum):
    """Supported health analysis archetypes"""
    FOUNDATION_BUILDER = "Foundation Builder"
    TRANSFORMATION_SEEKER = "Transformation Seeker"
    SYSTEMATIC_IMPROVER = "Systematic Improver"
    PEAK_PERFORMER = "Peak Performer"
    RESILIENCE_REBUILDER = "Resilience Rebuilder"
    CONNECTED_EXPLORER = "Connected Explorer"

class AnalysisTypeEnum(str, Enum):
    """Analysis types"""
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"

class TodayMetrics(BaseModel):
    """Current day health metrics"""
    steps: int = Field(description="Daily step count")
    resting_hr: int = Field(description="Resting heart rate in BPM")
    sleep_efficiency: float = Field(ge=0, le=100, description="Sleep efficiency percentage")
    calories_consumed: int = Field(ge=0, description="Calories consumed today")
    calories_burned: int = Field(ge=0, description="Calories burned today")
    routine_rating: Optional[float] = Field(default=None, ge=1, le=5, description="Daily routine rating")

class UserSummary(BaseModel):
    """User summary for user listing"""
    id: str = Field(description="User profile ID")
    name: str = Field(description="User display name")
    age: int = Field(ge=1, le=150, description="User age")
    archetype: ArchetypeEnum = Field(description="Current health archetype")
    overall_score: int = Field(ge=0, le=100, description="Overall health score")
    last_analysis_date: datetime = Field(description="Most recent analysis timestamp")
    today_metrics: TodayMetrics = Field(description="Today's health metrics")
    analysis_count: int = Field(ge=0, description="Total number of analyses performed")

class UserListResponse(BaseModel):
    """Response for GET /api/users"""
    users: List[UserSummary] = Field(description="List of user summaries")
    total_count: int = Field(ge=0, description="Total number of users available")
    has_more: bool = Field(description="Whether more results exist")

class Goals(BaseModel):
    """User health goals"""
    steps: int = Field(ge=0, description="Daily step goal")
    calories: int = Field(ge=0, description="Daily calorie goal")

class AnalysisSummary(BaseModel):
    """Summary of user's analysis history"""
    total_analyses: int = Field(ge=0, description="Total number of analyses")
    initial_analyses: int = Field(ge=0, description="Number of initial analyses")
    follow_up_analyses: int = Field(ge=0, description="Number of follow-up analyses")
    archetypes_used: List[str] = Field(description="List of archetypes used in analyses")

class CurrentMetrics(BaseModel):
    """Current health metrics from external sources"""
    steps: int = Field(description="Current daily steps")
    calories_consumed: int = Field(description="Calories consumed today")
    calories_burned: int = Field(description="Calories burned today")
    resting_hr: int = Field(description="Current resting heart rate")
    hrv: int = Field(description="Heart rate variability")
    sleep_debt: float = Field(ge=0, description="Sleep debt in hours")
    sleep_efficiency: float = Field(ge=0, le=100, description="Sleep efficiency percentage")
    routine_rating: Optional[float] = Field(default=None, ge=1, le=5, description="Routine adherence rating")

class UserProfile(BaseModel):
    """Complete user profile response"""
    id: str = Field(description="User profile ID")
    name: str = Field(description="User display name")
    age: int = Field(ge=1, le=150, description="User age")
    archetype: ArchetypeEnum = Field(description="Current health archetype")
    overall_score: int = Field(ge=0, le=100, description="Latest overall health score")
    profile_created: datetime = Field(description="Profile creation timestamp")
    last_analysis: datetime = Field(description="Most recent analysis timestamp")
    analysis_summary: AnalysisSummary = Field(description="Analysis history summary")
    current_metrics: CurrentMetrics = Field(description="Current health metrics")
    goals: Goals = Field(description="User health goals")
    trends: Optional[List['TrendDataPoint']] = Field(default=None, description="Historical trend data")
```

---

## 3. COMPONENT MODELS

### 3.1 Behavior Analysis Models

```python
class BehavioralPatterns(BaseModel):
    """Behavioral pattern scores"""
    workout_consistency: float = Field(ge=0, le=1, description="Workout consistency score")
    nutrition_adherence: float = Field(ge=0, le=1, description="Nutrition adherence score")
    sleep_regularity: float = Field(ge=0, le=1, description="Sleep regularity score")
    stress_management: float = Field(ge=0, le=1, description="Stress management score")

class RecommendationPriority(str, Enum):
    """Recommendation priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BehaviorRecommendation(BaseModel):
    """Individual behavior recommendation"""
    category: str = Field(description="Behavior category")
    priority: RecommendationPriority = Field(description="Recommendation priority")
    suggestion: str = Field(description="Specific recommendation text")
    confidence: float = Field(ge=0, le=1, description="AI confidence score")

class BehaviorAnalysisResponse(BaseModel):
    """Response for GET /api/users/{user_id}/behavior"""
    analysis_date: datetime = Field(description="When analysis was performed")
    analysis_type: AnalysisTypeEnum = Field(description="Type of analysis")
    consistency_score: int = Field(ge=0, le=100, description="Behavioral consistency score")
    adherence_rate: int = Field(ge=0, le=100, description="Plan adherence percentage")
    preferred_workout_time: str = Field(description="Preferred workout time")
    motivation_factors: List[str] = Field(description="Identified motivation factors")
    challenges: List[str] = Field(description="Identified behavioral challenges")
    strengths: List[str] = Field(description="Identified behavioral strengths")
    behavioral_patterns: BehavioralPatterns = Field(description="Behavioral pattern scores")
    recommendations: List[BehaviorRecommendation] = Field(description="Behavior recommendations")
```

### 3.2 Engagement Analysis Models

```python
class FeatureUsage(BaseModel):
    """App feature usage statistics"""
    routine_tracking: int = Field(ge=0, le=100, description="Routine tracking usage percentage")
    nutrition_logging: int = Field(ge=0, le=100, description="Nutrition logging usage percentage")
    progress_reviews: int = Field(ge=0, le=100, description="Progress reviews usage percentage")
    goal_setting: int = Field(ge=0, le=100, description="Goal setting usage percentage")

class EngagementTrendPoint(BaseModel):
    """Single engagement trend data point"""
    date: date = Field(description="Date of engagement data")
    score: int = Field(ge=0, le=100, description="Daily engagement score")

class EngagementInsights(BaseModel):
    """Engagement pattern insights"""
    most_used_feature: str = Field(description="Most frequently used feature")
    engagement_pattern: str = Field(description="Description of usage pattern")
    improvement_areas: List[str] = Field(description="Suggested improvement areas")

class EngagementAnalysisResponse(BaseModel):
    """Response for GET /api/users/{user_id}/engagement"""
    analysis_date: datetime = Field(description="Analysis timestamp")
    app_usage_minutes: int = Field(ge=0, description="Daily average app usage in minutes")
    weekly_logins: int = Field(ge=0, description="Login frequency per week")
    feature_usage: FeatureUsage = Field(description="Feature usage statistics")
    engagement_trend: List[EngagementTrendPoint] = Field(description="Engagement trend data")
    engagement_insights: EngagementInsights = Field(description="Engagement insights")
```

### 3.3 Nutrition Plan Models

```python
class MacroNutrients(BaseModel):
    """Macro nutrient breakdown"""
    protein: int = Field(ge=0, le=100, description="Protein percentage of total calories")
    carbs: int = Field(ge=0, le=100, description="Carbohydrates percentage")
    fats: int = Field(ge=0, le=100, description="Fats percentage")
    
    @validator('fats')
    def validate_macro_total(cls, v, values):
        total = v + values.get('protein', 0) + values.get('carbs', 0)
        if abs(total - 100) > 1:  # Allow 1% tolerance for rounding
            raise ValueError('Macro nutrients must sum to approximately 100%')
        return v

class MealMacros(BaseModel):
    """Macro nutrients in grams for a meal"""
    protein: int = Field(ge=0, description="Protein in grams")
    carbs: int = Field(ge=0, description="Carbohydrates in grams")
    fats: int = Field(ge=0, description="Fats in grams")

class Meal(BaseModel):
    """Individual meal information"""
    time: str = Field(description="Meal time (e.g., '7:00 AM')")
    name: str = Field(description="Meal name")
    calories: int = Field(ge=0, description="Meal calories")
    description: str = Field(description="Meal description and ingredients")
    macros: MealMacros = Field(description="Meal macro nutrients in grams")

class NutritionPlanResponse(BaseModel):
    """Response for GET /api/users/{user_id}/nutrition"""
    generated_date: datetime = Field(description="When plan was created")
    analysis_type: AnalysisTypeEnum = Field(description="Type of analysis")
    daily_calorie_target: int = Field(ge=0, description="Total daily calorie target")
    macros: MacroNutrients = Field(description="Daily macro nutrient percentages")
    meals: List[Meal] = Field(description="Daily meal plan")
    nutrition_guidelines: List[str] = Field(description="Nutrition recommendations")
    dietary_considerations: List[str] = Field(description="Dietary restrictions or preferences")
    hydration_target: int = Field(ge=0, description="Daily water intake target in ml")
```

### 3.4 Routine Plan Models

```python
class IntensityLevel(str, Enum):
    """Exercise intensity levels"""
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class Exercise(BaseModel):
    """Individual exercise information"""
    name: str = Field(description="Exercise name")
    type: str = Field(description="Exercise category")
    duration: int = Field(ge=0, description="Duration in minutes")
    sets: Optional[int] = Field(default=None, ge=1, description="Number of sets")
    reps: Optional[int] = Field(default=None, ge=1, description="Repetitions per set")
    intensity: IntensityLevel = Field(description="Exercise intensity level")
    instructions: str = Field(description="Detailed exercise instructions")
    equipment: str = Field(description="Required equipment or 'bodyweight'")
    muscle_groups: List[str] = Field(description="Targeted muscle groups")

class WeeklyScheduleDay(BaseModel):
    """Weekly schedule for a single day"""
    day: str = Field(description="Day of the week")
    routine_type: str = Field(description="Type of routine for the day")
    duration: int = Field(ge=0, description="Expected duration in minutes")
    intensity: IntensityLevel = Field(description="Overall intensity level")

class ProgressionWeek(BaseModel):
    """Weekly progression plan"""
    week: int = Field(ge=1, description="Week number")
    changes: str = Field(description="Planned progression changes")
    intensity_adjustment: str = Field(description="Intensity modifications")

class RoutinePlanResponse(BaseModel):
    """Response for GET /api/users/{user_id}/routine"""
    generated_date: datetime = Field(description="When routine was created")
    analysis_type: AnalysisTypeEnum = Field(description="Type of analysis")
    routine_type: str = Field(description="Overall routine type")
    total_duration: int = Field(ge=0, description="Total routine duration in minutes")
    exercises: List[Exercise] = Field(description="Exercise list")
    weekly_schedule: List[WeeklyScheduleDay] = Field(description="Weekly workout schedule")
    progression_plan: List[ProgressionWeek] = Field(description="Progression planning")
    recovery_guidelines: List[str] = Field(description="Recovery recommendations")
```

---

## 4. INTEGRATION MODELS

### 4.1 Health Metrics Models

```python
class HealthScores(BaseModel):
    """Health scores from external API"""
    readiness: int = Field(ge=0, le=100, description="Readiness score")
    sleep: int = Field(ge=0, le=100, description="Sleep quality score")
    activity: int = Field(ge=0, le=100, description="Activity score")
    mental_wellbeing: int = Field(ge=0, le=100, description="Mental wellbeing score")

class Biomarkers(BaseModel):
    """Biomarker data from external API"""
    steps: int = Field(ge=0, description="Daily step count")
    distance: float = Field(ge=0, description="Distance in kilometers")
    calories_burned: int = Field(ge=0, description="Calories burned")
    active_minutes: int = Field(ge=0, description="Active minutes")
    resting_heart_rate: int = Field(ge=0, description="Resting heart rate")
    heart_rate_variability: int = Field(ge=0, description="HRV in milliseconds")
    sleep_duration: float = Field(ge=0, description="Sleep duration in hours")
    sleep_efficiency: float = Field(ge=0, le=100, description="Sleep efficiency percentage")
    deep_sleep: float = Field(ge=0, description="Deep sleep duration in hours")
    rem_sleep: float = Field(ge=0, description="REM sleep duration in hours")

class ArchetypeScore(BaseModel):
    """Individual archetype alignment score"""
    name: str = Field(description="Archetype name")
    score: float = Field(ge=0, le=1, description="Alignment score")

class DataCompleteness(BaseModel):
    """Data availability indicators"""
    scores_available: bool = Field(description="Whether health scores are available")
    biomarkers_available: bool = Field(description="Whether biomarkers are available")
    archetypes_available: bool = Field(description="Whether archetype data is available")

class HealthMetricsResponse(BaseModel):
    """Response for GET /api/users/{user_id}/metrics"""
    date: date = Field(description="Date of metrics")
    scores: HealthScores = Field(description="Health scores")
    biomarkers: Biomarkers = Field(description="Biomarker measurements")
    archetype_scores: List[ArchetypeScore] = Field(description="Archetype alignment scores")
    data_completeness: DataCompleteness = Field(description="Data availability indicators")
```

### 4.2 Trend Analysis Models

```python
class TrendScores(BaseModel):
    """Health scores for trend analysis"""
    overall: int = Field(ge=0, le=100, description="Overall health score")
    readiness: int = Field(ge=0, le=100, description="Readiness score")
    sleep: int = Field(ge=0, le=100, description="Sleep score")
    activity: int = Field(ge=0, le=100, description="Activity score")
    mental_wellbeing: int = Field(ge=0, le=100, description="Mental wellbeing score")

class TrendMetrics(BaseModel):
    """Health metrics for trend analysis"""
    steps: int = Field(ge=0, description="Daily steps")
    calories_consumed: int = Field(ge=0, description="Calories consumed")
    calories_burned: int = Field(ge=0, description="Calories burned")
    routine_rating: Optional[float] = Field(default=None, ge=1, le=5, description="Routine rating")
    resting_hr: int = Field(ge=0, description="Resting heart rate")
    hrv: int = Field(ge=0, description="Heart rate variability")
    sleep_debt: float = Field(ge=0, description="Sleep debt in hours")
    sleep_efficiency: float = Field(ge=0, le=100, description="Sleep efficiency")

class DataQuality(BaseModel):
    """Data quality indicators for trend point"""
    completeness: float = Field(ge=0, le=1, description="Data completeness percentage")
    sources: List[str] = Field(description="Data sources for this date")

class TrendDataPoint(BaseModel):
    """Single data point in trend analysis"""
    date: date = Field(description="Date of data point")
    scores: TrendScores = Field(description="Health scores for the date")
    metrics: TrendMetrics = Field(description="Health metrics for the date")
    data_quality: DataQuality = Field(description="Data quality indicators")

class DateRange(BaseModel):
    """Date range for trend analysis"""
    start_date: date = Field(description="Start date of trend data")
    end_date: date = Field(description="End date of trend data")
    total_days: int = Field(ge=0, description="Total days in range")

class TrendAnalysis(BaseModel):
    """Trend analysis summary"""
    improving_metrics: List[str] = Field(description="Metrics showing improvement")
    declining_metrics: List[str] = Field(description="Metrics showing decline")
    stable_metrics: List[str] = Field(description="Stable metrics")
    data_gaps: List[date] = Field(description="Dates with missing data")

class TrendsResponse(BaseModel):
    """Response for GET /api/users/{user_id}/trends"""
    date_range: DateRange = Field(description="Date range of trend data")
    trends: List[TrendDataPoint] = Field(description="Trend data points")
    trend_analysis: TrendAnalysis = Field(description="Trend analysis summary")
```

### 4.3 Dashboard Integration Models

```python
class LatestAnalysis(BaseModel):
    """Latest analysis summary for dashboard"""
    analysis_date: datetime = Field(description="Analysis timestamp")
    analysis_type: AnalysisTypeEnum = Field(description="Type of analysis")
    archetype: ArchetypeEnum = Field(description="Analysis archetype")
    has_behavior_analysis: bool = Field(description="Whether behavior analysis exists")
    has_nutrition_plan: bool = Field(description="Whether nutrition plan exists")
    has_routine_plan: bool = Field(description="Whether routine plan exists")
    has_engagement_metrics: bool = Field(description="Whether engagement metrics exist")

class DashboardUserProfile(BaseModel):
    """User profile summary for dashboard"""
    id: str = Field(description="User profile ID")
    name: str = Field(description="User display name")
    age: int = Field(ge=1, le=150, description="User age")
    archetype: ArchetypeEnum = Field(description="Current archetype")
    overall_score: int = Field(ge=0, le=100, description="Overall health score")

class DashboardResponse(BaseModel):
    """Response for GET /api/users/{user_id}/dashboard"""
    user_profile: DashboardUserProfile = Field(description="User profile summary")
    current_metrics: CurrentMetrics = Field(description="Current health metrics")
    goals: Goals = Field(description="User health goals")
    trends: List[TrendDataPoint] = Field(description="Historical trend data")
    latest_analysis: Optional[LatestAnalysis] = Field(default=None, description="Latest analysis summary")
```

---

## 5. ERROR MODELS

### 5.1 Error Response Models

```python
class ErrorDetail(BaseModel):
    """Individual error detail"""
    field: Optional[str] = Field(default=None, description="Field that caused the error")
    message: str = Field(description="Error message")
    code: str = Field(description="Error code")

class APIError(BaseModel):
    """Standard API error response"""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")

class ValidationError(APIError):
    """Validation error response"""
    error: str = Field(default="validation_error", description="Error type")

class NotFoundError(APIError):
    """Resource not found error"""
    error: str = Field(default="not_found", description="Error type")
    resource_type: str = Field(description="Type of resource not found")
    resource_id: str = Field(description="ID of resource not found")

class ExternalAPIError(APIError):
    """External API integration error"""
    error: str = Field(default="external_api_error", description="Error type")
    service: str = Field(description="External service name")
    status_code: Optional[int] = Field(default=None, description="HTTP status code from external service")

class InternalServerError(APIError):
    """Internal server error"""
    error: str = Field(default="internal_server_error", description="Error type")
```

---

## 6. UTILITY MODELS

### 6.1 Common Base Models

```python
class TimestampMixin(BaseModel):
    """Mixin for models that need timestamps"""
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class PaginationMixin(BaseModel):
    """Mixin for paginated responses"""
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Number of items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")
    total_items: int = Field(ge=0, description="Total number of items")

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(default=True, description="Whether the request was successful")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")
```

### 6.2 Configuration Models

```python
class APIConfig(BaseModel):
    """API configuration model"""
    hos_fapi_base_url: str = Field(description="Base URL for hos-fapi-hm-sahha-main")
    hos_fapi_timeout: int = Field(default=30, description="Timeout for hos-fapi calls")
    cache_ttl_user_profile: int = Field(default=900, description="User profile cache TTL in seconds")
    cache_ttl_dashboard: int = Field(default=300, description="Dashboard cache TTL in seconds")
    cache_ttl_trends: int = Field(default=3600, description="Trends cache TTL in seconds")
    max_concurrent_requests: int = Field(default=10, description="Max concurrent external API requests")
```

---

## MODEL USAGE EXAMPLES

### Request Validation Example
```python
from fastapi import HTTPException
from pydantic import ValidationError

@app.get("/api/users", response_model=UserListResponse)
async def list_users(params: UserListParams = Depends()):
    try:
        # Parameters are automatically validated by Pydantic
        users = await user_service.list_users(params)
        return users
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
```

### Response Serialization Example
```python
@app.get("/api/users/{user_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: str, params: DashboardParams = Depends()):
    dashboard_data = await user_service.get_dashboard_data(user_id, params.days)
    return DashboardResponse(**dashboard_data)
```

### Error Handling Example
```python
from fastapi import HTTPException

async def get_user_profile(user_id: str):
    try:
        profile = await user_service.get_user(user_id)
        return profile
    except UserNotFoundError:
        error = NotFoundError(
            message=f"User with ID {user_id} not found",
            resource_type="user",
            resource_id=user_id
        )
        raise HTTPException(status_code=404, detail=error.dict())
    except ExternalAPIException as e:
        error = ExternalAPIError(
            message="Failed to fetch user metrics",
            service="hos-fapi-hm-sahha-main",
            status_code=e.status_code
        )
        raise HTTPException(status_code=503, detail=error.dict())
```

## Model Registration

All models should be registered in a central `dashboard_models.py` file:

```python
# health_agents/dashboard_models.py
from .models import *

# Export all models for easy importing
__all__ = [
    # Request models
    'UserListParams', 'UserProfileParams', 'DashboardParams', 'TrendsParams', 'MetricsParams', 'EngagementParams',
    
    # Response models
    'UserListResponse', 'UserProfile', 'DashboardResponse', 'TrendsResponse', 'HealthMetricsResponse',
    
    # Component models
    'BehaviorAnalysisResponse', 'EngagementAnalysisResponse', 'NutritionPlanResponse', 'RoutinePlanResponse',
    
    # Error models
    'APIError', 'ValidationError', 'NotFoundError', 'ExternalAPIError', 'InternalServerError',
    
    # Utility models
    'BaseResponse', 'APIConfig'
]
```