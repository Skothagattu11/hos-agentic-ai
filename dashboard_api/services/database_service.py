from typing import Optional, Dict, Any, List
import os
import logging
from datetime import datetime
from health_agents.analysis_history_manager import AnalysisHistoryManager

# Try to import supabase, make it optional for now
try:
    from supabase import create_client, Client as SupabaseClient
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    SupabaseClient = None

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database access (PostgreSQL + Supabase)"""
    
    def __init__(self):
        # Existing PostgreSQL connection via analysis_history_manager
        self.analysis_history = AnalysisHistoryManager()
        
        # Initialize Supabase client if available
        self.supabase: Optional[SupabaseClient] = None
        if SUPABASE_AVAILABLE:
            try:
                supabase_url = os.environ.get("SUPABASE_URL")
                supabase_key = os.environ.get("SUPABASE_KEY")
                
                if supabase_url and supabase_key:
                    self.supabase = create_client(supabase_url, supabase_key)
                    logger.info("Supabase client initialized successfully")
                else:
                    logger.warning("SUPABASE_URL or SUPABASE_KEY not found in environment")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.supabase = None
        else:
            logger.warning("Supabase package not available")
    
    async def get_all_profile_ids(self) -> List[str]:
        """Get all unique user profile IDs"""
        try:
            # Try to get from analysis_memory first (PostgreSQL)
            result = []
            
            # Use existing analysis_history connection
            connection = self.analysis_history.connection
            if hasattr(connection, 'client'):
                # Direct Supabase client call
                response = connection.client.table('analysis_memory').select('profile_id').execute()
                if response.data:
                    profile_ids = list(set([row['profile_id'] for row in response.data]))
                    result.extend(profile_ids)
                    logger.debug(f"Found {len(profile_ids)} profile IDs from analysis_memory")
            
            # Fallback: try direct Supabase connection for profiles table
            if not result and self.supabase:
                try:
                    response = self.supabase.table('profiles').select('id').execute()
                    if response.data:
                        profile_ids = [row['id'] for row in response.data]
                        result.extend(profile_ids)
                        logger.debug(f"Found {len(profile_ids)} profile IDs from profiles table")
                except Exception as e:
                    logger.error(f"Error querying profiles table: {e}")
            
            return list(set(result))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting profile IDs: {e}")
            return []
    
    async def get_user_profile_from_profiles_table(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from profiles table"""
        try:
            if self.supabase:
                response = self.supabase.table('profiles').select('*').eq('id', profile_id).limit(1).execute()
                if response.data:
                    return response.data[0]
            
            # Fallback: try via analysis_history connection if it has Supabase client
            connection = self.analysis_history.connection
            if hasattr(connection, 'client'):
                response = connection.client.table('profiles').select('*').eq('id', profile_id).limit(1).execute()
                if response.data:
                    return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile for {profile_id}: {e}")
            return None
    
    async def get_user_analysis_summary(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user analysis summary from analysis_memory"""
        try:
            # Use existing analysis_history_manager functionality
            latest_analysis = await self.analysis_history.get_latest_analysis(profile_id)
            analysis_count = await self.analysis_history.get_analysis_count(profile_id)
            
            if not latest_analysis and analysis_count == 0:
                return None
            
            # Count initial vs follow-up analyses
            initial_count = 0
            follow_up_count = 0
            
            # Get all analyses for this user to count types
            connection = self.analysis_history.connection
            if hasattr(connection, 'client'):
                response = connection.client.table('analysis_memory')\
                    .select('analysis_type')\
                    .eq('profile_id', profile_id)\
                    .execute()
                
                if response.data:
                    for row in response.data:
                        if row.get('analysis_type') == 'initial':
                            initial_count += 1
                        elif row.get('analysis_type') == 'follow_up':
                            follow_up_count += 1
            
            return {
                "total_analyses": analysis_count,
                "initial_analyses": initial_count,
                "follow_up_analyses": follow_up_count,
                "latest_analysis_date": latest_analysis.get('analysis_date') if latest_analysis else None,
                "latest_archetype": latest_analysis.get('archetype') if latest_analysis else None
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis summary for {profile_id}: {e}")
            return None
    
    async def get_user_scores_from_supabase(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user health scores directly from Supabase scores table"""
        try:
            client = None
            
            # Try direct Supabase client first
            if self.supabase:
                client = self.supabase
            # Fallback to analysis_history connection
            elif hasattr(self.analysis_history.connection, 'client'):
                client = self.analysis_history.connection.client
            
            if not client:
                logger.warning("No Supabase client available")
                return None
            
            response = client.table('scores')\
                .select('*')\
                .eq('profile_id', profile_id)\
                .order('score_date_time', desc=True)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting scores for {profile_id}: {e}")
            return None
    
    async def get_total_user_counts(self) -> Dict[str, int]:
        """Get statistics about users in the database"""
        try:
            stats = {
                "total_users": 0,
                "users_with_analysis": 0,
                "users_with_health_data": 0
            }
            
            # Get total users from profiles table
            client = None
            if self.supabase:
                client = self.supabase
            elif hasattr(self.analysis_history.connection, 'client'):
                client = self.analysis_history.connection.client
            
            if client:
                # Count total users
                response = client.table('profiles').select('id', count='exact').execute()
                stats["total_users"] = response.count or 0
                
                # Count users with health data
                response = client.table('scores').select('profile_id', count='exact').execute()
                stats["users_with_health_data"] = response.count or 0
                
                # Count users with analysis data
                response = client.table('analysis_memory').select('profile_id', count='exact').execute()
                stats["users_with_analysis"] = response.count or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user counts: {e}")
            return {"total_users": 0, "users_with_analysis": 0, "users_with_health_data": 0}
    
    async def test_connections(self) -> Dict[str, str]:
        """Test database connections"""
        results = {}
        
        # Test analysis_memory connection
        try:
            connection = self.analysis_history.connection
            if hasattr(connection, 'client'):
                # Test with a simple query
                response = connection.client.table('analysis_memory').select('profile_id').limit(1).execute()
                results["analysis_memory"] = "healthy"
            else:
                results["analysis_memory"] = "no_client_available"
        except Exception as e:
            results["analysis_memory"] = f"error: {str(e)}"
        
        # Test direct Supabase connection
        try:
            if self.supabase:
                response = self.supabase.table('profiles').select('id').limit(1).execute()
                results["supabase_database"] = "healthy"
            else:
                results["supabase_database"] = "client_not_initialized"
        except Exception as e:
            results["supabase_database"] = f"error: {str(e)}"
        
        return results
    
    async def fetch_all(self, query: str, params: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute raw SQL query and return all results.
        For Phase 2 analysis data extraction.
        
        Args:
            query: SQL query string with $1, $2, etc. placeholders
            params: List of parameters to bind to query
            
        Returns:
            List of dictionaries representing query results
        """
        try:
            logger.debug(f"Executing query: {query[:100]}... with {len(params)} params")
            
            # Get Supabase client
            client = None
            if self.supabase:
                client = self.supabase
            elif hasattr(self.analysis_history.connection, 'client'):
                client = self.analysis_history.connection.client
            
            if not client:
                raise Exception("No database client available")
            
            # Convert PostgreSQL-style query ($1, $2) to Supabase RPC or direct table query
            # For analysis_memory queries, we'll use Supabase table API instead of raw SQL
            
            if "FROM analysis_memory" in query and "WHERE profile_id = $1 AND DATE(analysis_date) = $2" in query:
                # Handle the specific analysis_memory query for Phase 2
                profile_id = params[0]
                target_date = params[1]
                
                # Build Supabase query
                query_builder = client.table('analysis_memory')\
                    .select('*')\
                    .eq('profile_id', profile_id)\
                    .gte('analysis_date', target_date)\
                    .lt('analysis_date', f"{target_date}T23:59:59.999999+00:00")\
                    .order('analysis_date', desc=True)\
                    .order('created_at', desc=True)
                
                # Add analysis_type filter if provided
                if len(params) >= 4 and params[2]:  # analysis_type parameter exists
                    query_builder = query_builder.eq('analysis_type', params[2])
                    limit_value = params[3] if len(params) > 3 else params[2]  # Handle parameter order
                else:
                    limit_value = params[2] if len(params) > 2 else 10
                
                # Apply limit
                if isinstance(limit_value, int):
                    query_builder = query_builder.limit(limit_value)
                
                # Execute query
                response = query_builder.execute()
                
                if response.data:
                    logger.debug(f"Query returned {len(response.data)} results")
                    return response.data
                else:
                    logger.debug("Query returned no results")
                    return []
            
            else:
                # For other queries, try to handle generically or raise error
                logger.error(f"Unsupported query type: {query[:50]}...")
                raise Exception("This query type is not yet supported by fetch_all method")
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise Exception(f"Database query failed: {str(e)}")