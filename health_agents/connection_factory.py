"""
Connection Factory - Automatically detects and uses the best available connection method
This allows existing code to work with either PostgreSQL or Supabase seamlessly
"""

import os
import asyncpg
from pathlib import Path
from dotenv import load_dotenv
from .supabase_adapter import connect_supabase_adapter


class ConnectionFactory:
    """
    Factory class that provides the best available database connection
    Tries Supabase first, falls back to PostgreSQL if needed
    """
    
    @staticmethod
    def _load_env():
        """Load environment variables from .env file"""
        current_dir = Path(__file__).parent.parent
        parent_dir = current_dir.parent
        env_locations = [
            current_dir / ".env",
            parent_dir / ".env",
            Path.cwd() / ".env"
        ]

        for env_path in env_locations:
            if env_path.exists():
                load_dotenv(env_path)
                break

    @staticmethod
    async def create_connection(database_url: str = None, **kwargs):
        """
        Create the best available database connection
        
        Priority:
        1. Supabase connection (if SUPABASE_URL and SUPABASE_KEY are available)
        2. PostgreSQL connection (if DATABASE_URL is available or provided)
        
        Returns a connection object that works with existing asyncpg code
        """
        ConnectionFactory._load_env()
        
        # Try Supabase first
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if supabase_url and supabase_key:
            try:
                print("[CONNECTING] Attempting Supabase connection...")
                connection = await connect_supabase_adapter(supabase_url, supabase_key)
                print("[SUCCESS] Connected via Supabase adapter with enhanced SQL parsing")
                return connection
            except Exception as e:
                print(f"[WARNING] Supabase connection failed: {e}")
                print("[CONNECTING] Falling back to PostgreSQL...")
        
        # Fallback to PostgreSQL
        db_url = database_url or os.getenv("DATABASE_URL")
        
        if not db_url:
            raise ValueError(
                "No database connection available. Please provide either:\n"
                "1. SUPABASE_URL and SUPABASE_KEY environment variables, or\n"
                "2. DATABASE_URL environment variable"
            )
        
        try:
            print(f"[CONNECTING] Attempting PostgreSQL connection...")
            connection = await asyncpg.connect(db_url, statement_cache_size=0, **kwargs)
            print("[SUCCESS] Connected via PostgreSQL")
            return connection
        except Exception as e:
            print(f"[ERROR] PostgreSQL connection failed: {e}")
            raise


# Convenience function that mimics asyncpg.connect
async def smart_connect(database_url: str = None, **kwargs):
    """
    Smart connection function that automatically chooses the best connection method
    Drop-in replacement for asyncpg.connect()
    """
    return await ConnectionFactory.create_connection(database_url, **kwargs)