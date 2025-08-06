"""
Phase 3 Health Data Models for Dashboard API
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from datetime import date


class DailyScore(BaseModel):
    """Daily health scores"""
    date: str  # YYYY-MM-DD format
    sleep: Union[int, str]  # 0-100 or "--"
    activity: Union[int, str]  # 0-100 or "--"
    nutrition: str = "--"  # Always "--" for now
    readiness: Union[int, str]  # 0-100 or "--"
    wellbeing: Union[int, str]  # 0-100 or "--"


class HealthScoresResponse(BaseModel):
    """Response model for health scores endpoint"""
    user_id: str
    scores: List[DailyScore]


class ActivityMetrics(BaseModel):
    """Activity biomarker metrics"""
    steps: Union[int, str]  # Count or "--"
    calories_burned: Union[int, str]  # kcal or "--"


class ReadinessMetrics(BaseModel):
    """Readiness biomarker metrics"""
    resting_hr: Union[int, str]  # bpm or "--"
    hrv: str = "--"  # Always "--" for now


class SleepMetrics(BaseModel):
    """Sleep biomarker metrics"""
    sleep_efficiency: Union[int, str]  # Percentage or "--"
    sleep_debt_hours: Union[float, str]  # Hours or "--"
    avg_sleep_time: Union[str, None] = None  # HH:MM format or None
    avg_wake_time: Union[str, None] = None  # HH:MM format or None


class DailyRatingMetrics(BaseModel):
    """Daily rating metrics"""
    routine_satisfaction: str = "--"  # Always "--" for now


class BiomarkersData(BaseModel):
    """All biomarker categories"""
    activity: ActivityMetrics
    readiness: ReadinessMetrics
    sleep: SleepMetrics
    daily_rating: DailyRatingMetrics


class HealthBiomarkersResponse(BaseModel):
    """Response model for health biomarkers endpoint"""
    user_id: str
    date: str  # YYYY-MM-DD format
    biomarkers: BiomarkersData