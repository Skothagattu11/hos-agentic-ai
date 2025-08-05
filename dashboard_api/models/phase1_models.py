from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ArchetypeEnum(str, Enum):
    """Supported health analysis archetypes"""
    FOUNDATION_BUILDER = "Foundation Builder"
    TRANSFORMATION_SEEKER = "Transformation Seeker"
    SYSTEMATIC_IMPROVER = "Systematic Improver"
    PEAK_PERFORMER = "Peak Performer"
    RESILIENCE_REBUILDER = "Resilience Rebuilder"
    CONNECTED_EXPLORER = "Connected Explorer"

class HealthScores(BaseModel):
    """Current health scores"""
    overall: Optional[int] = Field(default=None, ge=0, le=100, description="Overall health score")
    readiness: Optional[int] = Field(default=None, ge=0, le=100, description="Readiness score")
    sleep: Optional[int] = Field(default=None, ge=0, le=100, description="Sleep score")
    activity: Optional[int] = Field(default=None, ge=0, le=100, description="Activity score")
    mental_wellbeing: Optional[int] = Field(default=None, ge=0, le=100, description="Mental wellbeing score")

class AnalysisSummary(BaseModel):
    """Summary of user analysis history"""
    total_analyses: int = Field(ge=0, description="Total number of analyses")
    initial_analyses: int = Field(ge=0, description="Number of initial analyses")
    follow_up_analyses: int = Field(ge=0, description="Number of follow-up analyses")
    last_analysis_date: Optional[datetime] = Field(default=None, description="Last analysis timestamp")
    latest_archetype: Optional[ArchetypeEnum] = Field(default=None, description="Most recent archetype")

class DataAvailability(BaseModel):
    """Data availability indicators"""
    has_analysis_data: bool = Field(description="Whether user has analysis data")
    has_health_scores: bool = Field(description="Whether user has health scores")
    has_biomarkers: bool = Field(description="Whether user has biomarker data")
    last_data_update: Optional[datetime] = Field(default=None, description="Last data update timestamp")

class UserSummary(BaseModel):
    """User summary for listing endpoint"""
    id: str = Field(description="User profile ID")
    name: Optional[str] = Field(default=None, description="User display name")
    age: Optional[int] = Field(default=None, ge=1, le=150, description="User age")
    total_analyses: int = Field(ge=0, description="Total number of analyses")
    last_analysis_date: Optional[datetime] = Field(default=None, description="Last analysis timestamp")
    latest_archetype: Optional[ArchetypeEnum] = Field(default=None, description="Latest archetype")
    has_health_data: bool = Field(description="Whether user has health data available")
    overall_score: Optional[int] = Field(default=None, ge=0, le=100, description="Overall health score")

class UserProfile(BaseModel):
    """Complete user profile for individual endpoint"""
    id: str = Field(description="User profile ID")
    name: Optional[str] = Field(default=None, description="User display name")
    age: Optional[int] = Field(default=None, ge=1, le=150, description="User age")
    profile_created: Optional[datetime] = Field(default=None, description="Profile creation timestamp")
    analysis_summary: AnalysisSummary = Field(description="Analysis history summary")
    current_health_scores: HealthScores = Field(description="Current health scores")
    data_availability: DataAvailability = Field(description="Data availability status")

class UserListResponse(BaseModel):
    """Response for user listing endpoint"""
    users: List[UserSummary] = Field(description="List of user summaries")
    total_count: int = Field(ge=0, description="Total number of users")
    has_more: bool = Field(description="Whether more results exist")

class ServiceStatus(BaseModel):
    """Individual service status"""
    supabase_database: str = Field(description="Supabase database status")
    hos_fapi_api: str = Field(description="hos-fapi-hm-sahha API status")
    analysis_memory: str = Field(description="Analysis memory status")

class SystemStatistics(BaseModel):
    """System statistics"""
    total_users: int = Field(ge=0, description="Total number of users")
    users_with_analysis: int = Field(ge=0, description="Users with analysis data")
    users_with_health_data: int = Field(ge=0, description="Users with health data")

class CachePerformance(BaseModel):
    """Cache performance metrics"""
    hit_rate_percent: float = Field(ge=0, le=100, description="Cache hit rate percentage")
    total_requests: int = Field(ge=0, description="Total cache requests")
    cache_hits: int = Field(ge=0, description="Number of cache hits")

class HealthCheckResponse(BaseModel):
    """Response for health check endpoint"""
    status: str = Field(description="Overall system status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    services: ServiceStatus = Field(description="Individual service statuses")
    statistics: SystemStatistics = Field(description="System statistics")
    cache_performance: CachePerformance = Field(description="Cache performance metrics")

class ExternalServices(BaseModel):
    """External service configuration"""
    hos_fapi_url: str = Field(description="hos-fapi-hm-sahha API URL")
    supabase_project: str = Field(description="Supabase project identifier")

class ServiceInfoResponse(BaseModel):
    """Response for service info endpoint"""
    service: str = Field(default="health-agent-main-dashboard", description="Service name")
    version: str = Field(default="1.0.0-phase1", description="Service version")
    phase: str = Field(default="1", description="Implementation phase")
    environment: str = Field(description="Deployment environment")
    features_enabled: List[str] = Field(description="Enabled features")
    external_services: ExternalServices = Field(description="External service configuration")
    supported_archetypes: List[ArchetypeEnum] = Field(description="Supported analysis archetypes")

class APIError(BaseModel):
    """Standard API error response"""
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    warnings: Optional[List[str]] = Field(default=None, description="Warning messages")