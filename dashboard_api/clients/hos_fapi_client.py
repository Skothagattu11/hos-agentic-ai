import httpx
from typing import Optional, Dict, Any
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class HosFapiClient:
    """HTTP client for hos-fapi-hm-sahha-main API"""
    
    def __init__(self):
        self.base_url = os.environ.get("HOS_FAPI_BASE_URL", "https://hos-fapi-hm-sahha.onrender.com")
        self.timeout = int(os.environ.get("HOS_FAPI_TIMEOUT", "30"))
        self.max_retries = int(os.environ.get("HOS_FAPI_MAX_RETRIES", "3"))
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info(f"HosFapiClient initialized with base_url: {self.base_url}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def get_health_metrics(self, profile_id: str, metric_type: str = "scores") -> Optional[Dict[str, Any]]:
        """Get health metrics for a user from hos-fapi-hm-sahha-main"""
        try:
            logger.debug(f"Fetching {metric_type} for user {profile_id}")
            
            response = await self.client.get(
                f"/api/v1/health-metrics/{metric_type}",
                params={"profile_id": profile_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Successfully fetched {metric_type} for user {profile_id}")
                return data
            elif response.status_code == 404:
                logger.warning(f"No {metric_type} found for user {profile_id}")
                return None
            else:
                logger.error(f"HTTP {response.status_code} getting {metric_type} for user {profile_id}: {response.text}")
                response.raise_for_status()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout getting {metric_type} for user {profile_id}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting {metric_type} for user {profile_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting {metric_type} for user {profile_id}: {e}")
            raise
    
    async def get_user_scores(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user health scores"""
        return await self.get_health_metrics(profile_id, "scores")
    
    async def get_user_biomarkers(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user biomarkers"""
        return await self.get_health_metrics(profile_id, "biomarkers")
    
    async def health_check(self) -> bool:
        """Check if hos-fapi-hm-sahha-main is accessible"""
        try:
            logger.debug("Performing health check on hos-fapi API")
            response = await self.client.get("/", timeout=10)
            is_healthy = response.status_code == 200
            logger.info(f"hos-fapi health check: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
        except Exception as e:
            logger.error(f"hos-fapi health check failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        logger.debug("HosFapiClient closed")