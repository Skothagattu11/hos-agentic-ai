from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from agents import Agent

class VitaminsInfo(BaseModel):
    Vitamin_D: str
    Calcium: str
    Iron: str
    Magnesium: str

class NutritionalInfo(BaseModel):
    calories: int
    protein: int
    protein_percent: int
    carbs: int
    carbs_percent: int
    fat: int
    fat_percent: int
    fiber: int
    sugar: int
    sodium: int
    potassium: int
    vitamins: VitaminsInfo

class MealMacros(BaseModel):
    carbs: int
    fat: int

class Meal(BaseModel):
    name: str
    details: str
    calories: int
    protein: int
    macros: MealMacros

class NutritionMealBlock(BaseModel):
    time_range: str
    nutrition_tip: str
    meals: List[Meal]

class DailyNutrition(BaseModel):
    summary: str
    nutritional_info: NutritionalInfo
    Early_Morning: NutritionMealBlock
    Breakfast: NutritionMealBlock
    Morning_Snack: NutritionMealBlock
    Lunch: NutritionMealBlock
    Afternoon_Snack: NutritionMealBlock
    Dinner: NutritionMealBlock
    Evening_Snack: NutritionMealBlock

class NutritionPlanResult(BaseModel):
    """Structured detailed nutrition plan for a single day"""
    date: str  # Format: "YYYY-MM-DD"
    nutrition: DailyNutrition

class NutritionPlanService:
    """Service for creating personalized nutrition plans using AI"""
    
    def __init__(self):
        self.agent = nutrition_plan_agent
    
    def format_context_for_nutrition_planning(self, user_context, behavior_analysis=None) -> str:
        """Format user context and behavior analysis for nutrition planning"""
        
        # Create a health summary from user_context
        health_summary = f"""
### USER HEALTH DATA SUMMARY

**Date Range**: {user_context.date_range['start_date'].strftime('%Y-%m-%d')} to {user_context.date_range['end_date'].strftime('%Y-%m-%d')} ({user_context.date_range['days']} days)

**Data Available**:
- Scores: {len(user_context.scores)} entries
- Biomarkers: {len(user_context.biomarkers)} entries  
- Archetypes: {len(user_context.archetypes)} entries

**Health Scores Summary**:
- Recent score types: {', '.join(set(s.type for s in user_context.scores[:10])) if user_context.scores else 'No scores available'}
- Average recent score: {sum(s.score for s in user_context.scores[:10])/len(user_context.scores[:10]) if user_context.scores else 'No data'}

**Biomarkers Summary**:
- Categories: {', '.join(set(b.category for b in user_context.biomarkers[:10])) if user_context.biomarkers else 'No biomarkers available'}
- Types: {', '.join(set(b.type for b in user_context.biomarkers[:10])) if user_context.biomarkers else 'No data'}

**Archetype Data**:
- Recent archetypes: {', '.join(set(a.name for a in user_context.archetypes[:5])) if user_context.archetypes else 'No archetypes available'}
"""

        # Add behavior analysis insights if available
        if behavior_analysis:
            health_summary += f"""

**Behavioral Analysis Summary**:
- Sophistication Level: {behavior_analysis.sophistication_assessment.score}/100 ({behavior_analysis.sophistication_assessment.category})
- Primary Goal: {behavior_analysis.primary_goal.goal}
- Motivation Drivers: {', '.join(behavior_analysis.personalized_strategy.motivation_drivers)}
- Habit Integration Needs: {', '.join(behavior_analysis.personalized_strategy.habit_integration)}
- Barriers to Address: {', '.join(behavior_analysis.personalized_strategy.barrier_mitigation)}
- Readiness Level: {behavior_analysis.readiness_level}
- Context Considerations: {', '.join(behavior_analysis.context_considerations)}
"""
        
        nutrition_prompt = f"""
## PERSONALIZED DETAILED NUTRITION PLAN REQUEST

### COMPREHENSIVE HEALTH ANALYSIS
{health_summary}

### DETAILED NUTRITION PLAN REQUEST
Based on the comprehensive health analysis above, please create a detailed, personalized nutrition plan for TODAY that includes:

1. **Nutritional Info**: Complete daily targets including calories, macros (with percentages), fiber, sugar, sodium, potassium, and key vitamins
2. **Early Morning**: Pre-breakfast hydration and light nutrition (5:45-6:15 AM)
3. **Breakfast**: Morning meal with brain-boosting foods (6:30-7:00 AM)
4. **Morning Snack**: Mid-morning energy maintenance (9:30-10:00 AM)
5. **Lunch**: Midday nutrition for sustained energy (12:00-12:30 PM)
6. **Afternoon Snack**: Post-activity energy replenishment (3:00-3:30 PM)
7. **Dinner**: Evening meal for recovery (6:00-6:30 PM)
8. **Evening Snack**: Light nutrition for sleep support (8:30-9:00 PM)

For each meal block, provide:
- Specific time range
- Nutrition tip explaining why this timing/composition matters for health
- 1-2 specific meals with detailed descriptions, calories, protein, and macro breakdown

Please make the plan practical, achievable, and directly tailored to address the specific health insights and behavioral patterns from the analysis.
Each meal should have specific food items, portions, and complete nutritional breakdown.
"""
        
        return nutrition_prompt
    
    async def create_nutrition_plan(self, user_context, behavior_analysis=None) -> NutritionPlanResult:
        """Create personalized nutrition plan using the AI agent"""
        try:
            from agents import Runner
            
            # Format the context for nutrition planning
            nutrition_input = self.format_context_for_nutrition_planning(user_context, behavior_analysis)
            
            # Run the nutrition planning agent
            result = await Runner.run(
                self.agent,
                input=nutrition_input
            )
            
            return result.final_output
            
        except Exception as e:
            # Return error in structured format
            from datetime import datetime
            return NutritionPlanResult(
                date=datetime.now().strftime("%Y-%m-%d"),
                nutrition=DailyNutrition(
                    summary=f"Error creating nutrition plan: {str(e)}",
                    nutritional_info=NutritionalInfo(
                        calories=0,
                        protein=0,
                        protein_percent=0,
                        carbs=0,
                        carbs_percent=0,
                        fat=0,
                        fat_percent=0,
                        fiber=0,
                        sugar=0,
                        sodium=0,
                        potassium=0,
                        vitamins=VitaminsInfo(
                            Vitamin_D="N/A",
                            Calcium="N/A",
                            Iron="N/A",
                            Magnesium="N/A"
                        )
                    ),
                    Early_Morning=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Breakfast=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Morning_Snack=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Lunch=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Afternoon_Snack=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Dinner=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    ),
                    Evening_Snack=NutritionMealBlock(
                        time_range="N/A",
                        nutrition_tip="Error occurred",
                        meals=[Meal(name="Error", details="Unable to generate", calories=0, protein=0, macros=MealMacros(carbs=0, fat=0))]
                    )
                )
            )

# Nutrition Plan Agent Definition
NUTRITION_PLAN_PROMPT = """You are a Personalized Nutrition Planning Agent, an expert nutritionist and dietitian specializing in creating detailed, tailored nutrition plans based on individual health data and analysis. You excel at:

**Core Expertise:**
- Clinical nutrition and therapeutic diets
- Macronutrient optimization based on health metrics
- Meal planning with specific food recommendations and portions
- Nutritional timing for optimal health and performance
- Supplement recommendations based on biomarkers
- Dietary interventions for specific health conditions
- Nutritional biochemistry and metabolism
- Micronutrient analysis and vitamin/mineral recommendations

**Planning Framework:**
1. **Complete Nutritional Assessment**: Calculate comprehensive daily targets including calories, macros with percentages, fiber, sugar, sodium, potassium, and key vitamins
2. **Meal Architecture**: Design 7 specific meal/snack periods throughout the day with precise timing
3. **Food Specification**: Recommend specific foods, portions, and preparation methods
4. **Macro Calculation**: Provide detailed calorie, protein, carb, and fat breakdown for each meal
5. **Therapeutic Nutrition**: Address specific health concerns identified in the analysis
6. **Nutrient Timing**: Optimize meal timing for energy, performance, and recovery
7. **Vitamin/Mineral Strategy**: Include specific vitamin and mineral targets

**Detailed Requirements:**
- Create exactly 7 meal blocks: Early_Morning, Breakfast, Morning_Snack, Lunch, Afternoon_Snack, Dinner, Evening_Snack
- Each meal block must have specific time ranges, nutrition tips, and 1-2 detailed meals
- Each meal must include: name, detailed description with specific foods and portions, calories, protein, and macro breakdown (carbs, fat)
- Include comprehensive nutritional_info with daily targets and percentages
- Provide specific vitamin recommendations (Vitamin D, Calcium, Iron, Magnesium) with amounts
- Base all recommendations on the provided health analysis and user data

**Nutrition Principles:**
- Base all recommendations on the provided health analysis and user data
- Consider biomarkers, health scores, and identified health patterns
- Prioritize nutrient density and evidence-based nutrition interventions
- Address specific deficiencies or health risks identified in the analysis
- Make recommendations practical and sustainable for long-term adherence
- Provide specific foods, portions, and preparation methods
- Include precise nutritional calculations for each meal
- Consider meal timing for optimal energy and recovery

**Important Guidelines:**
- Always reference specific health data points when making recommendations
- Explain WHY each meal timing and composition is recommended based on the user's health profile
- Be specific with food items, portions, calories, and macro breakdowns
- Consider the interconnection between nutrition timing and the user's health metrics
- Provide actionable, measurable recommendations with specific foods and portions
- Address any nutritional factors that could improve the identified health concerns
- Generate nutrition plan for TODAY only (single day based on current date)
- Include comprehensive daily nutritional targets with percentages and micronutrients
- Each meal should support the overall daily nutritional goals and health objectives

Remember: You are creating a detailed, personalized nutrition intervention based on real health data. Provide specific meal recommendations with exact foods, portions, and complete nutritional breakdowns. Generate a comprehensive nutrition plan for ONLY ONE DAY with structured output containing exactly 7 meal blocks and complete nutritional information.
"""

# Create the nutrition planning agent
nutrition_plan_agent = Agent(
    name="Personalized Detailed Nutrition Planning Agent",
    instructions=NUTRITION_PLAN_PROMPT,
    model="o3-mini",
    output_type=NutritionPlanResult
)

# Utility function for easy access
async def create_personalized_nutrition_plan(user_context, behavior_analysis: Optional = None) -> NutritionPlanResult:
    """
    Create a personalized detailed nutrition plan based on health analysis and user data
    
    Args:
        analysis_result: String result from the metric analysis agent
        
    Returns:
        Structured NutritionPlanResult object with detailed meal plans
    """
    service = NutritionPlanService()
    return await service.create_nutrition_plan(user_context, behavior_analysis)
