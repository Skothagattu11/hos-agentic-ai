import time
import json
import os
from datetime import datetime, date, time as datetime_time
from agents import Runner, trace
from duckduckgo_search import DDGS
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.json import JSON
from rich.tree import Tree
from rich.prompt import Prompt
from health_agents.user_profile import get_user_profile_context
from health_agents.nutrition_plan_agent import create_personalized_nutrition_plan, NutritionPlanResult
from health_agents.routine_plan_agent import create_personalized_routine_plan, RoutinePlanResult, RoutinePlanService
from health_agents.behavior_analysis_agent import analyze_user_behavior, BehaviorAnalysisResult
from health_agents.analysis_history_manager import AnalysisHistoryManager

console = Console()

class HealthCoordinator:
    def __init__(self, profile_id: str, database_url: str = None):
        self.profile_id = profile_id
        self.analysis_history = AnalysisHistoryManager(database_url)
        self.routine_service = RoutinePlanService()

    def serialize_data(self, obj):
        """Helper method to serialize objects with datetime handling"""
        if obj is None:
            return None
            
        if hasattr(obj, 'dict'):
            data = obj.dict()
        elif hasattr(obj, '__dict__'):
            data = obj.__dict__
        else:
            return str(obj)
        
        # Convert datetime objects to ISO format strings
        def convert_datetime(item):
            if isinstance(item, datetime):
                return item.isoformat()
            elif isinstance(item, date):
                return item.isoformat()
            elif isinstance(item, datetime_time):
                return item.isoformat()
            elif isinstance(item, dict):
                return {k: convert_datetime(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [convert_datetime(v) for v in item]
            else:
                return item
        
        return convert_datetime(data)

    def get_next_file_number(self, prefix: str) -> int:
        """Get the next incremental number for input/output files"""
        import glob
        existing_files = glob.glob(f"{prefix}_*.txt")
        if not existing_files:
            return 1
        
        numbers = []
        for file in existing_files:
            try:
                # Extract number from filename like "input_1.txt" -> 1
                num_str = file.split('_')[1].split('.')[0]
                numbers.append(int(num_str))
            except (IndexError, ValueError):
                continue
        
        return max(numbers) + 1 if numbers else 1

    def log_input_data(self, user_context, latest_analysis, analysis_context):
        """Log input data (user profile and memory context) to input_N.txt in JSON format"""
        try:
            # Prepare input data for logging
            input_data = {
                "timestamp": datetime.now().isoformat(),
                "profile_id": self.profile_id,
                "user_profile": {
                    "date_range": {
                        "start_date": user_context.date_range['start_date'].isoformat() if user_context.date_range.get('start_date') else None,
                        "end_date": user_context.date_range['end_date'].isoformat() if user_context.date_range.get('end_date') else None,
                        "days": user_context.date_range.get('days')
                    },
                    "data_summary": {
                        "scores_count": len(user_context.scores),
                        "archetypes_count": len(user_context.archetypes),
                        "biomarkers_count": len(user_context.biomarkers)
                    },
                    "scores": [self.serialize_data(score) for score in user_context.scores],
                    "archetypes": [self.serialize_data(archetype) for archetype in user_context.archetypes],
                    "biomarkers": [self.serialize_data(biomarker) for biomarker in user_context.biomarkers]
                },
                "analysis_context": {
                    "has_previous_analysis": latest_analysis is not None,
                    "previous_analysis_date": latest_analysis.analysis_date.isoformat() if latest_analysis else None,
                    "previous_archetype": latest_analysis.archetype if latest_analysis else None,
                    "user_preferences": latest_analysis.user_preferences if latest_analysis else {},
                    "health_goals": latest_analysis.health_goals if latest_analysis else {},
                    "dietary_restrictions": latest_analysis.dietary_restrictions if latest_analysis else {},
                    "lifestyle_context": latest_analysis.lifestyle_context if latest_analysis else {},
                    "medical_conditions": latest_analysis.medical_conditions if latest_analysis else {},
                    "formatted_context": analysis_context
                }
            }
            
            # Get next file number and write to input_N.txt
            file_number = self.get_next_file_number("input")
            filename = f"input_{file_number}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(input_data, indent=2, ensure_ascii=False, default=str))
            
            console.print(f"[dim]📝 Input data logged to {filename}[/dim]")
            
        except Exception as e:
            console.print(f"[red]⚠️ Error logging input data: {str(e)}[/red]")

    def log_output_data(self, user_context, behavior_analysis=None, nutrition_plan=None, routine_plan=None):
        """Log output data (user context summary, behavior analysis, nutrition plan, routine plan) to output_N.txt in JSON format"""
        try:
            # Create a summary of user_context data
            user_data_summary = {
                "date_range": {
                    "start_date": user_context.date_range['start_date'].isoformat(),
                    "end_date": user_context.date_range['end_date'].isoformat(),
                    "days": user_context.date_range['days']
                },
                "data_counts": {
                    "scores": len(user_context.scores),
                    "biomarkers": len(user_context.biomarkers),
                    "archetypes": len(user_context.archetypes)
                },
                "score_types": list(set(s.type for s in user_context.scores[:10])) if user_context.scores else [],
                "biomarker_categories": list(set(b.category for b in user_context.biomarkers[:10])) if user_context.biomarkers else [],
                "archetype_names": list(set(a.name for a in user_context.archetypes[:5])) if user_context.archetypes else []
            }
            
            # Prepare output data for logging
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "profile_id": self.profile_id,
                "user_data_summary": user_data_summary,
                "behavior_analysis": None,
                "nutrition_plan": None,
                "routine_plan": None
            }
            
            # Add behavior analysis if available
            if behavior_analysis:
                try:
                    output_data["behavior_analysis"] = self.serialize_data(behavior_analysis)
                except Exception as e:
                    output_data["behavior_analysis"] = f"Error serializing behavior analysis: {str(e)}"
            
            # Add nutrition plan if available
            if nutrition_plan:
                try:
                    output_data["nutrition_plan"] = self.serialize_data(nutrition_plan)
                except Exception as e:
                    output_data["nutrition_plan"] = f"Error serializing nutrition plan: {str(e)}"
            
            # Add routine plan if available
            if routine_plan:
                try:
                    output_data["routine_plan"] = self.serialize_data(routine_plan)
                except Exception as e:
                    output_data["routine_plan"] = f"Error serializing routine plan: {str(e)}"
            
            # Get next file number and write to output_N.txt  
            file_number = self.get_next_file_number("output")
            filename = f"output_{file_number}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json.dumps(output_data, indent=2, ensure_ascii=False, default=str))
            
            console.print(f"[dim]📝 Output data logged to {filename}[/dim]")
            
        except Exception as e:
            console.print(f"[red]⚠️ Error logging output data: {str(e)}[/red]")

    def display_routine_plan(self, routine_result: RoutinePlanResult, selected_archetype: str = ""):
        """Display structured routine plan data"""
        try:
            tree = Tree(f"📅 🏃‍♀️ Personalized Routine Plan ({selected_archetype})")
            
            # Add date and summary
            day_tree = tree.add(f"[bold cyan]{routine_result.date}[/bold cyan]")
            day_tree.add(f"[yellow]📝 Summary:[/yellow] {routine_result.routine.summary}")
            
            # Add each time block
            time_blocks = [
                ("Morning Wake-up", routine_result.routine.morning_wakeup),
                ("Focus Block", routine_result.routine.focus_block),
                ("Afternoon Recharge", routine_result.routine.afternoon_recharge),
                ("Evening Wind-down", routine_result.routine.evening_winddown)
            ]
            
            for block_name, block_data in time_blocks:
                block_tree = day_tree.add(f"[bold magenta]⏰ {block_name}[/bold magenta]")
                block_tree.add(f"🕐 [bold blue]{block_data.time_range}[/bold blue]")
                block_tree.add(f"[dim]💡 Why: {block_data.why_it_matters}[/dim]")
                
                for i, task in enumerate(block_data.tasks, 1):
                    task_tree = block_tree.add(f"[bold white]{i}. {task.task}[/bold white]")
                    task_tree.add(f"[dim italic]→ {task.reason}[/dim italic]")
            
            console.print(Panel(tree, title=f"🏃‍♀️ Personalized Routine Plan ({selected_archetype})", border_style="magenta", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying routine plan: {str(e)}[/red]")

    def display_nutrition_plan(self, nutrition_result: NutritionPlanResult):
        """Display structured detailed nutrition plan data"""
        try:
            tree = Tree(f"📅 🥗 Personalized Detailed Nutrition Plan")
            
            # Add date and summary
            day_tree = tree.add(f"[bold cyan]{nutrition_result.date}[/bold cyan]")
            day_tree.add(f"[yellow]📝 Summary:[/yellow] {nutrition_result.nutrition.summary}")
            
            # Add comprehensive nutritional targets
            nutrition_tree = day_tree.add("[green]🥗 Daily Nutritional Targets[/green]")
            info = nutrition_result.nutrition.nutritional_info
            nutrition_tree.add(f"• Calories: [bold]{info.calories}[/bold]")
            nutrition_tree.add(f"• Protein: [bold]{info.protein}g ({info.protein_percent}%)[/bold]")
            nutrition_tree.add(f"• Carbs: [bold]{info.carbs}g ({info.carbs_percent}%)[/bold]")
            nutrition_tree.add(f"• Fat: [bold]{info.fat}g ({info.fat_percent}%)[/bold]")
            nutrition_tree.add(f"• Fiber: [bold]{info.fiber}g[/bold]")
            nutrition_tree.add(f"• Sugar: [bold]{info.sugar}g[/bold]")
            nutrition_tree.add(f"• Sodium: [bold]{info.sodium}mg[/bold]")
            nutrition_tree.add(f"• Potassium: [bold]{info.potassium}mg[/bold]")
            
            # Add vitamins
            vitamins_tree = nutrition_tree.add("[magenta]💊 Key Vitamins & Minerals[/magenta]")
            vitamins_tree.add(f"• Vitamin D: [bold]{info.vitamins.Vitamin_D}[/bold]")
            vitamins_tree.add(f"• Calcium: [bold]{info.vitamins.Calcium}[/bold]")
            vitamins_tree.add(f"• Iron: [bold]{info.vitamins.Iron}[/bold]")
            vitamins_tree.add(f"• Magnesium: [bold]{info.vitamins.Magnesium}[/bold]")
            
            # Add each meal block (7 blocks)
            meal_blocks = [
                ("Early Morning", nutrition_result.nutrition.Early_Morning),
                ("Breakfast", nutrition_result.nutrition.Breakfast),
                ("Morning Snack", nutrition_result.nutrition.Morning_Snack),
                ("Lunch", nutrition_result.nutrition.Lunch),
                ("Afternoon Snack", nutrition_result.nutrition.Afternoon_Snack),
                ("Dinner", nutrition_result.nutrition.Dinner),
                ("Evening Snack", nutrition_result.nutrition.Evening_Snack)
            ]
            
            for meal_name, meal_data in meal_blocks:
                meal_tree = day_tree.add(f"[bold magenta]🍽️ {meal_name}[/bold magenta]")
                meal_tree.add(f"🕐 [bold blue]{meal_data.time_range}[/bold blue]")
                meal_tree.add(f"[dim]💡 Tip: {meal_data.nutrition_tip}[/dim]")
                
                # Add individual meals
                for i, meal in enumerate(meal_data.meals, 1):
                    meal_item_tree = meal_tree.add(f"[bold white]{i}. {meal.name}[/bold white]")
                    meal_item_tree.add(f"[green]📋 Details: {meal.details}[/green]")
                    meal_item_tree.add(f"[yellow]🔥 Calories: {meal.calories} | Protein: {meal.protein}g[/yellow]")
                    meal_item_tree.add(f"[cyan]📊 Macros: Carbs {meal.macros.carbs}g | Fat {meal.macros.fat}g[/cyan]")
            
            console.print(Panel(tree, title="🥗 Personalized Detailed Nutrition Plan", border_style="blue", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying nutrition plan: {str(e)}[/red]")

    def display_behavior_analysis(self, behavior_result: BehaviorAnalysisResult):
        """Display structured behavior analysis data"""
        try:
            tree = Tree(f"📅 🧠 Behavioral Analysis Report")
            
            # Add date and user
            main_tree = tree.add(f"[bold cyan]{behavior_result.analysis_date} - User: {behavior_result.user_id}[/bold cyan]")
            
            # Behavioral Signature
            signature_tree = main_tree.add(f"[bold magenta]🎯 Behavioral Signature[/bold magenta]")
            signature_tree.add(f"[bold white]'{behavior_result.behavioral_signature.signature}'[/bold white]")
            signature_tree.add(f"[dim]Confidence: {behavior_result.behavioral_signature.confidence:.1%}[/dim]")
            
            # Sophistication Assessment
            sophistication_tree = main_tree.add(f"[bold green]📊 Sophistication Assessment[/bold green]")
            sophistication_tree.add(f"Score: [bold]{behavior_result.sophistication_assessment.score}/100[/bold] ([bold]{behavior_result.sophistication_assessment.category}[/bold])")
            sophistication_tree.add(f"[dim italic]{behavior_result.sophistication_assessment.justification}[/dim italic]")
            
            # Primary Goal
            goal_tree = main_tree.add(f"[bold blue]🎯 Primary Goal[/bold blue]")
            goal_tree.add(f"[bold white]{behavior_result.primary_goal.goal}[/bold white]")
            goal_tree.add(f"Timeline: [bold]{behavior_result.primary_goal.timeline}[/bold]")
            
            success_tree = goal_tree.add("[yellow]📈 Success Metrics[/yellow]")
            for metric in behavior_result.primary_goal.success_metrics:
                success_tree.add(f"• {metric}")
            
            # Adaptive Parameters
            adaptive_tree = main_tree.add(f"[bold purple]⚙️ Adaptive Parameters[/bold purple]")
            adaptive_tree.add(f"• Complexity: [bold]{behavior_result.adaptive_parameters.complexity_level}[/bold]")
            adaptive_tree.add(f"• Time Commitment: [bold]{behavior_result.adaptive_parameters.time_commitment}[/bold]")
            adaptive_tree.add(f"• Technology Integration: [bold]{behavior_result.adaptive_parameters.technology_integration}[/bold]")
            adaptive_tree.add(f"• Customization Level: [bold]{behavior_result.adaptive_parameters.customization_level}[/bold]")
            
            # Readiness & Stage
            status_tree = main_tree.add(f"[bold yellow]📋 Current Status[/bold yellow]")
            status_tree.add(f"Readiness Level: [bold]{behavior_result.readiness_level}[/bold]")
            status_tree.add(f"Habit Formation Stage: [bold]{behavior_result.habit_formation_stage}[/bold]")
            
            # Recommendations
            rec_tree = main_tree.add(f"[bold red]💡 Key Recommendations[/bold red]")
            for i, rec in enumerate(behavior_result.recommendations[:5], 1):  # Show top 5
                rec_tree.add(f"{i}. {rec}")
            
            console.print(Panel(tree, title="🧠 Behavioral Analysis Report", border_style="blue", padding=(1, 2)))
            
        except Exception as e:
            console.print(f"[red]Error displaying behavior analysis: {str(e)}[/red]")

    async def run_analysis(self, selected_archetype: str = "Foundation Builder", days: int = 7):
        """Complete health analysis workflow with nutrition and routine planning"""
        
        # Initialize variables to store results for logging
        nutrition_plan = None
        routine_plan = None
        behavior_analysis = None
        
        with trace("Health Analysis Workflow"):
            console.print(f"[bold cyan]🏥 Starting Comprehensive Health Analysis for Profile: {self.profile_id}[/bold cyan]")
            
            # Step 0: Initialize analysis history and retrieve previous analysis
            console.print("[cyan]🧠 Retrieving analysis history and context...[/cyan]")
            try:
                await self.analysis_history.connect()
                latest_analysis = await self.analysis_history.get_latest_analysis(self.profile_id)
                analysis_count = await self.analysis_history.get_analysis_count(self.profile_id)
                
                # Determine data fetching strategy and analysis type
                if latest_analysis and analysis_count > 0:
                    # Follow-up mode: 1 day of data
                    data_days = 1
                    analysis_type = "Follow-up Analysis"
                    has_previous_analysis = True
                    console.print(Panel(
                        f"[bold green]✅ Analysis History Retrieved[/bold green]\n"
                        f"[yellow]Previous Analyses:[/yellow] {analysis_count}\n"
                        f"[yellow]Last Analysis:[/yellow] {latest_analysis.analysis_date}\n"
                        f"[yellow]Last Archetype:[/yellow] {latest_analysis.archetype}\n"
                        f"[yellow]Has Nutrition Plan:[/yellow] {'Yes' if latest_analysis.nutrition_plan else 'No'}\n"
                        f"[yellow]Has Routine Plan:[/yellow] {'Yes' if latest_analysis.routine_plan else 'No'}\n"
                        f"[yellow]Data Fetching:[/yellow] {data_days} day(s) (Follow-up mode)",
                        title="🧠 Analysis History Summary"
                    ))
                else:
                    # Initial mode: 7 days of data
                    data_days = days
                    analysis_type = "Initial Analysis"
                    has_previous_analysis = False
                    console.print(Panel(
                        f"[bold green]✅ New User Analysis Setup[/bold green]\n"
                        f"[yellow]Analysis Type:[/yellow] {analysis_type}\n"
                        f"[yellow]Data Fetching:[/yellow] {data_days} day(s) (Complete profile mode)",
                        title="🧠 Analysis History Summary"
                    ))
                
            except Exception as e:
                console.print(f"[bold red]❌ Error retrieving analysis history: {str(e)}[/bold red]")
                latest_analysis = None
                data_days = days
                analysis_type = "Initial Analysis"
                has_previous_analysis = False
            
            # Step 1: Fetch user profile data
            console.print(f"[cyan]📊 Fetching user health data for {data_days} day(s)...[/cyan]")
            try:
                user_context = await get_user_profile_context(self.profile_id, days=data_days)
                
                console.print(Panel(
                    f"[bold green]✅ Data Retrieved Successfully[/bold green]\n"
                    f"[yellow]Analysis Type:[/yellow] {analysis_type}\n"
                    f"[yellow]Time Period:[/yellow] {user_context.date_range['start_date']} to {user_context.date_range['end_date']}\n"
                    f"[yellow]Duration:[/yellow] {data_days} day(s)\n"
                    f"[yellow]Data Summary:[/yellow]\n"
                    f"  • Scores: {len(user_context.scores)} records\n"
                    f"  • Archetypes: {len(user_context.archetypes)} records\n"
                    f"  • Biomarkers: {len(user_context.biomarkers)} records",
                    title="📊 Health Data Summary"
                ))
                
            except Exception as e:
                console.print(f"[bold red]❌ Error fetching user data: {str(e)}[/bold red]")
                return
            
            # Log input data (user profile and memory context)
            console.print("[cyan]📝 Logging input data...[/cyan]")
            try:
                # Format analysis context for analysis
                analysis_context = ""
                previous_analysis = {}
                if latest_analysis:
                    analysis_context = f"Previous analysis from {latest_analysis.analysis_date}: {latest_analysis.archetype} archetype"
                    if has_previous_analysis:
                        console.print("[dim]📝 Including previous analysis context for follow-up analysis...[/dim]")
                        # Extract previous analysis data
                        if latest_analysis.behavior_analysis:
                            previous_analysis["behavior_analysis"] = latest_analysis.behavior_analysis
                    else:
                        console.print("[dim]📝 Initial analysis - no previous context available...[/dim]")
                
                # Log input data before analysis  
                self.log_input_data(user_context, latest_analysis, analysis_context)
                
            except Exception as e:
                console.print(f"[red]⚠️ Error logging input data: {str(e)}[/red]")
                analysis_context = ""
                previous_analysis = {}

            # Step 2: Run comprehensive behavior analysis
            console.print("[cyan]🧠 Running comprehensive behavior analysis...[/cyan]")
            try:
                with console.status("[bold cyan]Analyzing behavioral patterns with AI...") as status:
                    # Pass previous behavior analysis if available for follow-up mode
                    previous_behavior_data = previous_analysis.get("behavior_analysis") if has_previous_analysis else None
                    behavior_analysis = await analyze_user_behavior(
                        user_context, 
                        analysis_context, 
                        previous_behavior_data
                    )
                
                console.print("[bold green]✅ Behavior analysis complete![/bold green]\n")
                
                # Display the behavior analysis results
                self.display_behavior_analysis(behavior_analysis)
                
                # Note: Behavior analysis will be saved to analysis history at the end
                
            except Exception as e:
                console.print(f"[bold red]❌ Error during behavior analysis: {str(e)}[/bold red]")
                behavior_analysis = None
            
            # Step 4: Create personalized nutrition plan
            console.print("[cyan]🥗 Creating personalized nutrition plan...[/cyan]")
            try:
                with console.status("[bold cyan]Generating nutrition recommendations...") as status:
                    nutrition_plan = await create_personalized_nutrition_plan(user_context, behavior_analysis)
                
                console.print("[bold green]✅ Nutrition plan created![/bold green]\n")
                
                # Display the nutrition plan
                self.display_nutrition_plan(nutrition_plan)
                
                # Note: Nutrition plan will be saved to analysis history at the end
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating nutrition plan: {str(e)}[/bold red]")
                nutrition_plan = None
            
            # Step 5: Create personalized routine plan (with behavior analysis integration)
            console.print(f"[cyan]🏃‍♀️ Creating personalized routine plan with behavioral insights for {selected_archetype}...[/cyan]")
            try:
                with console.status("[bold cyan]Generating behaviorally-informed routine recommendations...") as status:
                    routine_plan = await create_personalized_routine_plan(user_context, selected_archetype, behavior_analysis) # Changed to user_context
                
                console.print("[bold green]✅ Behaviorally-informed routine plan created![/bold green]\n")
                
                # Display the routine plan
                self.display_routine_plan(routine_plan, selected_archetype)
                
                # Note: Routine plan will be saved to analysis history at the end
                
            except Exception as e:
                console.print(f"[bold red]❌ Error creating routine plan: {str(e)}[/bold red]")
                routine_plan = None
            
            # Step 6: Create analysis history record
            console.print("[cyan]💾 Creating analysis history record...[/cyan]")
            try:
                # Create comprehensive analysis record
                analysis_id = await self.analysis_history.create_analysis_record(
                    self.profile_id,
                    selected_archetype,
                    behavior_analysis,
                    nutrition_plan,
                    routine_plan,
                    user_context
                )
                console.print(f"[green]✅ Analysis record created: {analysis_id}[/green]")
                
            except Exception as e:
                console.print(f"[red]⚠️ Error creating analysis record: {str(e)}[/red]")
            
            # Log complete output data (analysis + behavior analysis + nutrition plan + routine plan)
            console.print("[cyan]📝 Logging complete output data...[/cyan]")
            try:
                self.log_output_data(user_context, behavior_analysis, nutrition_plan, routine_plan) # Changed to user_context
            except Exception as e:
                console.print(f"[red]⚠️ Error logging output data: {str(e)}[/red]")
            
            # Final summary
            console.print("\n" + "="*80)
            console.print("[bold green]🎉 COMPREHENSIVE HEALTH ANALYSIS COMPLETE! 🎉[/bold green]")
            console.print("="*80)
            console.print(f"[cyan]✅ Health metrics analyzed for profile: {self.profile_id}[/cyan]")
            console.print(f"[cyan]✅ Comprehensive behavior analysis completed (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ Personalized nutrition plan generated (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ Behaviorally-informed routine plan generated (Structured Output)[/cyan]")
            console.print(f"[cyan]✅ User memory updated with latest results[/cyan]")
            console.print(f"[cyan]✅ Selected Archetype: {selected_archetype}[/cyan]")
            console.print(f"[cyan]✅ Analysis Type: {analysis_type}[/cyan]")
            console.print(f"[dim]Analysis period: {user_context.date_range['start_date']} to {user_context.date_range['end_date']}[/dim]")
            console.print("="*80)
            
            # Cleanup
            try:
                await self.analysis_history.disconnect()
            except Exception as e:
                console.print(f"[dim]⚠️ Warning: Error disconnecting from database: {str(e)}[/dim]")