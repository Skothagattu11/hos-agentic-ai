import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncpg
from .connection_factory import smart_connect
from .nutrition_plan_agent import NutritionPlanResult
from .routine_plan_agent import RoutinePlanResult
from .behavior_analysis_agent import BehaviorAnalysisResult

@dataclass
class UserMemory:
    """User memory data structure"""
    profile_id: str
    user_preferences: Dict[str, Any]
    health_goals: Dict[str, Any]
    dietary_restrictions: Dict[str, Any]
    lifestyle_context: Dict[str, Any]
    medical_conditions: Dict[str, Any]
    last_analysis_result: Optional[str]
    analysis_insights: Dict[str, Any]
    last_nutrition_plan: Optional[Dict[str, Any]]
    last_routine_plan: Optional[Dict[str, Any]]
    last_behavior_analysis: Optional[Dict[str, Any]]
    # Archetype-specific routine plans
    transformation_seeker_plan: Optional[Dict[str, Any]]
    systematic_improver_plan: Optional[Dict[str, Any]]
    peak_performer_plan: Optional[Dict[str, Any]]
    resilience_rebuilder_plan: Optional[Dict[str, Any]]
    connected_explorer_plan: Optional[Dict[str, Any]]
    foundation_builder_plan: Optional[Dict[str, Any]]
    last_archetype: Optional[str]
    health_trends: Dict[str, Any]
    improvement_areas: Dict[str, Any]
    success_patterns: Dict[str, Any]
    total_analyses: int
    last_analysis_date: Optional[datetime]
    nutrition_plan_date: Optional[datetime]
    routine_plan_date: Optional[datetime]
    behavior_analysis_date: Optional[datetime]

class MemoryManager:
    """Manages user memory for health analysis continuity"""
    
    def __init__(self, database_url: str = None):
        # Store database_url for compatibility, but we'll use smart_connect
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
        """Establish database connection using smart connection factory"""
        try:
            self.connection = await smart_connect(self.database_url)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
    
    async def get_user_memory(self, profile_id: str) -> Optional[UserMemory]:
        """Retrieve user memory from database"""
        if not self.connection:
            await self.connect()
        
        try:
            # Use a simpler query that works better with Supabase
            query = """
                SELECT *
                FROM memory 
                WHERE profile_id = $1
            """
            
            row = await self.connection.fetchrow(query, profile_id)
            
            if row:
                return UserMemory(
                    profile_id=row['profile_id'],
                    user_preferences=row['user_preferences'] or {},
                    health_goals=row['health_goals'] or {},
                    dietary_restrictions=row['dietary_restrictions'] or {},
                    lifestyle_context=row['lifestyle_context'] or {},
                    medical_conditions=row['medical_conditions'] or {},
                    last_analysis_result=row['last_analysis_result'],
                    analysis_insights=row['analysis_insights'] or {},
                    last_nutrition_plan=row['last_nutrition_plan'],
                    last_routine_plan=row['last_routine_plan'],
                    last_behavior_analysis=row['last_behavior_analysis'],
                    # Archetype-specific routine plans
                    transformation_seeker_plan=row['transformation_seeker_plan'],
                    systematic_improver_plan=row['systematic_improver_plan'],
                    peak_performer_plan=row['peak_performer_plan'],
                    resilience_rebuilder_plan=row['resilience_rebuilder_plan'],
                    connected_explorer_plan=row['connected_explorer_plan'],
                    foundation_builder_plan=row['foundation_builder_plan'],
                    last_archetype=row['last_archetype'],
                    health_trends=row['health_trends'] or {},
                    improvement_areas=row['improvement_areas'] or {},
                    success_patterns=row['success_patterns'] or {},
                    total_analyses=row['total_analyses'] or 0,
                    last_analysis_date=row['last_analysis_date'],
                    nutrition_plan_date=row['nutrition_plan_date'],
                    routine_plan_date=row['routine_plan_date'],
                    behavior_analysis_date=row['behavior_analysis_date']
                )
            return None
            
        except Exception as e:
            print(f"Error retrieving user memory: {e}")
            return None
    
    async def create_user_memory(self, profile_id: str, 
                                user_preferences: Dict[str, Any] = None,
                                health_goals: Dict[str, Any] = None,
                                dietary_restrictions: Dict[str, Any] = None,
                                lifestyle_context: Dict[str, Any] = None,
                                medical_conditions: Dict[str, Any] = None) -> bool:
        """Create initial user memory record"""
        if not self.connection:
            await self.connect()
        
        try:
            # First try to update existing record
            update_query = """
                UPDATE memory 
                SET user_preferences = $2,
                    health_goals = $3,
                    dietary_restrictions = $4,
                    lifestyle_context = $5,
                    medical_conditions = $6,
                    updated_at = NOW()
                WHERE profile_id = $1
            """
            
            result = await self.connection.execute(
                update_query, profile_id,
                self._serialize_for_json(user_preferences or {}),
                self._serialize_for_json(health_goals or {}),
                self._serialize_for_json(dietary_restrictions or {}),
                self._serialize_for_json(lifestyle_context or {}),
                self._serialize_for_json(medical_conditions or {})
            )
            
            # If no rows were updated, insert new record
            if result == "UPDATE 0":
                insert_query = """
                    INSERT INTO memory (profile_id, user_preferences, health_goals, 
                                      dietary_restrictions, lifestyle_context, medical_conditions)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """
                
                await self.connection.execute(
                    insert_query, profile_id,
                    self._serialize_for_json(user_preferences or {}),
                    self._serialize_for_json(health_goals or {}),
                    self._serialize_for_json(dietary_restrictions or {}),
                    self._serialize_for_json(lifestyle_context or {}),
                    self._serialize_for_json(medical_conditions or {})
                )
            
            return True
            
        except Exception as e:
            print(f"Error creating user memory: {e}")
            return False
    
    async def update_analysis_result(self, profile_id: str, analysis_result: str, 
                                   insights: Dict[str, Any] = None) -> bool:
        """Update memory with new analysis result"""
        if not self.connection:
            await self.connect()
        
        try:
            query = """
                UPDATE memory 
                SET last_analysis_result = $2,
                    analysis_insights = $3,
                    last_analysis_date = NOW(),
                    total_analyses = total_analyses + 1
                WHERE profile_id = $1
            """
            
            await self.connection.execute(
                query, profile_id, analysis_result, 
                self._serialize_for_json(insights or {})
            )
            return True
            
        except Exception as e:
            print(f"Error updating analysis result: {e}")
            return False
    
    async def update_nutrition_plan(self, profile_id: str, 
                                  nutrition_plan: NutritionPlanResult) -> bool:
        """Update memory with new nutrition plan"""
        if not self.connection:
            await self.connect()
        
        # Ensure memory record exists
        await self.ensure_user_memory_exists(profile_id)
        
        try:
            # Convert nutrition plan to dict for JSON storage
            plan_dict = {
                "date": nutrition_plan.date,
                "nutrition": {
                    "summary": nutrition_plan.nutrition.summary,
                    "nutritional_info": {
                        "calories": nutrition_plan.nutrition.nutritional_info.calories,
                        "protein": nutrition_plan.nutrition.nutritional_info.protein,
                        "protein_percent": nutrition_plan.nutrition.nutritional_info.protein_percent,
                        "carbs": nutrition_plan.nutrition.nutritional_info.carbs,
                        "carbs_percent": nutrition_plan.nutrition.nutritional_info.carbs_percent,
                        "fat": nutrition_plan.nutrition.nutritional_info.fat,
                        "fat_percent": nutrition_plan.nutrition.nutritional_info.fat_percent,
                        "fiber": nutrition_plan.nutrition.nutritional_info.fiber,
                        "sugar": nutrition_plan.nutrition.nutritional_info.sugar,
                        "sodium": nutrition_plan.nutrition.nutritional_info.sodium,
                        "potassium": nutrition_plan.nutrition.nutritional_info.potassium,
                        "vitamins": {
                            "Vitamin_D": nutrition_plan.nutrition.nutritional_info.vitamins.Vitamin_D,
                            "Calcium": nutrition_plan.nutrition.nutritional_info.vitamins.Calcium,
                            "Iron": nutrition_plan.nutrition.nutritional_info.vitamins.Iron,
                            "Magnesium": nutrition_plan.nutrition.nutritional_info.vitamins.Magnesium
                        }
                    },
                    # Add all meal blocks...
                    "Early_Morning": self._meal_block_to_dict(nutrition_plan.nutrition.Early_Morning),
                    "Breakfast": self._meal_block_to_dict(nutrition_plan.nutrition.Breakfast),
                    "Morning_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Morning_Snack),
                    "Lunch": self._meal_block_to_dict(nutrition_plan.nutrition.Lunch),
                    "Afternoon_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Afternoon_Snack),
                    "Dinner": self._meal_block_to_dict(nutrition_plan.nutrition.Dinner),
                    "Evening_Snack": self._meal_block_to_dict(nutrition_plan.nutrition.Evening_Snack)
                }
            }
            
            query = """
                UPDATE memory 
                SET last_nutrition_plan = $2,
                    nutrition_plan_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(plan_dict))
            return True
            
        except Exception as e:
            print(f"Error updating nutrition plan: {e}")
            return False
    
    async def update_routine_plan(self, profile_id: str, 
                                routine_plan: RoutinePlanResult) -> bool:
        """Update memory with new routine plan"""
        if not self.connection:
            await self.connect()
        
        # Ensure memory record exists
        await self.ensure_user_memory_exists(profile_id)
        
        try:
            # Convert routine plan to dict for JSON storage
            plan_dict = {
                "date": routine_plan.date,
                "routine": {
                    "summary": routine_plan.routine.summary,
                    "morning_wakeup": self._time_block_to_dict(routine_plan.routine.morning_wakeup),
                    "focus_block": self._time_block_to_dict(routine_plan.routine.focus_block),
                    "afternoon_recharge": self._time_block_to_dict(routine_plan.routine.afternoon_recharge),
                    "evening_winddown": self._time_block_to_dict(routine_plan.routine.evening_winddown)
                }
            }
            
            query = """
                UPDATE memory 
                SET last_routine_plan = $2,
                    routine_plan_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(plan_dict))
            return True
            
        except Exception as e:
            print(f"Error updating routine plan: {e}")
            return False

    async def update_behavior_analysis(self, profile_id: str, 
                                     behavior_analysis: BehaviorAnalysisResult) -> bool:
        """Update memory with new behavior analysis"""
        if not self.connection:
            await self.connect()
        
        # Ensure memory record exists
        await self.ensure_user_memory_exists(profile_id)
        
        try:
            # Convert behavior analysis to dict for JSON storage
            analysis_dict = {
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
                "adaptive_parameters": {
                    "complexity_level": behavior_analysis.adaptive_parameters.complexity_level,
                    "time_commitment": behavior_analysis.adaptive_parameters.time_commitment,
                    "technology_integration": behavior_analysis.adaptive_parameters.technology_integration,
                    "customization_level": behavior_analysis.adaptive_parameters.customization_level
                },
                "evidence_based_kpis": {
                    "behavioral_metrics": behavior_analysis.evidence_based_kpis.behavioral_metrics,
                    "performance_metrics": behavior_analysis.evidence_based_kpis.performance_metrics,
                    "mastery_metrics": behavior_analysis.evidence_based_kpis.mastery_metrics
                },
                "personalized_strategy": {
                    "motivation_drivers": behavior_analysis.personalized_strategy.motivation_drivers,
                    "habit_integration": behavior_analysis.personalized_strategy.habit_integration,
                    "barrier_mitigation": behavior_analysis.personalized_strategy.barrier_mitigation
                },
                "adaptation_framework": {
                    "escalation_triggers": behavior_analysis.adaptation_framework.escalation_triggers,
                    "deescalation_triggers": behavior_analysis.adaptation_framework.deescalation_triggers,
                    "adaptation_frequency": behavior_analysis.adaptation_framework.adaptation_frequency
                },
                "readiness_level": behavior_analysis.readiness_level,
                "habit_formation_stage": behavior_analysis.habit_formation_stage,
                "motivation_profile": {
                    "primary_drivers": behavior_analysis.motivation_profile.primary_drivers,
                    "secondary_drivers": behavior_analysis.motivation_profile.secondary_drivers,
                    "motivation_type": behavior_analysis.motivation_profile.motivation_type,
                    "reward_preferences": behavior_analysis.motivation_profile.reward_preferences,
                    "accountability_level": behavior_analysis.motivation_profile.accountability_level,
                    "social_motivation": behavior_analysis.motivation_profile.social_motivation
                },
                "context_considerations": behavior_analysis.context_considerations,
                "recommendations": behavior_analysis.recommendations
            }
            
            query = """
                UPDATE memory 
                SET last_behavior_analysis = $2,
                    behavior_analysis_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(analysis_dict))
            return True
            
        except Exception as e:
            print(f"Error updating behavior analysis: {e}")
            return False

    async def update_archetype_routine_plan(self, profile_id: str, 
                                           archetype: str, routine_plan: RoutinePlanResult) -> bool:
        """Update memory with new archetype-specific routine plan"""
        if not self.connection:
            await self.connect()
        
        try:
            # Convert routine plan to dict for JSON storage
            plan_dict = {
                "date": routine_plan.date,
                "routine": {
                    "summary": routine_plan.routine.summary,
                    "morning_wakeup": self._time_block_to_dict(routine_plan.routine.morning_wakeup),
                    "focus_block": self._time_block_to_dict(routine_plan.routine.focus_block),
                    "afternoon_recharge": self._time_block_to_dict(routine_plan.routine.afternoon_recharge),
                    "evening_winddown": self._time_block_to_dict(routine_plan.routine.evening_winddown)
                }
            }
            
            # Map archetype names to database column names
            archetype_columns = {
                "Transformation Seeker": "transformation_seeker_plan",
                "Systematic Improver": "systematic_improver_plan",
                "Peak Performer": "peak_performer_plan",
                "Resilience Rebuilder": "resilience_rebuilder_plan",
                "Connected Explorer": "connected_explorer_plan",
                "Foundation Builder": "foundation_builder_plan"
            }
            
            if archetype not in archetype_columns:
                print(f"Unknown archetype: {archetype}")
                return False
            
            column_name = archetype_columns[archetype]
            
            query = f"""
                UPDATE memory 
                SET {column_name} = $2,
                    last_archetype = $3,
                    routine_plan_date = NOW()
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, profile_id, self._serialize_for_json(plan_dict), archetype)
            return True
            
        except Exception as e:
            print(f"Error updating {archetype} routine plan: {e}")
            return False

    async def update_user_context(self, profile_id: str, 
                                 user_preferences: Dict[str, Any] = None,
                                 health_goals: Dict[str, Any] = None,
                                 dietary_restrictions: Dict[str, Any] = None,
                                 lifestyle_context: Dict[str, Any] = None,
                                 medical_conditions: Dict[str, Any] = None) -> bool:
        """Update user context information"""
        if not self.connection:
            await self.connect()
        
        try:
            update_fields = []
            params = [profile_id]
            param_count = 2
            
            if user_preferences is not None:
                update_fields.append(f"user_preferences = ${param_count}")
                params.append(self._serialize_for_json(user_preferences))
                param_count += 1
            
            if health_goals is not None:
                update_fields.append(f"health_goals = ${param_count}")
                params.append(self._serialize_for_json(health_goals))
                param_count += 1
            
            if dietary_restrictions is not None:
                update_fields.append(f"dietary_restrictions = ${param_count}")
                params.append(self._serialize_for_json(dietary_restrictions))
                param_count += 1
            
            if lifestyle_context is not None:
                update_fields.append(f"lifestyle_context = ${param_count}")
                params.append(self._serialize_for_json(lifestyle_context))
                param_count += 1
            
            if medical_conditions is not None:
                update_fields.append(f"medical_conditions = ${param_count}")
                params.append(self._serialize_for_json(medical_conditions))
                param_count += 1
            
            if not update_fields:
                return True
            
            query = f"""
                UPDATE memory 
                SET {', '.join(update_fields)}
                WHERE profile_id = $1
            """
            
            await self.connection.execute(query, *params)
            return True
            
        except Exception as e:
            print(f"Error updating user context: {e}")
            return False
    
    def _meal_block_to_dict(self, meal_block) -> Dict[str, Any]:
        """Convert meal block to dictionary"""
        return {
            "time_range": meal_block.time_range,
            "nutrition_tip": meal_block.nutrition_tip,
            "meals": [
                {
                    "name": meal.name,
                    "details": meal.details,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "macros": {
                        "carbs": meal.macros.carbs,
                        "fat": meal.macros.fat
                    }
                }
                for meal in meal_block.meals
            ]
        }
    
    def _time_block_to_dict(self, time_block) -> Dict[str, Any]:
        """Convert time block to dictionary"""
        return {
            "time_range": time_block.time_range,
            "why_it_matters": time_block.why_it_matters,
            "tasks": [
                {
                    "task": task.task,
                    "reason": task.reason
                }
                for task in time_block.tasks
            ]
        }
    
    def format_memory_context(self, memory: UserMemory) -> str:
        """Format memory into context string for analysis"""
        if not memory:
            return "No previous memory available for this user."
        
        context_parts = []
        
        # User preferences and goals
        if memory.user_preferences:
            context_parts.append(f"User Preferences: {self._serialize_for_json(memory.user_preferences)}")
        
        if memory.health_goals:
            context_parts.append(f"Health Goals: {self._serialize_for_json(memory.health_goals)}")
        
        if memory.dietary_restrictions:
            context_parts.append(f"Dietary Restrictions: {self._serialize_for_json(memory.dietary_restrictions)}")
        
        if memory.lifestyle_context:
            context_parts.append(f"Lifestyle Context: {self._serialize_for_json(memory.lifestyle_context)}")
        
        if memory.medical_conditions:
            context_parts.append(f"Medical Conditions: {self._serialize_for_json(memory.medical_conditions)}")
        
        # Previous analysis insights
        if memory.last_analysis_result:
            context_parts.append(f"Previous Analysis (from {memory.last_analysis_date}): {memory.last_analysis_result[:500]}...")
        
        if memory.analysis_insights:
            context_parts.append(f"Analysis Insights: {self._serialize_for_json(memory.analysis_insights)}")
        
        # Health trends and patterns
        if memory.health_trends:
            context_parts.append(f"Health Trends: {self._serialize_for_json(memory.health_trends)}")
        
        if memory.success_patterns:
            context_parts.append(f"Success Patterns: {self._serialize_for_json(memory.success_patterns)}")
        
        if memory.improvement_areas:
            context_parts.append(f"Areas for Improvement: {self._serialize_for_json(memory.improvement_areas)}")
        
        # Previous behavior analysis
        if memory.last_behavior_analysis:
            context_parts.append(f"Previous Behavior Analysis (from {memory.behavior_analysis_date}): {self._serialize_for_json(memory.last_behavior_analysis)}")
        
        # Analysis history
        context_parts.append(f"Total Previous Analyses: {memory.total_analyses}")
        
        return "\n\n".join(context_parts)

    async def ensure_user_memory_exists(self, profile_id: str) -> bool:
        """Ensure a memory record exists for the user, create if not"""
        if not self.connection:
            await self.connect()
        
        try:
            # First check if record exists using a simple query that works with Supabase
            try:
                existing = await self.connection.fetchrow(
                    "SELECT id FROM memory WHERE profile_id = $1", profile_id
                )
                
                if existing:
                    print(f"[MEMORY] Record already exists for profile_id: {profile_id}")
                    return True
            except Exception as select_error:
                print(f"[MEMORY] SELECT check failed: {select_error}")
                # Continue to INSERT, handle constraint error below
            
            # If no record exists, create one
            query = """
                INSERT INTO memory (profile_id, user_preferences, health_goals, 
                                  dietary_restrictions, lifestyle_context, medical_conditions)
                VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            await self.connection.execute(
                query, profile_id,
                self._serialize_for_json({}),
                self._serialize_for_json({}),
                self._serialize_for_json({}),
                self._serialize_for_json({}),
                self._serialize_for_json({})
            )
            print(f"[MEMORY] Created new record for profile_id: {profile_id}")
            return True
            
        except Exception as e:
            print(f"Error ensuring user memory exists: {e}")
            # If it's a duplicate key error, the record exists, which is fine
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                print(f"[MEMORY] Record already exists (from constraint error)")
                return True
            return False

    async def update_analysis_results(self, profile_id: str, 
                                    user_context = None,
                                    nutrition_plan: NutritionPlanResult = None,
                                    routine_plan: RoutinePlanResult = None,
                                    behavior_analysis: BehaviorAnalysisResult = None,
                                    selected_archetype: str = None) -> bool:
        """Comprehensive update of all analysis results in memory"""
        if not self.connection:
            await self.connect()
        
        try:
            # Ensure memory record exists
            await self.ensure_user_memory_exists(profile_id)
            
            # user_context is passed for potential future data logging/tracking
            
            # Update nutrition plan
            if nutrition_plan:
                await self.update_nutrition_plan(profile_id, nutrition_plan)
            
            # Update routine plan (with archetype if provided)
            if routine_plan:
                if selected_archetype:
                    await self.update_archetype_routine_plan(profile_id, selected_archetype, routine_plan)
                else:
                    await self.update_routine_plan(profile_id, routine_plan)
            
            # Update behavior analysis
            if behavior_analysis:
                await self.update_behavior_analysis(profile_id, behavior_analysis)
            
            return True
            
        except Exception as e:
            print(f"Error updating analysis results: {e}")
            return False 