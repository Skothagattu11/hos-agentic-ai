"""
Phase 2 Models for Analysis Data API

Pydantic models for handling analysis_memory table data extraction.
Supports all JSONB columns with flexible Dict[str, Any] typing.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalysisRecord(BaseModel):
    """
    Complete analysis record from analysis_memory table.
    Includes all metadata and JSON columns.
    """
    analysis_id: str = Field(..., description="Unique analysis identifier")
    analysis_date: datetime = Field(..., description="When the analysis was performed")
    analysis_type: str = Field(..., description="Type of analysis (initial/follow_up)")
    archetype: Optional[str] = Field(None, description="Health archetype used")
    previous_analysis_id: Optional[str] = Field(None, description="Previous analysis reference")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")
    
    # Core analysis JSON columns - primary focus for Phase 2
    behavior_analysis: Dict[str, Any] = Field(default_factory=dict, description="Behavior analysis JSON data")
    nutrition_plan: Dict[str, Any] = Field(default_factory=dict, description="Nutrition plan JSON data")
    routine_plan: Dict[str, Any] = Field(default_factory=dict, description="Routine plan JSON data")
    engagement_metrics: Dict[str, Any] = Field(default_factory=dict, description="Engagement metrics JSON data")
    
    # Additional JSON columns - flexible structure for future use
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences JSON data")
    health_goals: Dict[str, Any] = Field(default_factory=dict, description="Health goals JSON data")
    dietary_restrictions: Dict[str, Any] = Field(default_factory=dict, description="Dietary restrictions JSON data")
    lifestyle_context: Dict[str, Any] = Field(default_factory=dict, description="Lifestyle context JSON data")
    medical_conditions: Dict[str, Any] = Field(default_factory=dict, description="Medical conditions JSON data")
    analysis_insights: Dict[str, Any] = Field(default_factory=dict, description="Analysis insights JSON data")
    health_trends: Dict[str, Any] = Field(default_factory=dict, description="Health trends JSON data")
    improvement_areas: Dict[str, Any] = Field(default_factory=dict, description="Improvement areas JSON data")
    success_patterns: Dict[str, Any] = Field(default_factory=dict, description="Success patterns JSON data")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics JSON data")
    extras: Dict[str, Any] = Field(default_factory=dict, description="Additional data JSON field")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisDataResponse(BaseModel):
    """
    API response model for user analysis data.
    Contains all analyses for a specific user and date.
    """
    user_id: str = Field(..., description="User profile ID")
    date: str = Field(..., description="Requested date in YYYY-MM-DD format")
    total_analyses: int = Field(..., description="Number of analyses found for the date")
    analyses: List[AnalysisRecord] = Field(..., description="List of analysis records")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "mbzXA48h4ASzre407KoFMepfyGv1",
                "date": "2025-08-05",
                "total_analyses": 2,
                "analyses": [
                    {
                        "analysis_id": "da90ee32-e7c7-49c6-9784-95b778bca5a3",
                        "analysis_date": "2025-08-05T14:48:03.963349+00:00",
                        "analysis_type": "initial",
                        "archetype": "Peak Performer",
                        "previous_analysis_id": None,
                        "created_at": "2025-08-05T14:48:03.963349+00:00",
                        "updated_at": "2025-08-05T14:48:03.963349+00:00",
                        "behavior_analysis": {
                            "user_id": "mbzXA48h4ASzre407KoFMepfyGv1",
                            "primary_goal": {
                                "goal": "Enhance daily routine consistency and improve sleep quality",
                                "timeline": "30_days",
                                "success_metrics": ["Increase routine consistency to ≥85%"]
                            },
                            "readiness_level": "Developing"
                        },
                        "nutrition_plan": {
                            "fat": 52,
                            "date": "2025-08-05",
                            "carbs": 260,
                            "protein": 130,
                            "calories": 2100
                        },
                        "routine_plan": {
                            "date": "2025-08-06",
                            "summary": "Today's routine is designed to gradually build...",
                            "focus_block": "9:00 AM - 10:00 AM"
                        },
                        "engagement_metrics": {
                            "last_login": None,
                            "completion_rate": None
                        }
                    }
                ]
            }
        }


class AnalysisDataError(BaseModel):
    """
    Error response model for analysis data API.
    """
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    date: Optional[str] = Field(None, description="Date if applicable")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid date format. Use YYYY-MM-DD",
                "user_id": "user123",
                "date": "invalid-date"
            }
        }