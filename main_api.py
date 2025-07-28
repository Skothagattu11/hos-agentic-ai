#!/usr/bin/env python3
"""
Health Analysis Agent API Entry Point
Accepts command line arguments for user_id and archetype
"""

import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from coordinator import HealthCoordinator

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

def main():
    if len(sys.argv) != 3:
        print("Usage: python main_api.py <user_id> <archetype>")
        print("Archetypes: Foundation Builder, Transformation Seeker, Systematic Improver, Peak Performer, Resilience Rebuilder, Connected Explorer")
        sys.exit(1)
    
    user_id = sys.argv[1]
    archetype = sys.argv[2]
    
    # Validate archetype
    valid_archetypes = [
        "Foundation Builder",
        "Transformation Seeker", 
        "Systematic Improver",
        "Peak Performer",
        "Resilience Rebuilder",
        "Connected Explorer"
    ]
    
    if archetype not in valid_archetypes:
        print(f"[ERROR] Invalid archetype: {archetype}")
        print(f"Valid archetypes: {', '.join(valid_archetypes)}")
        sys.exit(1)
    
    print("Starting health analysis...")
    print(f"Selected archetype: {archetype}")
    print("Initializing analysis systems...")
    
    # Run the analysis
    asyncio.run(run_analysis_wrapper(user_id, archetype))

async def run_analysis_wrapper(user_id: str, archetype: str):
    """Async wrapper for running the health analysis"""
    try:
        # Get database connection options from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        database_url = os.getenv("DATABASE_URL")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Debug: Print environment variables (without exposing sensitive data)
    # Log debug info to server logs instead of stdout
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SUPABASE_URL loaded: {'Yes' if supabase_url else 'No'}")
        logger.info(f"SUPABASE_KEY loaded: {'Yes' if supabase_key else 'No'}")
        logger.info(f"DATABASE_URL loaded: {'Yes' if database_url else 'No'}")
        logger.info(f"OPENAI_API_KEY loaded: {'Yes' if openai_api_key else 'No'}")
        
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
        
        # Initialize the coordinator (it will use smart connection)
        coordinator = HealthCoordinator(user_id, database_url)
        
        # Run the analysis
        await coordinator.run_analysis(archetype)
        
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 