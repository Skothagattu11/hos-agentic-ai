from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from dataclasses import dataclass
from agents import Agent

# Pydantic models for data structure (same as before)
class ScoreData(BaseModel):
    profile_id: str
    category: str
    type: str
    data: Dict[str, Any]
    start_date_time: datetime
    end_date_time: datetime
    created_at: datetime
    updated_at: datetime

class ArchetypeData(BaseModel):
    profile_id: str
    category: str
    type: str
    data: Dict[str, Any]
    start_date_time: datetime
    end_date_time: datetime
    created_at: datetime
    updated_at: datetime

class BiomarkerData(BaseModel):
    profile_id: str
    category: str
    type: str
    data: Dict[str, Any]
    start_date_time: datetime
    end_date_time: datetime
    created_at: datetime
    updated_at: datetime

class UserProfileContext(BaseModel):
    user_id: str
    scores: List[ScoreData]
    archetypes: List[ArchetypeData]
    biomarkers: List[BiomarkerData]
    date_range: Dict[str, datetime]
    summary: Dict[str, Any]

@dataclass
class UserProfileServiceMCP:
    """Service class to handle user profile data fetching using MCP Supabase tools"""
    
    def get_date_range(self, days: int = 7) -> tuple[str, str]:
        """Get date range for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date.isoformat(), end_date.isoformat()
    
    def build_date_filter_query(self, profile_id: str, table: str, days: int = 7) -> str:
        """Build SQL query for fetching data from the last N days"""
        start_date, end_date = self.get_date_range(days)
        
        query = f"""
        SELECT * FROM {table} 
        WHERE profile_id = '{profile_id}' 
        AND start_date_time >= '{start_date}' 
        AND end_date_time <= '{end_date}'
        ORDER BY start_date_time DESC;
        """
        return query
    
    async def fetch_scores_data_mcp(self, profile_id: str, days: int = 7) -> List[ScoreData]:
        """Fetch scores data using MCP Supabase execute_sql"""
        query = self.build_date_filter_query(profile_id, 'scores', days)
        
        try:
            # Note: This would be called through MCP Supabase execute_sql tool
            # For now, returning empty list as placeholder
            # In actual implementation, you'd use:
            # result = mcp_supabase_execute_sql(query=query)
            
            print(f"Would execute query: {query}")
            return []
            
        except Exception as e:
            print(f"Error fetching scores data: {e}")
            return []
    
    async def fetch_archetypes_data_mcp(self, profile_id: str, days: int = 7) -> List[ArchetypeData]:
        """Fetch archetypes data using MCP Supabase execute_sql"""
        query = self.build_date_filter_query(profile_id, 'archetypes', days)
        
        try:
            print(f"Would execute query: {query}")
            return []
            
        except Exception as e:
            print(f"Error fetching archetypes data: {e}")
            return []
    
    async def fetch_biomarkers_data_mcp(self, profile_id: str, days: int = 7) -> List[BiomarkerData]:
        """Fetch biomarkers data using MCP Supabase execute_sql"""
        query = self.build_date_filter_query(profile_id, 'biomarkers', days)
        
        try:
            print(f"Would execute query: {query}")
            return []
            
        except Exception as e:
            print(f"Error fetching biomarkers data: {e}")
            return []
    
    def parse_sql_result_to_scores(self, sql_result: List[Dict]) -> List[ScoreData]:
        """Parse SQL result to ScoreData objects"""
        scores = []
        for item in sql_result:
            try:
                scores.append(ScoreData(
                    profile_id=item['profile_id'],
                    category=item['category'],
                    type=item['type'],
                    data=item['data'],
                    start_date_time=datetime.fromisoformat(item['start_date_time'].replace('Z', '+00:00')),
                    end_date_time=datetime.fromisoformat(item['end_date_time'].replace('Z', '+00:00')),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error parsing score data: {e}")
                continue
        return scores
    
    def parse_sql_result_to_archetypes(self, sql_result: List[Dict]) -> List[ArchetypeData]:
        """Parse SQL result to ArchetypeData objects"""
        archetypes = []
        for item in sql_result:
            try:
                archetypes.append(ArchetypeData(
                    profile_id=item['profile_id'],
                    category=item['category'],
                    type=item['type'],
                    data=item['data'],
                    start_date_time=datetime.fromisoformat(item['start_date_time'].replace('Z', '+00:00')),
                    end_date_time=datetime.fromisoformat(item['end_date_time'].replace('Z', '+00:00')),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error parsing archetype data: {e}")
                continue
        return archetypes
    
    def parse_sql_result_to_biomarkers(self, sql_result: List[Dict]) -> List[BiomarkerData]:
        """Parse SQL result to BiomarkerData objects"""
        biomarkers = []
        for item in sql_result:
            try:
                biomarkers.append(BiomarkerData(
                    profile_id=item['profile_id'],
                    category=item['category'],
                    type=item['type'],
                    data=item['data'],
                    start_date_time=datetime.fromisoformat(item['start_date_time'].replace('Z', '+00:00')),
                    end_date_time=datetime.fromisoformat(item['end_date_time'].replace('Z', '+00:00')),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error parsing biomarker data: {e}")
                continue
        return biomarkers
    
    def generate_summary(self, scores: List[ScoreData], archetypes: List[ArchetypeData], 
                        biomarkers: List[BiomarkerData]) -> Dict[str, Any]:
        """Generate a summary of the user's profile data"""
        
        summary = {
            "data_counts": {
                "scores": len(scores),
                "archetypes": len(archetypes),
                "biomarkers": len(biomarkers)
            },
            "categories": {
                "scores": list(set([score.category for score in scores])) if scores else [],
                "archetypes": list(set([archetype.category for archetype in archetypes])) if archetypes else [],
                "biomarkers": list(set([biomarker.category for biomarker in biomarkers])) if biomarkers else []
            },
            "types": {
                "scores": list(set([score.type for score in scores])) if scores else [],
                "archetypes": list(set([archetype.type for archetype in archetypes])) if archetypes else [],
                "biomarkers": list(set([biomarker.type for biomarker in biomarkers])) if biomarkers else []
            },
            "date_coverage": {
                "earliest_score": min([score.start_date_time for score in scores]) if scores else None,
                "latest_score": max([score.end_date_time for score in scores]) if scores else None,
                "earliest_archetype": min([archetype.start_date_time for archetype in archetypes]) if archetypes else None,
                "latest_archetype": max([archetype.end_date_time for archetype in archetypes]) if archetypes else None,
                "earliest_biomarker": min([biomarker.start_date_time for biomarker in biomarkers]) if biomarkers else None,
                "latest_biomarker": max([biomarker.end_date_time for biomarker in biomarkers]) if biomarkers else None,
            }
        }
        
        return summary

# User Profile Agent with MCP integration
USER_PROFILE_AGENT_MCP_PROMPT = """You are a User Profile Analysis Agent that specializes in understanding and interpreting user health data from Supabase.

Your role is to:
1. Analyze user profile data including scores, archetypes, and biomarkers from the last 7 days
2. Identify patterns and trends in the temporal data
3. Provide insights about the user's health status and progress
4. Structure the information for other health agents to use effectively

When analyzing data, consider:
- Temporal patterns and trends over the 7-day period
- Relationships between different data types (scores, archetypes, biomarkers)
- Significant changes or anomalies in the data
- Overall health indicators and risk factors
- Data quality and completeness

You have access to MCP Supabase tools to query the database directly when needed.

Provide clear, structured analysis with actionable insights for other health agents.
"""

# Create the user profile agent with MCP capabilities
user_profile_agent_mcp = Agent(
    name="User Profile MCP Agent",
    instructions=USER_PROFILE_AGENT_MCP_PROMPT,
    model="gpt-4o-mini"
)

# Utility function to get user profile context using MCP
async def get_user_profile_context_mcp(profile_id: str, days: int = 7) -> UserProfileContext:
    """Utility function to get user profile context using MCP Supabase tools"""
    service = UserProfileServiceMCP()
    
    # These would be replaced with actual MCP tool calls
    scores = await service.fetch_scores_data_mcp(profile_id, days)
    archetypes = await service.fetch_archetypes_data_mcp(profile_id, days)
    biomarkers = await service.fetch_biomarkers_data_mcp(profile_id, days)
    
    # Generate summary
    summary = service.generate_summary(scores, archetypes, biomarkers)
    
    # Create date range info
    start_date, end_date = service.get_date_range(days)
    date_range = {
        "start_date": datetime.fromisoformat(start_date),
        "end_date": datetime.fromisoformat(end_date),
        "days": days
    }
    
    return UserProfileContext(
        user_id=profile_id,
        scores=scores,
        archetypes=archetypes,
        biomarkers=biomarkers,
        date_range=date_range,
        summary=summary
    ) 