"""
Simple data mappers to convert API responses to existing models
"""
from typing import List, Dict
from datetime import datetime
from .models import ScoreData, ArchetypeData, BiomarkerData


class DataMapper:
    @staticmethod
    def map_scores(api_data: List[Dict]) -> List[ScoreData]:
        """Convert API scores to ScoreData models"""
        scores = []
        for item in api_data:
            try:
                scores.append(ScoreData(
                    id=str(item['id']),
                    profile_id=item['profile_id'],
                    type=item['type'],
                    score=float(item['score']),
                    data=item.get('data', {}),
                    score_date_time=item.get('score_date_time', ''),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error mapping score: {e}")
                continue
        return scores
    
    @staticmethod
    def map_archetypes(api_data: List[Dict]) -> List[ArchetypeData]:
        """Convert API archetypes to ArchetypeData models"""
        archetypes = []
        for item in api_data:
            try:
                archetypes.append(ArchetypeData(
                    id=str(item['id']),
                    profile_id=item['profile_id'],
                    name=item['name'],
                    periodicity=item['periodicity'],
                    value=item['value'],
                    data=item.get('data', {}),
                    start_date_time=datetime.fromisoformat(item['start_date_time'].replace('Z', '+00:00')),
                    end_date_time=datetime.fromisoformat(item['end_date_time'].replace('Z', '+00:00')),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error mapping archetype: {e}")
                continue
        return archetypes
    
    @staticmethod
    def map_biomarkers(api_data: List[Dict]) -> List[BiomarkerData]:
        """Convert API biomarkers to BiomarkerData models"""
        biomarkers = []
        for item in api_data:
            try:
                biomarkers.append(BiomarkerData(
                    id=str(item['id']),
                    profile_id=item['profile_id'],
                    category=item['category'],
                    type=item['type'],
                    data=item.get('data', {}),
                    start_date_time=datetime.fromisoformat(item['start_date_time'].replace('Z', '+00:00')),
                    end_date_time=datetime.fromisoformat(item['end_date_time'].replace('Z', '+00:00')),
                    created_at=datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                ))
            except Exception as e:
                print(f"Error mapping biomarker: {e}")
                continue
        return biomarkers