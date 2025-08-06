"""
Phase 2 API Endpoints for Analysis Data Extraction

Provides single endpoint to fetch all analysis_memory data for a user on a specific date.
Supports date filtering, analysis type filtering, and proper error handling.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging
from datetime import datetime

from ..models.phase2_models import AnalysisDataResponse, AnalysisDataError
from ..services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)

# Create router for Phase 2 endpoints
router = APIRouter(
    prefix="/api/v1",
    tags=["Phase 2: Analysis Data"],
    responses={
        400: {"model": AnalysisDataError, "description": "Invalid request parameters"},
        404: {"model": AnalysisDataResponse, "description": "No data found (returns empty analyses list)"},
        500: {"model": AnalysisDataError, "description": "Internal server error"}
    }
)


def get_dashboard_service():
    """Dependency to get dashboard service instance"""
    return DashboardService()


@router.get("/users/{user_id}/analysis-data", response_model=AnalysisDataResponse)
async def get_user_analysis_data(
    user_id: str,
    date: str = Query(..., description="Date in YYYY-MM-DD format", example="2025-08-05"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of analyses to return"),
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type", enum=["initial", "follow_up"]),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get all analysis data for a user on a specific date.
    
    Returns complete analysis_memory records with all JSON columns for the specified date.
    Handles multiple analyses per day and provides flexible filtering options.
    
    **Key Features:**
    - Single API call replaces multiple endpoint calls
    - Returns all JSON columns (behavior_analysis, nutrition_plan, routine_plan, engagement_metrics, etc.)
    - Handles multiple analyses per day automatically
    - Supports analysis type filtering (initial vs follow_up)
    - Implements intelligent caching (5 minutes for today, 1 hour for historical dates)
    - Graceful handling of empty or malformed JSON fields
    
    **Use Cases:**
    - Frontend date navigation (get all data when user switches dates)
    - Tab-based UI where each tab shows different JSON column data
    - Historical analysis review and comparison
    - Debug/admin interface to see raw AI-generated data
    
    **Example Usage:**
    ```
    GET /api/v1/users/mbzXA48h4ASzre407KoFMepfyGv1/analysis-data?date=2025-08-05
    GET /api/v1/users/user123/analysis-data?date=2025-08-05&analysis_type=initial
    GET /api/v1/users/user123/analysis-data?date=2025-08-05&limit=5
    ```
    """
    try:
        logger.info(f"Analysis data request: user={user_id}, date={date}, limit={limit}, type={analysis_type}")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format provided: {date}")
            raise HTTPException(
                status_code=400, 
                detail="Invalid date format. Use YYYY-MM-DD (e.g., 2025-08-05)"
            )
        
        # Validate analysis_type if provided
        if analysis_type and analysis_type not in ["initial", "follow_up"]:
            logger.warning(f"Invalid analysis_type provided: {analysis_type}")
            raise HTTPException(
                status_code=400, 
                detail="analysis_type must be 'initial' or 'follow_up'"
            )
        
        # Validate user_id (basic validation)
        if not user_id or not user_id.strip():
            logger.warning("Empty user_id provided")
            raise HTTPException(
                status_code=400,
                detail="user_id is required and cannot be empty"
            )
        
        # Call service to get analysis data
        try:
            result = await service.get_user_analysis_data(user_id, date, limit, analysis_type)
            
            # Log successful retrieval
            logger.info(f"Successfully retrieved {result.total_analyses} analyses for user {user_id} on {date}")
            
            return result
            
        except Exception as service_error:
            # Log the full error for debugging
            logger.error(f"Service error for user {user_id} on {date}: {str(service_error)}")
            
            # Return user-friendly error message
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving analysis data: {str(service_error)}"
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
        
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error in analysis data endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )
    
    finally:
        # Always cleanup service resources
        try:
            await service.cleanup()
        except Exception as cleanup_error:
            logger.warning(f"Error during service cleanup: {cleanup_error}")


