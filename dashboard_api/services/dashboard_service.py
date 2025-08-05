from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime

from .database_service import DatabaseService
from .cache_service import CacheService
from ..clients.hos_fapi_client import HosFapiClient
from ..models.phase1_models import (
    UserSummary, UserProfile, AnalysisSummary, HealthScores, 
    DataAvailability, UserListResponse, HealthCheckResponse,
    ServiceStatus, SystemStatistics, CachePerformance,
    ServiceInfoResponse, ExternalServices, ArchetypeEnum
)

logger = logging.getLogger(__name__)

class DashboardService:
    """Main service for dashboard API operations"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.cache_service = CacheService()
        self.hos_fapi_client = HosFapiClient()
        
        logger.info("DashboardService initialized")
    
    def _parse_health_scores(self, scores_data: Optional[Dict[str, Any]]) -> HealthScores:
        """Parse health scores from API response or database"""
        if not scores_data:
            return HealthScores()
        
        # Handle different response formats
        scores = HealthScores(
            overall=scores_data.get('overall') or scores_data.get('readiness'),  # Fallback to readiness if no overall
            readiness=scores_data.get('readiness'),
            sleep=scores_data.get('sleep'),
            activity=scores_data.get('activity'),
            mental_wellbeing=scores_data.get('mental_wellbeing')
        )
        
        return scores
    
    def _safe_archetype_parse(self, archetype_str: Optional[str]) -> Optional[ArchetypeEnum]:
        """Safely parse archetype string to enum"""
        if not archetype_str:
            return None
        
        try:
            # Try direct enum lookup
            for archetype in ArchetypeEnum:
                if archetype.value == archetype_str:
                    return archetype
            
            # If no exact match, return None
            logger.warning(f"Unknown archetype: {archetype_str}")
            return None
        except Exception as e:
            logger.error(f"Error parsing archetype {archetype_str}: {e}")
            return None
    
    async def get_user_health_scores(self, profile_id: str) -> HealthScores:
        """Get user health scores with fallback strategy"""
        # Check cache first
        cached_scores = await self.cache_service.get_user_scores(profile_id)
        if cached_scores:
            return self._parse_health_scores(cached_scores)
        
        scores_data = None
        
        # Try external API first
        try:
            logger.debug(f"Trying external API for scores: {profile_id}")
            scores_data = await self.hos_fapi_client.get_user_scores(profile_id)
            if scores_data:
                logger.debug(f"Got scores from external API for {profile_id}")
        except Exception as e:
            logger.warning(f"External API failed for scores {profile_id}: {e}")
        
        # Fallback to direct database query
        if not scores_data:
            try:
                logger.debug(f"Trying direct DB query for scores: {profile_id}")
                scores_data = await self.db_service.get_user_scores_from_supabase(profile_id)
                if scores_data:
                    logger.debug(f"Got scores from direct DB for {profile_id}")
            except Exception as e:
                logger.error(f"Direct DB query failed for scores {profile_id}: {e}")
        
        # Parse and cache result
        scores = self._parse_health_scores(scores_data)
        if scores_data:
            await self.cache_service.set_user_scores(profile_id, scores_data)
        
        return scores
    
    async def get_single_user_summary(self, profile_id: str) -> Optional[UserSummary]:
        """Get summary for a single user"""
        try:
            # Get basic profile info
            profile_data = await self.db_service.get_user_profile_from_profiles_table(profile_id)
            
            # Get analysis summary
            analysis_summary = await self.db_service.get_user_analysis_summary(profile_id)
            
            # Get health scores
            health_scores = await self.get_user_health_scores(profile_id)
            
            # Build user summary
            user_summary = UserSummary(
                id=profile_id,
                name=profile_data.get('name') if profile_data else None,
                age=profile_data.get('age') if profile_data else None,
                total_analyses=analysis_summary.get('total_analyses', 0) if analysis_summary else 0,
                last_analysis_date=analysis_summary.get('latest_analysis_date') if analysis_summary else None,
                latest_archetype=self._safe_archetype_parse(analysis_summary.get('latest_archetype')) if analysis_summary else None,
                has_health_data=any([health_scores.overall, health_scores.readiness, health_scores.sleep, health_scores.activity, health_scores.mental_wellbeing]),
                overall_score=health_scores.overall
            )
            
            return user_summary
            
        except Exception as e:
            logger.error(f"Error getting user summary for {profile_id}: {e}")
            return None
    
    async def list_users(self, limit: int = 20, offset: int = 0) -> UserListResponse:
        """Get paginated list of users"""
        try:
            # Check cache first
            cached_result = await self.cache_service.get_user_list(limit, offset)
            if cached_result:
                logger.debug(f"Returning cached user list (limit={limit}, offset={offset})")
                return UserListResponse(**cached_result)
            
            # Get all profile IDs
            all_profile_ids = await self.db_service.get_all_profile_ids()
            total_count = len(all_profile_ids)
            
            # Apply pagination
            paginated_ids = all_profile_ids[offset:offset + limit]
            
            # Process users in parallel with concurrency control
            semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
            
            async def get_user_with_semaphore(profile_id: str):
                async with semaphore:
                    return await self.get_single_user_summary(profile_id)
            
            if paginated_ids:
                tasks = [get_user_with_semaphore(profile_id) for profile_id in paginated_ids]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out exceptions and None results
                valid_users = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Failed to get user {paginated_ids[i]}: {result}")
                    elif result is not None:
                        valid_users.append(result)
            else:
                valid_users = []
            
            response = UserListResponse(
                users=valid_users,
                total_count=total_count,
                has_more=(offset + limit) < total_count
            )
            
            # Cache the result
            await self.cache_service.set_user_list(limit, offset, response.dict())
            
            logger.info(f"Retrieved {len(valid_users)} users (limit={limit}, offset={offset}, total={total_count})")
            return response
            
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return UserListResponse(users=[], total_count=0, has_more=False)
    
    async def get_user_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get detailed user profile"""
        try:
            # Check cache first
            cached_profile = await self.cache_service.get_user_profile(profile_id)
            if cached_profile:
                logger.debug(f"Returning cached user profile for {profile_id}")
                return UserProfile(**cached_profile)
            
            # Get data from multiple sources in parallel
            profile_task = self.db_service.get_user_profile_from_profiles_table(profile_id)
            analysis_task = self.db_service.get_user_analysis_summary(profile_id)
            scores_task = self.get_user_health_scores(profile_id)
            
            profile_data, analysis_summary, health_scores = await asyncio.gather(
                profile_task, analysis_task, scores_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(profile_data, Exception):
                logger.error(f"Error getting profile data for {profile_id}: {profile_data}")
                profile_data = None
            
            if isinstance(analysis_summary, Exception):
                logger.error(f"Error getting analysis summary for {profile_id}: {analysis_summary}")
                analysis_summary = None
            
            if isinstance(health_scores, Exception):
                logger.error(f"Error getting health scores for {profile_id}: {health_scores}")
                health_scores = HealthScores()
            
            # Return None if no basic profile data
            if not profile_data and not analysis_summary:
                logger.warning(f"No data found for user {profile_id}")
                return None
            
            # Build complete user profile
            user_profile = UserProfile(
                id=profile_id,
                name=profile_data.get('name') if profile_data else None,
                age=profile_data.get('age') if profile_data else None,
                profile_created=profile_data.get('created_at') if profile_data else None,
                analysis_summary=AnalysisSummary(
                    total_analyses=analysis_summary.get('total_analyses', 0) if analysis_summary else 0,
                    initial_analyses=analysis_summary.get('initial_analyses', 0) if analysis_summary else 0,
                    follow_up_analyses=analysis_summary.get('follow_up_analyses', 0) if analysis_summary else 0,
                    last_analysis_date=analysis_summary.get('latest_analysis_date') if analysis_summary else None,
                    latest_archetype=self._safe_archetype_parse(analysis_summary.get('latest_archetype')) if analysis_summary else None
                ),
                current_health_scores=health_scores,
                data_availability=DataAvailability(
                    has_analysis_data=bool(analysis_summary and analysis_summary.get('total_analyses', 0) > 0),
                    has_health_scores=any([health_scores.overall, health_scores.readiness, health_scores.sleep, health_scores.activity, health_scores.mental_wellbeing]),
                    has_biomarkers=False,  # TODO: Check biomarkers in future phases
                    last_data_update=datetime.now()  # TODO: Get actual last update time
                )
            )
            
            # Cache the result
            await self.cache_service.set_user_profile(profile_id, user_profile.dict())
            
            logger.info(f"Retrieved complete profile for user {profile_id}")
            return user_profile
            
        except Exception as e:
            logger.error(f"Error getting user profile for {profile_id}: {e}")
            return None
    
    async def health_check(self) -> HealthCheckResponse:
        """Perform comprehensive health check"""
        try:
            # Check cache first
            cached_health = await self.cache_service.get_health_check()
            if cached_health:
                logger.debug("Returning cached health check result")
                return HealthCheckResponse(**cached_health)
            
            # Test all services in parallel
            db_test_task = self.db_service.test_connections()
            api_test_task = self.hos_fapi_client.health_check()
            stats_task = self.db_service.get_total_user_counts()
            
            db_results, api_healthy, stats = await asyncio.gather(
                db_test_task, api_test_task, stats_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(db_results, Exception):
                db_results = {"supabase_database": f"error: {str(db_results)}", "analysis_memory": f"error: {str(db_results)}"}
            
            if isinstance(api_healthy, Exception):
                api_healthy = False
            
            if isinstance(stats, Exception):
                stats = {"total_users": 0, "users_with_analysis": 0, "users_with_health_data": 0}
            
            # Build health check response
            health_response = HealthCheckResponse(
                status="healthy" if all([
                    "error" not in db_results.get("supabase_database", ""),
                    "error" not in db_results.get("analysis_memory", ""),
                    api_healthy
                ]) else "degraded",
                services=ServiceStatus(
                    supabase_database=db_results.get("supabase_database", "unknown"),
                    hos_fapi_api="healthy" if api_healthy else "unhealthy",
                    analysis_memory=db_results.get("analysis_memory", "unknown")
                ),
                statistics=SystemStatistics(**stats),
                cache_performance=CachePerformance(**self.cache_service.get_stats())
            )
            
            # Cache the result
            await self.cache_service.set_health_check(health_response.dict())
            
            logger.info(f"Health check completed: {health_response.status}")
            return health_response
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return HealthCheckResponse(
                status="error",
                services=ServiceStatus(
                    supabase_database=f"error: {str(e)}",
                    hos_fapi_api="unknown",
                    analysis_memory="unknown"
                ),
                statistics=SystemStatistics(total_users=0, users_with_analysis=0, users_with_health_data=0),
                cache_performance=CachePerformance(hit_rate_percent=0, total_requests=0, cache_hits=0)
            )
    
    def get_service_info(self) -> ServiceInfoResponse:
        """Get service information"""
        import os
        
        return ServiceInfoResponse(
            environment=os.environ.get("ENVIRONMENT", "development"),
            features_enabled=[
                "basic_user_listing",
                "user_profiles",
                "health_monitoring", 
                "hybrid_data_access",
                "caching"
            ],
            external_services=ExternalServices(
                hos_fapi_url=self.hos_fapi_client.base_url,
                supabase_project=os.environ.get("SUPABASE_URL", "").split("//")[-1].split(".")[0] if os.environ.get("SUPABASE_URL") else "unknown"
            ),
            supported_archetypes=list(ArchetypeEnum)
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.hos_fapi_client.close()
            logger.info("DashboardService cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")