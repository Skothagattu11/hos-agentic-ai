#!/usr/bin/env python3
"""
Health Analysis System - Main Entry Point
Supports both interactive CLI mode and API command-line mode
"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from coordinator import HealthCoordinator
from health_agents.routine_plan_agent import RoutinePlanService

# Load environment variables from .env file
# Check multiple locations for .env file
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
env_locations = [
    current_dir / ".env",
    parent_dir / ".env",
    Path.cwd() / ".env"
]

env_loaded = False
for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        import logging
        logging.getLogger(__name__).info(f"Loaded .env from: {env_path}")
        break

if not env_loaded:
    import logging
    logging.getLogger(__name__).info("No .env file found. Please create one using env.example as template.")
    load_dotenv()  # Load from system environment

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

def validate_archetype(archetype: str) -> bool:
    """Validate archetype selection"""
    valid_archetypes = [
        "Foundation Builder",
        "Transformation Seeker", 
        "Systematic Improver",
        "Peak Performer",
        "Resilience Rebuilder",
        "Connected Explorer"
    ]
    return archetype in valid_archetypes

async def run_api_mode(user_id: str, archetype: str):
    """Run analysis in API mode (command-line arguments)"""
    try:
        # Get database connection options from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        database_url = os.getenv("DATABASE_URL")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Check for database connection options
        if not (supabase_url and supabase_key) and not database_url:
            print("[ERROR] No database connection configured.")
            print("Please provide either:")
            print("  1. SUPABASE_URL and SUPABASE_KEY, or")
            print("  2. DATABASE_URL")
            print("See env.example file for template.")
            sys.exit(1)
        
        if not openai_api_key:
            print("[ERROR] OPENAI_API_KEY not found in environment variables.")
            print("Please add your OpenAI API key to the .env file.")
            print("See env.example file for template.")
            sys.exit(1)
        
        print("Starting health analysis...")
        print(f"Selected archetype: {archetype}")
        print("Initializing analysis systems...")
        
        # Initialize the coordinator (it will use smart connection)
        coordinator = HealthCoordinator(user_id, database_url)
        
        # Run the analysis
        await coordinator.run_analysis(archetype)
        
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        sys.exit(1)

async def run_interactive_mode():
    """Run analysis in interactive CLI mode"""
    console.print("[bold green]🏥 Welcome to the Health Analysis System![/bold green]")

    # Basic environment check - check for Supabase or DATABASE_URL
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    database_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not ((supabase_url and supabase_key) or database_url):
        console.print("[bold red]❌ Missing database configuration. Please provide either:[/bold red]")
        console.print("  1. SUPABASE_URL and SUPABASE_KEY, or")
        console.print("  2. DATABASE_URL")
        return
        
    if not openai_api_key:
        console.print("[bold red]❌ Missing OPENAI_API_KEY environment variable[/bold red]")
        return

    # Get user input
    profile_id = Prompt.ask("Enter the user profile ID to analyze")
    if not profile_id.strip():
        console.print("[bold red]Please enter a valid profile ID.[/bold red]")
        return
    
    # Get archetype selection
    selected_archetype = get_archetype_selection()

    # Initialize and run health coordinator with selected archetype
    health_coordinator = HealthCoordinator(profile_id=profile_id, database_url=database_url)
    await health_coordinator.run_analysis(selected_archetype=selected_archetype)

async def main():
    """Main entry point - supports both API and interactive modes"""
    # Check if running in API mode (command-line arguments)
    if len(sys.argv) == 3:
        user_id = sys.argv[1]
        archetype = sys.argv[2]
        
        # Validate archetype
        if not validate_archetype(archetype):
            print(f"[ERROR] Invalid archetype: {archetype}")
            print("Valid archetypes: Foundation Builder, Transformation Seeker, Systematic Improver, Peak Performer, Resilience Rebuilder, Connected Explorer")
            sys.exit(1)
        
        # Run in API mode
        await run_api_mode(user_id, archetype)
    
    elif len(sys.argv) == 1:
        # Run in interactive mode
        await run_interactive_mode()
    
    else:
        print("Usage:")
        print("  Interactive mode: python main.py")
        print("  API mode: python main.py <user_id> <archetype>")
        print("Archetypes: Foundation Builder, Transformation Seeker, Systematic Improver, Peak Performer, Resilience Rebuilder, Connected Explorer")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())