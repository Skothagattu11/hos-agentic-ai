from dotenv import load_dotenv
from rich.console import Console
import asyncio
from rich.prompt import Prompt
from coordinator import HealthCoordinator
from health_agents.routine_plan_agent import RoutinePlanService
import os

load_dotenv()

console = Console()

def get_archetype_selection():
    """Display archetype options and get user selection at the beginning"""
    try:
        # Get available archetypes
        service = RoutinePlanService()
        available_archetypes = service.get_available_archetypes()
        
        # Display archetype selection panel
        archetype_descriptions = {
            "Transformation Seeker": "🚀 Ambitious individuals ready for major lifestyle changes and dramatic improvement",
            "Systematic Improver": "🔬 Detail-oriented, methodical approach with evidence-based, incremental progress",
            "Peak Performer": "🏆 High-achieving individuals seeking elite-level performance optimization",
            "Resilience Rebuilder": "🌱 Gentle restoration and recovery-focused approach for burnout or stress recovery",
            "Connected Explorer": "🌍 Social connection and adventure-oriented wellness with community focus",
            "Foundation Builder": "🏗️ Simple, sustainable basics for beginners or those rebuilding health habits"
        }
        
        # Show archetype options
        console.print("\n" + "="*80)
        console.print("[bold cyan]🎯 SELECT YOUR ROUTINE PLAN ARCHETYPE[/bold cyan]")
        console.print("="*80)
        console.print("[dim]Choose the approach that best matches your personality and wellness goals:[/dim]\n")
        
        # Display options
        for i, archetype in enumerate(available_archetypes, 1):
            description = archetype_descriptions.get(archetype, "Routine planning approach")
            console.print(f"[bold yellow]{i}.[/bold yellow] [bold]{archetype}[/bold]")
            console.print(f"   {description}\n")
        
        # Get user choice
        while True:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Choose your archetype[/bold cyan] (enter number 1-6)",
                    default="6"
                )
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_archetypes):
                    selected_archetype = available_archetypes[choice_num - 1]
                    console.print(f"\n[bold green]✅ Selected: {selected_archetype}[/bold green]")
                    console.print("="*80 + "\n")
                    return selected_archetype
                else:
                    console.print("[red]❌ Invalid choice. Please enter a number between 1-6.[/red]")
                    
            except ValueError:
                console.print("[red]❌ Invalid input. Please enter a number.[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️ Selection cancelled. Using Foundation Builder as default.[/yellow]")
                return "Foundation Builder"
                
    except Exception as e:
        console.print(f"[red]❌ Error during archetype selection: {str(e)}[/red]")
        console.print("[yellow]⚠️ Using Foundation Builder as default.[/yellow]")
        return "Foundation Builder"

async def main() -> None:
    console.print("[bold green]🏥 Welcome to the Health Analysis System![/bold green]")

    # Basic environment check
    if not os.getenv("DATABASE_URL") or not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]❌ Missing required environment variables (DATABASE_URL, OPENAI_API_KEY)[/bold red]")
        return

    # Get user input
    profile_id = Prompt.ask("Enter the user profile ID to analyze")
    if not profile_id.strip():
        console.print("[bold red]Please enter a valid profile ID.[/bold red]")
        return
    
    # Get archetype selection
    selected_archetype = get_archetype_selection()

    # Initialize and run health coordinator with selected archetype
    health_coordinator = HealthCoordinator(profile_id=profile_id)
    await health_coordinator.run_analysis(selected_archetype=selected_archetype)

if __name__ == "__main__":
    asyncio.run(main())