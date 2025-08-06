"""
Phase 3 Health Data API Endpoints
"""
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional
import logging
from datetime import datetime

from ..models.phase3_models import HealthScoresResponse, HealthBiomarkersResponse
from ..services.health_data_service import HealthDataService
from ..services.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard_api", tags=["health-data"])
health_service = HealthDataService()
cache_service = CacheService()

# Cache TTLs
SCORES_CACHE_TTL = 3600  # 1 hour
BIOMARKERS_CACHE_TTL = 7200  # 2 hours


@router.get("/health_scores/{user_id}", response_model=HealthScoresResponse)
async def get_health_scores(
    user_id: str = Path(..., description="User profile ID"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Get health scores for a user over a date range.
    
    Returns daily scores for sleep, activity, nutrition, readiness, and wellbeing.
    Missing data is represented as "--".
    """
    try:
        # Validate date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check if start_date <= end_date
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="Start date must be before or equal to end date")
        
        # Check cache
        cache_key = f"health_scores:{user_id}:{start_date}:{end_date}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for health scores: {cache_key}")
            return HealthScoresResponse(**cached_data)
        
        # Fetch from service
        logger.info(f"Fetching health scores for user {user_id} from {start_date} to {end_date}")
        scores_response = await health_service.get_health_scores(user_id, start_date, end_date)
        
        # Cache the response
        await cache_service.set(cache_key, scores_response.dict(), ttl=SCORES_CACHE_TTL)
        
        return scores_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_health_scores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health_biomarkers/{user_id}", response_model=HealthBiomarkersResponse)
async def get_health_biomarkers(
    user_id: str = Path(..., description="User profile ID"),
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """
    Get health biomarkers for a user on a specific date.
    
    Returns biomarker data including:
    - Activity: steps, calories burned
    - Readiness: resting heart rate, HRV
    - Sleep: efficiency, debt, average times
    - Daily rating: routine satisfaction
    
    Missing data is represented as "--".
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Check cache
        cache_key = f"health_biomarkers:{user_id}:{date}"
        cached_data = await cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Cache hit for health biomarkers: {cache_key}")
            return HealthBiomarkersResponse(**cached_data)
        
        # Fetch from service
        logger.info(f"Fetching health biomarkers for user {user_id} on {date}")
        biomarkers_response = await health_service.get_health_biomarkers(user_id, date)
        
        # Cache the response
        await cache_service.set(cache_key, biomarkers_response.dict(), ttl=BIOMARKERS_CACHE_TTL)
        
        return biomarkers_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_health_biomarkers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")