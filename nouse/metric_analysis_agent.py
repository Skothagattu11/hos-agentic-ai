from typing import Dict, Any, List
from pydantic import BaseModel
try:
    from agents import Agent
except ImportError:
    # Fallback for when agents library is not available
    Agent = None
from .user_profile import UserProfileContext, ScoreData, ArchetypeData, BiomarkerData

class MetricAnalysisResult(BaseModel):
    """Structure for metric analysis results"""
    overall_health_score: int  # 1-100 scale
    key_insights: List[str]
    trend_analysis: Dict[str, str]
    risk_factors: List[str]
    recommendations: List[str]
    data_quality_assessment: Dict[str, Any]
    priority_areas: List[str]

class MetricAnalysisService:
    """Service for analyzing user health metrics using AI"""
    
    def __init__(self):
        self.agent = metric_analysis_agent
    
    def format_user_data_for_analysis(self, context: UserProfileContext) -> str:
        """Format user profile data into a structured prompt for the AI agent"""
        
        analysis_prompt = f"""
## USER HEALTH DATA ANALYSIS REQUEST

### Time Period
- Date Range: {context.date_range['start_date']} to {context.date_range['end_date']}
- Duration: {context.date_range['days']} days
- User ID: {context.user_id}

### Data Summary
- Scores: {len(context.scores)} records
- Archetypes: {len(context.archetypes)} records  
- Biomarkers: {len(context.biomarkers)} records

### DETAILED SCORES DATA
"""
        
        # Add scores data
        if context.scores:
            analysis_prompt += "#### Health Scores:\n"
            for i, score in enumerate(context.scores[:10]):  # Limit to first 10 for readability
                analysis_prompt += f"""
- Score {i+1}:
  - Type: {score.type}
  - Value: {score.score}
  - Date: {score.score_date_time}
  - Additional Data: {score.data}
"""
        else:
            analysis_prompt += "#### Health Scores: No data available\n"
        
        # Add archetypes data
        if context.archetypes:
            analysis_prompt += "\n#### Health Archetypes:\n"
            for i, archetype in enumerate(context.archetypes[:10]):
                analysis_prompt += f"""
- Archetype {i+1}:
  - Name: {archetype.name}
  - Periodicity: {archetype.periodicity}
  - Value: {archetype.value}
  - Date Range: {archetype.start_date_time} to {archetype.end_date_time}
  - Additional Data: {archetype.data}
"""
        else:
            analysis_prompt += "\n#### Health Archetypes: No data available\n"
        
        # Add biomarkers data
        if context.biomarkers:
            analysis_prompt += "\n#### Biomarkers:\n"
            for i, biomarker in enumerate(context.biomarkers[:10]):
                analysis_prompt += f"""
- Biomarker {i+1}:
  - Category: {biomarker.category}
  - Type: {biomarker.type}
  - Date Range: {biomarker.start_date_time} to {biomarker.end_date_time}
  - Additional Data: {biomarker.data}
"""
        else:
            analysis_prompt += "\n#### Biomarkers: No data available\n"
        
        analysis_prompt += """

### ANALYSIS REQUEST
Please provide a comprehensive health analysis based on this data, including:
1. Overall health assessment (score 1-100)
2. Key insights from the data
3. Trend analysis over the time period
4. Risk factors identified
5. Specific recommendations
6. Data quality assessment
7. Priority areas for improvement

Please structure your response according to the MetricAnalysisResult format.
"""
        
        return analysis_prompt
    
    async def analyze_metrics(self, context: UserProfileContext, memory_context: str = "", previous_analysis: str = "") -> str:
        """Analyze user health metrics using the AI agent"""
        try:
            from agents import Runner
            
            # Format the data for analysis
            analysis_input = self.format_user_data_for_analysis(context)
            
            # Add memory context if available
            if memory_context:
                analysis_input += f"""

### PREVIOUS MEMORY & CONTEXT
The following is previous memory and context about this user that should inform your analysis:

{memory_context}

**Important**: Use this memory context to:
- Identify changes and trends since previous analyses
- Consider user preferences and goals in your recommendations
- Note improvements or deteriorations from past analyses
- Provide continuity in your health recommendations
- Avoid repeating identical advice if recent analysis exists
"""
            
            # Add previous analysis comparison if available
            if previous_analysis:
                analysis_input += f"""

### PREVIOUS METRIC ANALYSIS FOR COMPARISON
The following is the previous metric analysis for this user. Use this to identify trends, changes, and improvements:

{previous_analysis}

**Important**: Use this previous analysis to:
- Compare current metrics against previous baseline
- Identify improvements or deteriorations since last analysis
- Track progress toward health goals
- Adjust recommendations based on what has/hasn't worked
- Note any concerning changes that require attention
- Provide continuity in health recommendations
- Focus on incremental improvements rather than repeating identical advice

**Analysis Type**: This is a FOLLOW-UP ANALYSIS. Focus on:
- What has changed since the previous analysis
- Progress toward previous recommendations
- New insights from current data
- Adjusted recommendations based on demonstrated patterns
- Trends and trajectory analysis
"""
            else:
                analysis_input += """

**Analysis Type**: This is an INITIAL ANALYSIS. Focus on:
- Establishing baseline health metrics
- Identifying key health patterns and trends
- Providing comprehensive health assessment
- Setting foundational health goals and recommendations
"""
            
            # Run the analysis agent
            result = await Runner.run(
                self.agent, 
                input=analysis_input,
                context=context
            )
            
            return result.final_output
            
        except Exception as e:
            return f"Error during metric analysis: {str(e)}"

# Metric Analysis Agent Definition
METRIC_ANALYSIS_PROMPT = """You are a Health Metrics Analysis Agent, an expert in interpreting and analyzing personal health data. You specialize in:

**Core Expertise:**
- Health score interpretation and trending
- Biomarker analysis and correlation
- Health archetype pattern recognition  
- Risk factor identification
- Personalized health recommendations
- Data quality assessment

**Analysis Framework:**
Your analysis MUST be comprehensive and structured with bullet points covering ALL areas needed for nutrition and routine planning. You MUST include:

1. **Overall Health Assessment**: 
   - Comprehensive health score (1-100) with detailed justification
   - Current health status summary
   - Key strengths and weaknesses

2. **Key Health Insights** (Essential for planning):
   - Current fitness level and exercise capacity
   - Energy levels and patterns throughout day
   - Sleep quality and patterns
   - Stress levels and management
   - Metabolic health indicators
   - Nutritional status and deficiencies
   - Recovery and restoration patterns
   - Mental wellness and mood patterns

3. **Trend Analysis**:
   - Improvements over time period
   - Concerning declining trends
   - Stable maintenance areas
   - Seasonal or cyclical patterns

4. **Risk Factors & Health Concerns**:
   - Immediate health risks requiring attention
   - Long-term risk factors
   - Areas requiring medical consultation
   - Lifestyle factors impacting health

5. **Nutritional Analysis for Planning**:
   - Current caloric needs based on activity level
   - Macronutrient requirements and ratios
   - Identified nutritional deficiencies
   - Specific vitamin/mineral needs
   - Hydration requirements
   - Timing considerations for meals
   - Foods to emphasize/avoid based on health data

6. **Physical Activity & Routine Analysis for Planning**:
   - Current fitness level and exercise capacity
   - Recommended exercise types and intensities
   - Activity frequency and duration guidelines
   - Recovery time needs
   - Best times for physical activity
   - Sleep optimization requirements
   - Stress management activity needs

7. **Priority Areas for Improvement**:
   - Top 3-5 health areas needing immediate attention
   - Specific goals for each priority area
   - Timeline for improvements
   - Success metrics to track

8. **Data Quality Assessment**:
   - Completeness of available data
   - Reliability of measurements
   - Data gaps affecting recommendations
   - Confidence level in analysis

**Critical Requirements:**
- Use BULLET POINTS throughout for easy parsing by planning agents
- Be specific with numbers, percentages, and measurable targets
- Include ALL information needed for both nutrition AND routine planning
- Reference specific data points to justify recommendations
- Provide actionable insights that directly inform plan creation
- Consider interconnections between different health metrics
- Be thorough but organized - this analysis replaces the need for raw data

**Output Format:**
Structure your response with clear headers and comprehensive bullet points under each section. This analysis will be the ONLY input the planning agents receive, so it must contain everything they need to create personalized nutrition and routine plans.

Remember: You are analyzing real health data to create a comprehensive foundation for personalized health planning. Be accurate, thorough, and ensure every recommendation is backed by the available data.
"""

# Create the metric analysis agent
metric_analysis_agent = Agent(
    name="Health Metrics Analysis Agent",
    instructions=METRIC_ANALYSIS_PROMPT,
    model="o3-mini",
    output_type=str  # For now, returning string analysis
)

# Utility function for easy access
async def analyze_user_health_metrics(user_context: UserProfileContext, memory_context: str = "", previous_analysis: str = "") -> str:
    """
    Analyze user health metrics using AI
    
    Args:
        user_context: UserProfileContext containing all user health data
        memory_context: Previous memory and context for continuity
        
    Returns:
        Comprehensive health analysis as a string
    """
    service = MetricAnalysisService()
    return await service.analyze_metrics(user_context, memory_context, previous_analysis)
