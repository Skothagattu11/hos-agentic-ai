from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional
import logging

from ..services.dashboard_service import DashboardService
from ..models.phase1_models import (
    UserListResponse, UserProfile, HealthCheckResponse, 
    ServiceInfoResponse, APIError
)

logger = logging.getLogger(__name__)

# Create router for Phase 1 endpoints
router = APIRouter(prefix="/api/v1", tags=["Phase 1 Dashboard"])

# Global service instance (will be replaced with proper dependency injection)
_dashboard_service: Optional[DashboardService] = None

def get_dashboard_service() -> DashboardService:
    """Dependency to get dashboard service instance"""
    global _dashboard_service
    if _dashboard_service is None:
        _dashboard_service = DashboardService()
    return _dashboard_service

@router.get("/users", response_model=UserListResponse)
async def list_users(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of users to return"),
    offset: int = Query(default=0, ge=0, description="Number of users to skip for pagination"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get paginated list of users with basic information
    
    This endpoint provides user listings for the bio-coach-hub dashboard homepage.
    It combines data from profiles, analysis_memory, and health scores tables.
    """
    try:
        logger.info(f"Listing users: limit={limit}, offset={offset}")
        
        result = await dashboard_service.list_users(limit=limit, offset=offset)
        
        logger.info(f"Successfully listed {len(result.users)} users")
        return result
        
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=APIError(
                error="internal_server_error",
                message="Failed to retrieve user list",
                details={"limit": limit, "offset": offset}
            ).dict()
        )

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str = Path(..., description="User profile ID"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get detailed user profile information
    
    This endpoint provides complete user profile data for the bio-coach-hub 
    user profile page, including analysis history and health scores.
    """
    try:
        logger.info(f"Getting user profile: {user_id}")
        
        user_profile = await dashboard_service.get_user_profile(user_id)
        
        if not user_profile:
            logger.warning(f"User profile not found: {user_id}")
            raise HTTPException(
                status_code=404,
                detail=APIError(
                    error="not_found",
                    message=f"User profile {user_id} not found",
                    details={"user_id": user_id}
                ).dict()
            )
        
        logger.info(f"Successfully retrieved user profile: {user_id}")
        return user_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=APIError(
                error="internal_server_error",
                message="Failed to retrieve user profile",
                details={"user_id": user_id}
            ).dict()
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    System health check endpoint
    
    This endpoint monitors the health of all integrated services including
    databases, external APIs, and cache performance.
    """
    try:
        logger.debug("Performing health check")
        
        health_status = await dashboard_service.health_check()
        
        # Return appropriate HTTP status based on health
        if health_status.status == "error":
            logger.error("Health check failed with error status")
            raise HTTPException(
                status_code=503,
                detail=health_status.dict()
            )
        elif health_status.status == "degraded":
            logger.warning("Health check shows degraded status")
            # Return 200 but with degraded status in response
        
        logger.info(f"Health check completed: {health_status.status}")
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing health check: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=APIError(
                error="service_unavailable",
                message="Health check failed",
                details={"error": str(e)}
            ).dict()
        )

@router.get("/info", response_model=ServiceInfoResponse)
async def get_service_info(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get service configuration and version information
    
    This endpoint provides information about the service configuration,
    enabled features, and external service connections.
    """
    try:
        logger.debug("Getting service info")
        
        service_info = dashboard_service.get_service_info()
        
        logger.debug("Successfully retrieved service info")
        return service_info
        
    except Exception as e:
        logger.error(f"Error getting service info: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=APIError(
                error="internal_server_error",
                message="Failed to retrieve service information",
                details={"error": str(e)}
            ).dict()
        )

# Additional utility endpoints for monitoring and debugging

@router.get("/cache/stats")
async def get_cache_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get cache performance statistics
    
    This endpoint provides detailed cache performance metrics for monitoring
    and debugging purposes.
    """
    try:
        logger.debug("Getting cache statistics")
        
        cache_stats = dashboard_service.cache_service.get_stats()
        
        logger.debug("Successfully retrieved cache stats")
        return {
            "cache_stats": cache_stats,
            "timestamp": dashboard_service.cache_service._cache.get("timestamp", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=APIError(
                error="internal_server_error",
                message="Failed to retrieve cache statistics",
                details={"error": str(e)}
            ).dict()
        )

@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(default=None, description="Specific cache type to clear"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Clear cache entries
    
    This endpoint allows clearing cache entries for debugging and testing.
    Use with caution in production.
    """
    try:
        logger.info(f"Clearing cache: {cache_type or 'all'}")
        
        dashboard_service.cache_service.clear_cache(cache_type)
        
        return {
            "message": f"Cache cleared: {cache_type or 'all'}",
            "timestamp": dashboard_service.cache_service._cache.get("timestamp", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=APIError(
                error="internal_server_error",
                message="Failed to clear cache",
                details={"cache_type": cache_type, "error": str(e)}
            ).dict()
        )