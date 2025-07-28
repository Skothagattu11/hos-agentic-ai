from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass
import os
import asyncpg
import json
from .connection_factory import smart_connect
from .api_client import HealthDataAPIClient
from .data_mappers import DataMapper

# Import models from separate file to avoid circular imports
from .models import ScoreData, ArchetypeData, BiomarkerData, UserProfileContext

@dataclass
class UserProfileService:
    """Service class to handle user profile data fetching and structuring"""
    
    def __init__(self):
        # Initialize API client and database connection
        self.database_url = os.getenv("DATABASE_URL")  # Optional now
        self.api_client = HealthDataAPIClient()
        self.data_mapper = DataMapper()
        self.use_api = os.getenv("USE_API", "true").lower() == "true"
    
    async def get_db_connection(self):
        """Get database connection"""
        # Disable prepared statements for pgbouncer compatibility
        return await smart_connect(self.database_url)
        
    def get_date_range(self, days: int = 7) -> tuple[datetime, datetime]:
        """Get date range for the last N days"""
        # Use current date as end date for more dynamic behavior
        from datetime import timezone
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    def datetime_to_string(self, dt: datetime) -> str:
        """Convert datetime to string format for SQL queries"""
        return dt.isoformat()
    
    def _get_latest_archetypes(self, archetypes: List[ArchetypeData]) -> List[ArchetypeData]:
        """Get the latest archetype for each name/periodicity combination"""
        from collections import defaultdict
        
        # Group archetypes by (name, periodicity)
        grouped = defaultdict(list)
        for archetype in archetypes:
            key = (archetype.name, archetype.periodicity)
            grouped[key].append(archetype)
        
        # Get the latest one from each group
        latest_archetypes = []
        for (name, periodicity), archetype_list in grouped.items():
            # Sort by start_date_time descending and take the first (latest)
            sorted_archetypes = sorted(archetype_list, key=lambda x: x.start_date_time, reverse=True)
            latest = sorted_archetypes[0]
            print(f"[ARCHETYPE] {name} ({periodicity}): Latest from {latest.start_date_time.strftime('%Y-%m-%d')}")
            latest_archetypes.append(latest)
        
        return latest_archetypes
    
    def parse_score_date_time(self, score_date_str: str) -> datetime:
        """Parse score_date_time string to datetime object for comparison"""
        try:
            # Handle different possible formats
            if 'T' in score_date_str:
                return datetime.fromisoformat(score_date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(score_date_str, '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing date string {score_date_str}: {e}")
            return datetime.now()
    
    async def fetch_scores_data(self, profile_id: str, days: int = 7) -> List[ScoreData]:
        """Fetch scores data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        # Try API first
        if self.use_api:
            try:
                print(f"[API] Fetching scores for {profile_id}")
                api_data = await self.api_client.get_scores(profile_id, start_date, end_date)
                scores = self.data_mapper.map_scores(api_data)
                print(f"[API] Retrieved {len(scores)} scores")
                return scores
            except Exception as e:
                print(f"[API ERROR] Scores failed: {e}, falling back to DB")
        
        # Fallback to database
        try:
            conn = await self.get_db_connection()
            
            # Use created_at for filtering since score_date_time is unreliable (has old dates and nulls)
            query = """
                SELECT id, profile_id, type, score, data, score_date_time, created_at, updated_at
                FROM scores 
                WHERE profile_id = $1 
                AND created_at >= $2 
                AND created_at <= $3
                ORDER BY created_at DESC
            """
            
            # Pass datetime objects directly (AsyncPG expects datetime, not strings)
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            scores = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    # Handle score_date_time as text (can be null or unreliable)
                    score_date_time = row['score_date_time'] if row['score_date_time'] else ""
                    
                    scores.append(ScoreData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        type=row['type'],
                        score=float(row['score']),
                        data=data_dict,
                        score_date_time=score_date_time,
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing score row: {row_error}")
                    continue
            
            return scores
            
        except Exception as e:
            print(f"Error fetching scores data: {e}")
            return []
    
    async def fetch_archetypes_data(self, profile_id: str, days: int = 7) -> List[ArchetypeData]:
        """Fetch archetypes data - returns latest archetype for each name/periodicity combination"""
        start_date, end_date = self.get_date_range(days)
        
        # Try API first
        if self.use_api:
            try:
                print(f"[API] Fetching all archetypes for {profile_id}")
                api_data = await self.api_client.get_archetypes(profile_id)
                archetypes = self.data_mapper.map_archetypes(api_data)
                
                # Get latest archetype for each name/periodicity combination
                latest_archetypes = self._get_latest_archetypes(archetypes)
                print(f"[API] Retrieved {len(archetypes)} total archetypes, filtered to {len(latest_archetypes)} latest ones")
                return latest_archetypes
            except Exception as e:
                print(f"[API ERROR] Archetypes failed: {e}, falling back to DB")
        
        # Fallback to database - get all archetypes for this profile
        try:
            conn = await self.get_db_connection()
            
            # Get ALL archetypes for this profile, not filtered by date
            query = """
                SELECT id, profile_id, name, periodicity, value, data, start_date_time, end_date_time, created_at, updated_at
                FROM archetypes 
                WHERE profile_id = $1 
                ORDER BY start_date_time DESC
            """
            
            # Pass only profile_id
            rows = await conn.fetch(query, profile_id)
            await conn.close()
            
            archetypes = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    archetypes.append(ArchetypeData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        name=row['name'],
                        periodicity=row['periodicity'],
                        value=row['value'],
                        data=data_dict,
                        start_date_time=row['start_date_time'],
                        end_date_time=row['end_date_time'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing archetype row: {row_error}")
                    continue
            
            # Get latest archetype for each name/periodicity combination
            latest_archetypes = self._get_latest_archetypes(archetypes)
            return latest_archetypes
            
        except Exception as e:
            print(f"Error fetching archetypes data: {e}")
            return []
    
    async def fetch_biomarkers_data(self, profile_id: str, days: int = 7) -> List[BiomarkerData]:
        """Fetch biomarkers data for the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        # Try API first
        if self.use_api:
            try:
                print(f"[API] Fetching biomarkers for {profile_id}")
                api_data = await self.api_client.get_biomarkers(profile_id, start_date, end_date)
                biomarkers = self.data_mapper.map_biomarkers(api_data)
                print(f"[API] Retrieved {len(biomarkers)} biomarkers")
                return biomarkers
            except Exception as e:
                print(f"[API ERROR] Biomarkers failed: {e}, falling back to DB")
        
        # Fallback to database
        try:
            conn = await self.get_db_connection()
            
            query = """
                SELECT id, profile_id, category, type, data, start_date_time, end_date_time, created_at, updated_at
                FROM biomarkers 
                WHERE profile_id = $1 
                AND start_date_time >= $2 
                AND start_date_time <= $3
                ORDER BY start_date_time DESC
            """
            
            # Pass datetime objects directly (AsyncPG expects datetime, not strings)
            rows = await conn.fetch(query, profile_id, start_date, end_date)
            await conn.close()
            
            biomarkers = []
            for row in rows:
                try:
                    # Parse JSON string to dictionary
                    data_dict = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    
                    biomarkers.append(BiomarkerData(
                        id=str(row['id']),
                        profile_id=row['profile_id'],
                        category=row['category'],
                        type=row['type'],
                        data=data_dict,
                        start_date_time=row['start_date_time'],
                        end_date_time=row['end_date_time'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    ))
                except Exception as row_error:
                    print(f"Error processing biomarker row: {row_error}")
                    continue
            
            return biomarkers
            
        except Exception as e:
            print(f"Error fetching biomarkers data: {e}")
            return []
    

    
    async def get_user_profile_context(self, profile_id: str, days: int = 7) -> UserProfileContext:
        """Main method to fetch and structure all user profile data"""
        
        # Fetch data from all tables
        scores = await self.fetch_scores_data(profile_id, days)
        archetypes = await self.fetch_archetypes_data(profile_id, days)
        biomarkers = await self.fetch_biomarkers_data(profile_id, days)
        
        # Create date range info
        start_date, end_date = self.get_date_range(days)
        date_range = {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        }
        
        return UserProfileContext(
            user_id=profile_id,
            scores=scores,
            archetypes=archetypes,
            biomarkers=biomarkers,
            date_range=date_range
        )



# Utility function to get user profile context
async def get_user_profile_context(profile_id: str, days: int = 7) -> UserProfileContext:
    """Utility function to get user profile context for use with agents"""
    service = UserProfileService()
    return await service.get_user_profile_context(profile_id, days)
