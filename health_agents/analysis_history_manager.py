import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncpg
from .connection_factory import smart_connect
from .nutrition_plan_agent import NutritionPlanResult
from .routine_plan_agent import RoutinePlanResult
from .behavior_analysis_agent import BehaviorAnalysisResult

@dataclass
class AnalysisRecord:
    """Analysis record data structure"""
    id: str
    profile_id: str
    analysis_date: datetime
    analysis_type: str
    archetype: str
    previous_analysis_id: Optional[str]
    behavior_analysis: Optional[Dict[str, Any]]
    nutrition_plan: Optional[Dict[str, Any]]
    routine_plan: Optional[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    health_goals: Dict[str, Any]
    dietary_restrictions: Dict[str, Any]
    lifestyle_context: Dict[str, Any]
    medical_conditions: Dict[str, Any]
    analysis_insights: Dict[str, Any]
    health_trends: Dict[str, Any]
    improvement_areas: Dict[str, Any]
    success_patterns: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    extras: Dict[str, Any]

class AnalysisHistoryManager:
    """Manages analysis history using the new analysis_memory table"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self.connection = None
    
    def _serialize_for_json(self, obj: Any) -> str:
        """Helper function to serialize objects to JSON, handling datetime objects"""
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
        
        return json.dumps(obj, default=datetime_handler)
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = await smart_connect(self.database_url)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
    
    async def get_latest_analysis(self, profile_id: str) -> Optional[AnalysisRecord]:
        """Get the most recent analysis for a profile (for memory context)"""
        if not self.connection:
            await self.connect()
        
        try:
            # Use direct Supabase client instead of broken adapter
            result = self.connection.client.table('analysis_memory').select('*').eq('profile_id', profile_id).order('analysis_date', desc=True).limit(1).execute()
            
            if not result.data:
                return None
                
            row = result.data[0]
            
            return AnalysisRecord(
                id=str(row['id']),
                profile_id=row['profile_id'],
                analysis_date=row['analysis_date'],
                analysis_type=row['analysis_type'],
                archetype=row['archetype'],
                previous_analysis_id=str(row['previous_analysis_id']) if row['previous_analysis_id'] else None,
                behavior_analysis=row['behavior_analysis'] or {},
                nutrition_plan=row['nutrition_plan'] or {},
                routine_plan=row['routine_plan'] or {},
                user_preferences=row['user_preferences'] or {},
                health_goals=row['health_goals'] or {},
                dietary_restrictions=row['dietary_restrictions'] or {},
                lifestyle_context=row['lifestyle_context'] or {},
                medical_conditions=row['medical_conditions'] or {},
                analysis_insights=row['analysis_insights'] or {},
                health_trends=row['health_trends'] or {},
                improvement_areas=row['improvement_areas'] or {},
                success_patterns=row['success_patterns'] or {},
                engagement_metrics=row['engagement_metrics'] or {},
                performance_metrics=row['performance_metrics'] or {},
                extras=row['extras'] or {}
            )
            
        except Exception as e:
            print(f"Error retrieving latest analysis: {e}")
            return None
    
    async def create_analysis_record(self, 
                                   profile_id: str,
                                   archetype: str,
                                   behavior_analysis: BehaviorAnalysisResult = None,
                                   nutrition_plan: NutritionPlanResult = None,
                                   routine_plan: RoutinePlanResult = None,
                                   user_context = None) -> str:
        """Create a new analysis record and return its ID"""
        if not self.connection:
            await self.connect()
        
        try:
            # Get previous analysis for memory chain
            previous_analysis = await self.get_latest_analysis(profile_id)
            previous_analysis_id = previous_analysis.id if previous_analysis else None
            
            # Determine analysis type
            analysis_type = "follow_up" if previous_analysis else "initial"
            
            # Convert analysis results to JSON
            behavior_json = self._convert_behavior_analysis(behavior_analysis) if behavior_analysis else None
            nutrition_json = self._convert_nutrition_plan(nutrition_plan) if nutrition_plan else None
            routine_json = self._convert_routine_plan(routine_plan) if routine_plan else None
            
            # Use direct Supabase client instead of broken adapter
            data = {
                'profile_id': profile_id,
                'analysis_type': analysis_type,
                'archetype': archetype,
                'previous_analysis_id': previous_analysis_id,
                'behavior_analysis': behavior_json,
                'nutrition_plan': nutrition_json,
                'routine_plan': routine_json
            }
            
            result = self.connection.client.table('analysis_memory').insert(data).execute()
            
            analysis_id = str(result.data[0]['id'])
            print(f"[ANALYSIS] Created new analysis record: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            print(f"Error creating analysis record: {e}")
            raise
    
    def _convert_behavior_analysis(self, behavior_analysis: BehaviorAnalysisResult) -> Dict[str, Any]:
        """Convert behavior analysis to dictionary - use Pydantic serialization to preserve ALL data"""
        return behavior_analysis.model_dump()
    
    def _convert_nutrition_plan(self, nutrition_plan: NutritionPlanResult) -> Dict[str, Any]:
        """Convert nutrition plan to dictionary - use Pydantic serialization to preserve ALL data"""
        return nutrition_plan.model_dump()
    
    def _convert_routine_plan(self, routine_plan: RoutinePlanResult) -> Dict[str, Any]:
        """Convert routine plan to dictionary - use Pydantic serialization to preserve ALL data"""
        return routine_plan.model_dump()
    
    async def get_analysis_count(self, profile_id: str) -> int:
        """Get total number of analyses for a profile"""
        if not self.connection:
            await self.connect()
        
        try:
            # Use direct Supabase client instead of broken adapter
            result = self.connection.client.table('analysis_memory').select('*', count='exact', head=True).eq('profile_id', profile_id).execute()
            return result.count or 0
        except Exception as e:
            print(f"Error getting analysis count: {e}")
            return 0
    
    async def update_engagement_metrics(self, analysis_id: str, metrics: Dict[str, Any]) -> bool:
        """Update engagement metrics for an analysis"""
        if not self.connection:
            await self.connect()
        
        try:
            # Use direct Supabase client instead of broken adapter
            result = self.connection.client.table('analysis_memory').update({
                'engagement_metrics': metrics,
                'updated_at': datetime.now().isoformat()
            }).eq('id', analysis_id).execute()
            
            print(f"[ENGAGEMENT] Updated metrics for analysis: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Error updating engagement metrics: {e}")
            return False