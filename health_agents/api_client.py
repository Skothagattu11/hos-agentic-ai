"""
Simple HTTP client for raw health data APIs
"""
import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime


class HealthDataAPIClient:
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.getenv("HOS_FAPI_BASE_URL", "https://hos-fapi-hm-sahha.onrender.com")).rstrip('/')
        self.timeout = 30
    
    async def get_scores(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch scores from API"""
        params = {
            'user_id': user_id,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'limit': 1000
        }
        return await self._request('/api/v1/sahha/scores', params)
    
    async def get_archetypes(self, user_id: str) -> List[Dict]:
        """Fetch archetypes from API"""
        params = {
            'user_id': user_id,
            'limit': 1000
        }
        return await self._request('/api/v1/sahha/archetypes', params)
    
    async def get_biomarkers(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch biomarkers from API"""
        params = {
            'user_id': user_id,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'limit': 1000
        }
        return await self._request('/api/v1/sahha/biomarkers', params)
    
    async def _request(self, endpoint: str, params: Dict) -> List[Dict]:
        """Make HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                print(f"[API DEBUG] Calling {url} with params: {params}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Debug: show response structure
                if isinstance(data, dict):
                    print(f"[API DEBUG] Response is dict with keys: {list(data.keys())}")
                    # Check if data is wrapped in a response object
                    if 'data' in data:
                        actual_data = data['data']
                        print(f"[API DEBUG] Found 'data' key, extracted {len(actual_data) if isinstance(actual_data, list) else 'not a list'} items")
                        return actual_data if isinstance(actual_data, list) else []
                    elif 'items' in data:
                        actual_data = data['items']
                        print(f"[API DEBUG] Found 'items' key, extracted {len(actual_data) if isinstance(actual_data, list) else 'not a list'} items")
                        return actual_data if isinstance(actual_data, list) else []
                    elif 'results' in data:
                        actual_data = data['results']
                        print(f"[API DEBUG] Found 'results' key, extracted {len(actual_data) if isinstance(actual_data, list) else 'not a list'} items")
                        return actual_data if isinstance(actual_data, list) else []
                
                print(f"[API DEBUG] Response status: {response.status_code}, data length: {len(data) if isinstance(data, list) else 'not a list'}")
                return data if isinstance(data, list) else []
            except httpx.HTTPError as http_err:
                print(f"[API HTTP ERROR] {endpoint}: {http_err}")
                print(f"[API DEBUG] Full URL: {url}")
                return []
            except Exception as e:
                print(f"[API ERROR] {endpoint}: {e}")
                return []