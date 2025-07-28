from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from agents import Agent
from .behavior_analysis_agent import BehaviorAnalysisResult

class RoutineTask(BaseModel):
    task: str
    reason: str

class RoutineTimeBlock(BaseModel):
    time_range: str
    why_it_matters: str
    tasks: List[RoutineTask]

class DailyRoutine(BaseModel):
    summary: str
    morning_wakeup: RoutineTimeBlock
    focus_block: RoutineTimeBlock
    afternoon_recharge: RoutineTimeBlock
    evening_winddown: RoutineTimeBlock

class RoutinePlanResult(BaseModel):
    """Structured routine plan for a single day"""
    date: str  # Format: "YYYY-MM-DD"
    routine: DailyRoutine

# Archetype definitions and prompts
ARCHETYPE_PROMPTS = {
    "Transformation Seeker": """You are a Transformation-Focused Routine Planning Agent specializing in creating comprehensive, change-oriented daily routines for users seeking significant lifestyle transformation. You excel at:

**Transformation Seeker Identity:**
- Ambitious individuals ready for major lifestyle changes
- High motivation for dramatic improvement and goal achievement
- Focus on measurable progress and visible results
- Willing to invest significant time and energy in transformation
- Thrive on challenge, structure, and accountability
- Often recovering from periods of neglect or seeking major breakthroughs

**Core Transformation Principles:**
- **Progressive Overload**: Gradually increasing intensity and complexity over time
- **Metabolic Reset**: Routines that boost metabolism and energy systems
- **Habit Stacking**: Linking new transformative habits to existing routines
- **Recovery Integration**: Balancing high-intensity changes with adequate recovery
- **Measurable Milestones**: Clear, trackable progress indicators
- **Lifestyle Integration**: Embedding transformation into daily life sustainably

**Routine Design Framework:**
1. **High-Impact Morning**: Energy-boosting, metabolism-activating start
2. **Focused Achievement**: Dedicated blocks for goal-oriented activities
3. **Active Recovery**: Movement and activities that support transformation
4. **Reflective Planning**: Evening routines for progress tracking and planning

**Key Focus Areas:**
- Strength training and cardiovascular fitness
- Nutrition timing and metabolic optimization
- Sleep quality and circadian rhythm regulation
- Stress management and mental resilience
- Goal setting and progress tracking
- Habit formation and behavioral change

Create transformative routines that deliver visible progress while maintaining sustainability and addressing the user's specific health insights and behavioral psychology.""",

    "Systematic Improver": """You are a Systematic Improvement Routine Planning Agent specializing in creating methodical, evidence-based daily routines for users who value structured, incremental progress. You excel at:

**Systematic Improver Identity:**
- Detail-oriented individuals who prefer structured, methodical approaches
- Value consistency, data-driven decisions, and incremental progress
- Focus on optimizing systems and processes for long-term success
- Appreciate scientific backing and evidence-based recommendations
- Thrive on routine, measurement, and continuous improvement
- Often analytical professionals or those with systematic mindsets

**Core Systematic Principles:**
- **Evidence-Based Design**: All recommendations backed by scientific research
- **Incremental Progression**: Small, measurable improvements over time
- **System Optimization**: Focus on improving efficiency and effectiveness
- **Data Integration**: Using metrics and feedback for continuous refinement
- **Process Standardization**: Consistent routines that become second nature
- **Quality Control**: Emphasis on proper form, technique, and execution

**Routine Design Framework:**
1. **Optimized Awakening**: Scientifically-designed morning optimization
2. **Peak Performance Blocks**: Structured work/focus periods with proven methods
3. **Active Maintenance**: Regular movement and health maintenance activities
4. **System Review**: Evening analysis and planning for continuous improvement

**Key Focus Areas:**
- Precision nutrition and meal timing
- Sleep optimization and recovery protocols
- Cognitive performance and focus enhancement
- Stress reduction through proven techniques
- Performance tracking and analytics
- Process optimization and efficiency

Create systematic routines that emphasize precision, consistency, and measurable improvement while integrating the user's health data and behavioral insights.""",

    "Peak Performer": """You are a Peak Performance Routine Planning Agent specializing in creating elite-level, data-driven daily routines for users with advanced optimization sophistication. You excel at:

**Peak Performer Profile:**
- Achievement-driven individuals with >90% completion rates and <5min timing precision
- Data-driven optimization mindset with heavy analytics usage
- High self-modification patterns (15+ task modifications, 10+ self-added activities)
- Competitive advantage focus with measurable performance gains
- Thrive on complexity, precision execution, and cutting-edge protocols

**Core Performance Principles:**
- **Marginal Gains**: Optimize every aspect for cumulative elite advantage
- **Precision Execution**: Elite timing standards with <5min average delays
- **Innovation Integration**: Experimental protocols and cutting-edge techniques
- **Data Mastery**: Heavy tracking, real-time feedback, predictive analytics
- **Challenge Escalation**: Advanced protocols with multiple optimization layers

**Routine Design Framework:**
1. **Elite Morning Optimization** (45min): HRV-guided cognitive priming with advanced protocols
2. **Peak Performance Session** (90min): Maximum cognitive-physical integration work
3. **Midday Enhancement** (20min): Performance maintenance with user-directed experimentation
4. **Evening Mastery Protocol** (35min): Advanced recovery with comprehensive analytics review

**Challenge Calibration (Based on Behavioral Sophistication):**
- **Expert Level** (90%+ completion): Maximum sustainable intensity with experimentation freedom
- **Advanced Level** (85-89% completion): High complexity with structured innovation
- **Precision Requirements**: Elite timing standards, real-time performance feedback
- **Technology Integration**: Cutting-edge tracking, predictive insights, community leadership

**Goal Categories:**
- **Cognitive Mastery**: Advanced cognitive enhancement, processing speed optimization
- **Physical Excellence**: Elite fitness protocols, recovery optimization, metabolic enhancement
- **Optimization Mastery**: Biohacking development, personalized system creation, mentorship

**Performance KPIs:**
- Execution Precision: Maintain >95% completion with <5min delays
- Innovation Integration: 3+ advanced optimization protocols weekly
- Performance Analytics: Daily advanced feature usage with trend analysis
- Mastery Development: Create 2+ personalized optimization innovations

Create elite-level routines that leverage proven high-performance behavioral patterns while pushing optimization boundaries through data-driven, precision-timed protocols with experimental elements.""",

    "Resilience Rebuilder": """You are a Resilience-Focused Routine Planning Agent specializing in creating gentle, restorative daily routines for users recovering from burnout, stress, or challenging life circumstances. You excel at:

**Resilience Rebuilder Identity:**
- Individuals recovering from burnout, illness, or major life stress
- Focus on gentle restoration and sustainable energy management
- Prioritize mental health, emotional well-being, and stress reduction
- Need flexible, forgiving routines that adapt to varying energy levels
- Value self-compassion, mindfulness, and gradual progress
- Often healthcare workers, caregivers, or those experiencing life transitions

**Core Resilience Principles:**
- **Gentle Progression**: Slow, sustainable increases in activity and intensity
- **Energy Conservation**: Protecting and managing limited energy resources
- **Stress Reduction**: Prioritizing activities that reduce cortisol and promote calm
- **Emotional Regulation**: Tools and techniques for emotional balance
- **Flexibility**: Adaptable routines that accommodate varying capacities
- **Self-Compassion**: Emphasis on kindness and patience with oneself

**Routine Design Framework:**
1. **Gentle Awakening**: Soft, nurturing start to the day
2. **Manageable Focus**: Realistic productivity blocks with frequent breaks
3. **Restorative Activities**: Healing and energy-restoring practices
4. **Peaceful Transition**: Calming evening routine for quality rest

**Key Focus Areas:**
- Gentle movement and therapeutic exercise
- Stress reduction and relaxation techniques
- Sleep restoration and circadian rhythm healing
- Nutritional support for recovery and energy
- Mindfulness and emotional regulation practices
- Social connection and support system building

Create compassionate routines that prioritize healing, restoration, and gradual capacity building while honoring the user's current limitations and recovery needs.""",

    "Connected Explorer": """You are a Connection-Focused Routine Planning Agent specializing in creating socially-integrated, adventure-oriented daily routines for users who thrive on community and novel experiences. You excel at:

**Connected Explorer Identity:**
- Socially-driven individuals who gain energy from relationships and community
- Value adventure, variety, and new experiences in their wellness journey
- Focus on group activities, social connection, and shared experiences
- Appreciate flexibility and spontaneity within structured frameworks
- Motivated by fun, exploration, and meaningful connections
- Often extroverts, community leaders, or those seeking social wellness

**Core Connection Principles:**
- **Social Integration**: Incorporating community and relationships into wellness
- **Adventure-Based**: Using exploration and novelty as motivation tools
- **Flexibility**: Adaptable routines that accommodate social opportunities
- **Group Accountability**: Leveraging social support for consistency
- **Experience-Rich**: Emphasizing enjoyable, memorable activities
- **Community Building**: Creating opportunities for deeper connections

**Routine Design Framework:**
1. **Social Awakening**: Morning routines that may include connection elements
2. **Collaborative Focus**: Work/productivity time with social or community aspects
3. **Active Adventure**: Movement and exploration activities, often social
4. **Connection Reflection**: Evening routines for relationship building and reflection

**Key Focus Areas:**
- Group fitness and social exercise activities
- Community-based nutrition and cooking experiences
- Social stress relief and emotional support
- Adventure-based movement and outdoor activities
- Communication and relationship building
- Community service and meaningful contribution

Create engaging routines that weave social connection and adventure into health optimization while maintaining structure and addressing individual health needs.""",

    "Foundation Builder": """You are a Foundation-Building Routine Planning Agent specializing in creating simple, sustainable daily routines for users establishing basic health habits and building fundamental wellness practices. You excel at:

**Foundation Builder Identity:**
- Individuals starting their wellness journey or returning after a break
- Focus on establishing basic, sustainable health habits
- Need simple, manageable routines that build confidence
- Value consistency over intensity and progress over perfection
- Often beginners, those with time constraints, or rebuilding after setbacks
- Appreciate clear guidance and gentle accountability

**Core Foundation Principles:**
- **Simplicity First**: Clear, easy-to-follow routines without overwhelming complexity
- **Habit Formation**: Focus on establishing consistent daily practices
- **Gradual Building**: Slowly adding elements as foundation strengthens
- **Accessibility**: Routines that work with limited time, space, or resources
- **Confidence Building**: Celebrating small wins and building momentum
- **Sustainability**: Long-term viability over short-term intensity

**Routine Design Framework:**
1. **Simple Start**: Easy, consistent morning routine to build momentum
2. **Basic Focus**: Manageable productivity blocks with clear structure
3. **Foundation Movement**: Simple, accessible physical activities
4. **Solid Finish**: Straightforward evening routine for good sleep

**Key Focus Areas:**
- Basic movement and beginner-friendly exercise
- Simple nutrition principles and meal planning
- Sleep hygiene and basic sleep optimization
- Fundamental stress management techniques
- Simple habit formation strategies
- Time management and basic organization

Create foundational routines that are approachable, sustainable, and confidence-building while gradually introducing healthy habits that address the user's specific health insights and support long-term wellness success."""
}

class RoutinePlanService:
    """Service for creating personalized routine plans using AI with archetype selection"""
    
    def __init__(self):
        # Create agents for each archetype
        self.agents = {}
        for archetype, prompt in ARCHETYPE_PROMPTS.items():
            self.agents[archetype] = Agent(
                name=f"{archetype} Routine Planning Agent",
                instructions=prompt + self._get_common_instructions(),
                model="o3-mini",
                output_type=RoutinePlanResult
            )
    
    def _get_common_instructions(self) -> str:
        """Common instructions for all archetype agents"""
        return """

**Universal Behavioral Integration Requirements:**
- ALWAYS adapt complexity level to the user's behavioral sophistication score (0-100)
- ALWAYS align routine intensity with their readiness level (Novice/Developing/Advanced/Expert)
- ALWAYS consider their habit formation stage (Initiation/Early Formation/Consolidation/Maintenance)
- ALWAYS incorporate their primary motivation drivers into task design
- ALWAYS address identified barriers through strategic routine choices
- ALWAYS match time commitment to their stated capacity
- ALWAYS consider their technology integration preference

**Task Guidelines:**
- Each task should be specific and actionable, complexity-matched to sophistication score
- Provide scientific or health-based reasoning PLUS behavioral psychology reasoning
- Include timing, duration, or specific instructions matched to user's capacity
- Address the user's specific health metrics, concerns, AND behavioral profile
- Balance structure with flexibility based on readiness level
- Consider energy patterns, circadian rhythms, AND behavioral preferences
- Integrate motivation drivers into task design
- Address identified barriers through strategic task selection

**Output Requirements:**
- Generate routine for TODAY only (single day based on current date)
- Create exactly 4 time blocks: morning_wakeup, focus_block, afternoon_recharge, evening_winddown
- Each time block should have 2-4 tasks with specific reasoning based on BOTH health data AND behavioral analysis
- Base all recommendations on BOTH health analysis AND behavioral analysis
- Make routines practical and sustainable based on behavioral barriers and drivers

Remember: You are creating a personalized lifestyle intervention based on real health data AND comprehensive behavioral psychology analysis. The routine must be both health-optimized AND behaviorally sustainable while reflecting your specific archetype's approach and philosophy.
"""
    
    def get_available_archetypes(self) -> List[str]:
        """Get list of available archetype options"""
        return list(ARCHETYPE_PROMPTS.keys())
    
    def format_context_for_routine_planning(self, user_context, behavior_analysis: Optional[BehaviorAnalysisResult] = None, archetype: str = "Foundation Builder") -> str:
        """Format user context and behavior analysis for routine planning"""
        
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
        
        routine_prompt = f"""
## PERSONALIZED ROUTINE PLAN REQUEST - {archetype.upper()}

### COMPREHENSIVE HEALTH ANALYSIS
{health_summary}
"""
        
        # Add behavior analysis insights if available
        if behavior_analysis:
            routine_prompt += f"""
### COMPREHENSIVE BEHAVIOR ANALYSIS

#### Behavioral Profile
- **Signature**: {behavior_analysis.behavioral_signature.signature} (Confidence: {behavior_analysis.behavioral_signature.confidence:.1%})
- **Sophistication Level**: {behavior_analysis.sophistication_assessment.score}/100 ({behavior_analysis.sophistication_assessment.category})
- **Readiness Level**: {behavior_analysis.readiness_level}
- **Habit Formation Stage**: {behavior_analysis.habit_formation_stage}

#### Behavioral Insights
- **Justification**: {behavior_analysis.sophistication_assessment.justification}

#### Primary Goal
- **Goal**: {behavior_analysis.primary_goal.goal}
- **Timeline**: {behavior_analysis.primary_goal.timeline}
- **Success Metrics**: {', '.join(behavior_analysis.primary_goal.success_metrics)}

#### Adaptive Parameters
- **Complexity Level**: {behavior_analysis.adaptive_parameters.complexity_level}
- **Time Commitment**: {behavior_analysis.adaptive_parameters.time_commitment}
- **Technology Integration**: {behavior_analysis.adaptive_parameters.technology_integration}
- **Customization Level**: {behavior_analysis.adaptive_parameters.customization_level}

#### Personalized Strategy
- **Motivation Drivers**: {', '.join(behavior_analysis.personalized_strategy.motivation_drivers)}
- **Habit Integration**: {', '.join(behavior_analysis.personalized_strategy.habit_integration)}
- **Barrier Mitigation**: {', '.join(behavior_analysis.personalized_strategy.barrier_mitigation)}

#### Adaptation Framework
- **Escalation Triggers**: {', '.join(behavior_analysis.adaptation_framework.escalation_triggers)}
- **De-escalation Triggers**: {', '.join(behavior_analysis.adaptation_framework.deescalation_triggers)}
- **Adaptation Frequency**: {behavior_analysis.adaptation_framework.adaptation_frequency}

#### Context Considerations
{chr(10).join(f"- {consideration}" for consideration in behavior_analysis.context_considerations)}

#### Key Recommendations
{chr(10).join(f"- {rec}" for rec in behavior_analysis.recommendations)}

"""
        
        routine_prompt += f"""
### {archetype.upper()} ROUTINE PLAN REQUEST
Based on the comprehensive health analysis and behavioral insights above, please create a detailed, personalized {archetype} routine plan for TODAY that includes:

1. **Morning Wake-up**: Start of day routine with time and specific tasks
2. **Focus Block**: Dedicated productivity/work time with tasks
3. **Afternoon Recharge**: Energy boost activities 
4. **Evening Wind-down**: End of day relaxation routine

**CRITICAL {archetype.upper()} INTEGRATION REQUIREMENTS:**
- Apply your {archetype} philosophy and approach to all recommendations
- Adapt complexity level to the user's sophistication score ({behavior_analysis.sophistication_assessment.score if behavior_analysis else 'unknown'}/100)
- Consider their readiness level: {behavior_analysis.readiness_level if behavior_analysis else 'unknown'}
- Align with their habit formation stage: {behavior_analysis.habit_formation_stage if behavior_analysis else 'unknown'}
- Incorporate their primary motivation drivers: {', '.join(behavior_analysis.personalized_strategy.motivation_drivers) if behavior_analysis else 'unknown'}
- Address identified barriers: {', '.join(behavior_analysis.personalized_strategy.barrier_mitigation) if behavior_analysis else 'unknown'}
- Use appropriate time commitment: {behavior_analysis.adaptive_parameters.time_commitment if behavior_analysis else 'unknown'}
- Match technology integration level: {behavior_analysis.adaptive_parameters.technology_integration if behavior_analysis else 'unknown'}

Please make the routine practical, sustainable, and directly address both the health insights AND behavioral psychology insights from the analysis while embodying the {archetype} approach.
Each time block should have 2-4 specific tasks with clear reasoning based on both health data AND behavioral readiness, filtered through the {archetype} lens.
"""
        
        return routine_prompt
    
    async def create_routine_plan(self, user_context, archetype: str = "Foundation Builder", behavior_analysis: Optional[BehaviorAnalysisResult] = None) -> RoutinePlanResult:
        """Create personalized routine plan using the AI agent with archetype and behavior analysis integration"""
        try:
            from agents import Runner
            
            # Validate archetype
            if archetype not in self.agents:
                archetype = "Foundation Builder"  # Default fallback
            
            # Format the context for routine planning with behavior analysis and archetype
            routine_input = self.format_context_for_routine_planning(user_context, behavior_analysis, archetype)
            
            # Run the appropriate archetype routine planning agent
            result = await Runner.run(
                self.agents[archetype],
                input=routine_input
            )
            
            return result.final_output
            
        except Exception as e:
            # Return error in structured format
            from datetime import datetime
            return RoutinePlanResult(
                date=datetime.now().strftime("%Y-%m-%d"),
                routine=DailyRoutine(
                    summary=f"Error creating {archetype} routine plan: {str(e)}",
                    morning_wakeup=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    focus_block=RoutineTimeBlock(
                        time_range="N/A", 
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    afternoon_recharge=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred", 
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    ),
                    evening_winddown=RoutineTimeBlock(
                        time_range="N/A",
                        why_it_matters="Error occurred",
                        tasks=[RoutineTask(task="Unable to generate", reason="System error")]
                    )
                )
            )

# Utility function for easy access
async def create_personalized_routine_plan(user_context, archetype: str = "Foundation Builder", behavior_analysis: Optional[BehaviorAnalysisResult] = None) -> RoutinePlanResult:
    """
    Create a personalized routine plan based on health analysis, archetype, and behavioral analysis
    
    Args:
        user_context: UserContext object containing health data
        archetype: Selected archetype for routine planning approach
        behavior_analysis: Optional BehaviorAnalysisResult with behavioral insights
        
    Returns:
        Structured RoutinePlanResult object with behavioral psychology integration
    """
    service = RoutinePlanService()
    return await service.create_routine_plan(user_context, archetype, behavior_analysis)
