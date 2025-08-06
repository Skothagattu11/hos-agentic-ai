"""
Health Data Service for Phase 3 APIs
Handles data fetching and transformation from hos-fapi-hm-sahha
"""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import logging
from ..clients.hos_fapi_client import HosFapiClient
from ..models.phase3_models import (
    DailyScore, HealthScoresResponse, ActivityMetrics, ReadinessMetrics,
    SleepMetrics, DailyRatingMetrics, BiomarkersData, HealthBiomarkersResponse
)

logger = logging.getLogger(__name__)


class HealthDataService:
    """Service for fetching and transforming health data"""
    
    def __init__(self):
        self.hos_client = HosFapiClient()
    
    async def get_health_scores(self, user_id: str, start_date: str, end_date: str) -> HealthScoresResponse:
        """
        Fetch and transform health scores for date range
        
        Args:
            user_id: User profile ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            HealthScoresResponse with daily scores
        """
        try:
            # Generate list of dates in range
            dates = self._generate_date_list(start_date, end_date)
            daily_scores = []
            
            for date_str in dates:
                # Fetch overview data for each date
                overview_data = await self.hos_client.get_health_overview(user_id, date_str)
                
                # Transform to daily score
                daily_score = self._transform_to_daily_score(date_str, overview_data)
                daily_scores.append(daily_score)
            
            return HealthScoresResponse(
                user_id=user_id,
                scores=daily_scores
            )
            
        except Exception as e:
            logger.error(f"Error fetching health scores: {str(e)}")
            raise
    
    async def get_health_biomarkers(self, user_id: str, date: str) -> HealthBiomarkersResponse:
        """
        Fetch and transform health biomarkers for specific date
        
        Args:
            user_id: User profile ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            HealthBiomarkersResponse with biomarker data
        """
        try:
            # Fetch data from multiple endpoints
            activity_data = await self.hos_client.get_activity_metrics(user_id, date)
            sleep_data = await self.hos_client.get_sleep_metrics(user_id, date)
            recovery_data = await self.hos_client.get_recovery_metrics(user_id, date)
            
            # Transform to biomarkers format
            biomarkers = BiomarkersData(
                activity=self._extract_activity_metrics(activity_data),
                readiness=self._extract_readiness_metrics(recovery_data),
                sleep=self._extract_sleep_metrics(sleep_data, user_id),
                daily_rating=DailyRatingMetrics()  # Always default values
            )
            
            return HealthBiomarkersResponse(
                user_id=user_id,
                date=date,
                biomarkers=biomarkers
            )
            
        except Exception as e:
            logger.error(f"Error fetching health biomarkers: {str(e)}")
            raise
    
    def _generate_date_list(self, start_date: str, end_date: str) -> List[str]:
        """Generate list of dates between start and end (inclusive)"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return date_list
    
    def _transform_to_daily_score(self, date: str, overview_data: Dict[str, Any]) -> DailyScore:
        """Transform overview data to daily score format"""
        # Handle None data
        if not overview_data:
            return DailyScore(
                date=date,
                sleep="--",
                activity="--",
                nutrition="--",
                readiness="--",
                wellbeing="--"
            )
        
        # Extract individual scores from overview response
        sleep_score = None
        if overview_data.get("sleep_last_night") and overview_data["sleep_last_night"].get("score"):
            sleep_score = overview_data["sleep_last_night"]["score"].get("value")
        
        activity_score = None
        # Activity score might be in a different place, check the actual response structure
        
        readiness_score = None
        if overview_data.get("readiness_score"):
            readiness_score = overview_data["readiness_score"].get("value")
        
        wellbeing_score = None
        if overview_data.get("mental_wellbeing"):
            wellbeing_score = overview_data["mental_wellbeing"].get("value")
        
        return DailyScore(
            date=date,
            sleep=self._convert_score(sleep_score),
            activity="--",  # Will need to fetch from activity endpoint
            nutrition="--",  # Always unavailable
            readiness=self._convert_score(readiness_score),
            wellbeing=self._convert_score(wellbeing_score)
        )
    
    def _convert_score(self, score: Optional[float]) -> Union[int, str]:
        """Convert score from 0-1 scale to 0-100 or '--' if missing"""
        if score is None:
            return "--"
        return int(score * 100)
    
    def _extract_activity_metrics(self, activity_data: Dict[str, Any]) -> ActivityMetrics:
        """Extract activity metrics from activity data"""
        if not activity_data:
            return ActivityMetrics(steps="--", calories_burned="--")
        
        # First check if there's a 'today' field with metrics
        today_data = activity_data.get("today", {})
        steps = today_data.get("steps", "--") if today_data else "--"
        calories = today_data.get("calories_burned", "--") if today_data else "--"
        
        # If not found in today data, look in biomarkers
        if steps == "--" or calories == "--":
            biomarkers = activity_data.get("biomarkers", [])
            for biomarker in biomarkers:
                biomarker_data = biomarker.get("data", {})
                if biomarker.get("type") == "steps" and steps == "--":
                    try:
                        steps = int(float(biomarker_data.get("value", "--")))
                    except (ValueError, TypeError):
                        steps = "--"
                elif biomarker.get("type") == "active_energy_burned" and calories == "--":
                    try:
                        calories = int(float(biomarker_data.get("value", "--")))
                    except (ValueError, TypeError):
                        calories = "--"
        
        return ActivityMetrics(
            steps=steps,
            calories_burned=calories
        )
    
    def _extract_readiness_metrics(self, recovery_data: Dict[str, Any]) -> ReadinessMetrics:
        """Extract readiness metrics from recovery data"""
        if not recovery_data:
            return ReadinessMetrics(resting_hr="--", hrv="--")
        
        # Look for heart rate in vitals biomarkers
        resting_hr = "--"
        
        biomarkers = recovery_data.get("biomarkers", [])
        for biomarker in biomarkers:
            biomarker_data = biomarker.get("data", {})
            if biomarker.get("type") == "heart_rate_resting":
                try:
                    resting_hr = int(float(biomarker_data.get("value", "--")))
                except (ValueError, TypeError):
                    resting_hr = "--"
                break
        
        return ReadinessMetrics(
            resting_hr=resting_hr,
            hrv="--"  # Always unavailable
        )
    
    def _extract_sleep_metrics(self, sleep_data: Dict[str, Any], user_id: str) -> SleepMetrics:
        """Extract sleep metrics from sleep data"""
        if not sleep_data:
            return SleepMetrics(
                sleep_efficiency="--",
                sleep_debt_hours="--",
                avg_sleep_time=None,
                avg_wake_time=None
            )
        
        # Check for last_night data first
        last_night = sleep_data.get("last_night", {})
        
        # Calculate sleep efficiency
        sleep_efficiency = "--"
        if last_night and last_night.get("efficiency") is not None:
            # If efficiency is already a percentage (0-100)
            sleep_efficiency = int(last_night["efficiency"])
        elif last_night and last_night.get("score") and last_night["score"].get("value") is not None:
            # Convert score to efficiency percentage
            sleep_efficiency = int(last_night["score"]["value"] * 100)
        
        # Calculate sleep debt
        sleep_debt = "--"
        duration_hours = None
        
        if last_night and last_night.get("duration_hours") is not None:
            duration_hours = last_night["duration_hours"]
        else:
            # Look for sleep duration in biomarkers
            biomarkers = sleep_data.get("biomarkers", [])
            for biomarker in biomarkers:
                biomarker_data = biomarker.get("data", {})
                if biomarker.get("type") == "sleep_duration":
                    try:
                        duration_minutes = float(biomarker_data.get("value", 0))
                        duration_hours = duration_minutes / 60
                        break
                    except (ValueError, TypeError):
                        pass
        
        if duration_hours is not None:
            # Calculate debt as difference from 8 hours
            sleep_debt = max(0, 8 - duration_hours)
            sleep_debt = round(sleep_debt, 1)
        
        # TODO: Calculate 7-day averages for sleep/wake times
        # For now, return None (frontend will show mock data)
        
        return SleepMetrics(
            sleep_efficiency=sleep_efficiency,
            sleep_debt_hours=sleep_debt,
            avg_sleep_time=None,
            avg_wake_time=None
        )