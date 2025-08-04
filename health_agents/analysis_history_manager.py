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
            query = """
                SELECT *
                FROM analysis_memory 
                WHERE profile_id = $1 
                ORDER BY analysis_date DESC 
                LIMIT 1
            """
            
            row = await self.connection.fetchrow(query, profile_id)
            
            if row:
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
            return None
            
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
            
            query = """
                INSERT INTO analysis_memory (
                    profile_id, analysis_type, archetype, previous_analysis_id,
                    behavior_analysis, nutrition_plan, routine_plan
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """
            
            result = await self.connection.fetchrow(
                query, profile_id, analysis_type, archetype, previous_analysis_id,
                self._serialize_for_json(behavior_json) if behavior_json else None,
                self._serialize_for_json(nutrition_json) if nutrition_json else None,
                self._serialize_for_json(routine_json) if routine_json else None
            )
            
            analysis_id = str(result['id'])
            print(f"[ANALYSIS] Created new analysis record: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            print(f"Error creating analysis record: {e}")
            raise
    
    def _convert_behavior_analysis(self, behavior_analysis: BehaviorAnalysisResult) -> Dict[str, Any]:
        """Convert behavior analysis to dictionary"""
        return {
            "analysis_date": behavior_analysis.analysis_date,
            "user_id": behavior_analysis.user_id,
            "behavioral_signature": {
                "signature": behavior_analysis.behavioral_signature.signature,
                "confidence": behavior_analysis.behavioral_signature.confidence
            },
            "sophistication_assessment": {
                "score": behavior_analysis.sophistication_assessment.score,
                "category": behavior_analysis.sophistication_assessment.category,
                "justification": behavior_analysis.sophistication_assessment.justification
            },
            "primary_goal": {
                "goal": behavior_analysis.primary_goal.goal,
                "timeline": behavior_analysis.primary_goal.timeline,
                "success_metrics": behavior_analysis.primary_goal.success_metrics
            },
            "readiness_level": behavior_analysis.readiness_level,
            "habit_formation_stage": behavior_analysis.habit_formation_stage,
            "recommendations": behavior_analysis.recommendations
        }
    
    def _convert_nutrition_plan(self, nutrition_plan: NutritionPlanResult) -> Dict[str, Any]:
        """Convert nutrition plan to dictionary"""
        return {
            "date": nutrition_plan.date,
            "summary": nutrition_plan.nutrition.summary,
            "calories": nutrition_plan.nutrition.nutritional_info.calories,
            "protein": nutrition_plan.nutrition.nutritional_info.protein,
            "carbs": nutrition_plan.nutrition.nutritional_info.carbs,
            "fat": nutrition_plan.nutrition.nutritional_info.fat
        }
    
    def _convert_routine_plan(self, routine_plan: RoutinePlanResult) -> Dict[str, Any]:
        """Convert routine plan to dictionary"""
        return {
            "date": routine_plan.date,
            "summary": routine_plan.routine.summary,
            "morning_wakeup": routine_plan.routine.morning_wakeup.time_range,
            "focus_block": routine_plan.routine.focus_block.time_range,
            "afternoon_recharge": routine_plan.routine.afternoon_recharge.time_range,
            "evening_winddown": routine_plan.routine.evening_winddown.time_range
        }
    
    async def get_analysis_count(self, profile_id: str) -> int:
        """Get total number of analyses for a profile"""
        if not self.connection:
            await self.connect()
        
        try:
            result = await self.connection.fetchval(
                "SELECT COUNT(*) FROM analysis_memory WHERE profile_id = $1", 
                profile_id
            )
            return result or 0
        except Exception as e:
            print(f"Error getting analysis count: {e}")
            return 0
    
    async def update_engagement_metrics(self, analysis_id: str, metrics: Dict[str, Any]) -> bool:
        """Update engagement metrics for an analysis"""
        if not self.connection:
            await self.connect()
        
        try:
            query = """
                UPDATE analysis_memory 
                SET engagement_metrics = $2, updated_at = NOW()
                WHERE id = $1
            """
            
            await self.connection.execute(query, analysis_id, self._serialize_for_json(metrics))
            print(f"[ENGAGEMENT] Updated metrics for analysis: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Error updating engagement metrics: {e}")
            return False