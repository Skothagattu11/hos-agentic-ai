#!/usr/bin/env python3
"""
Simple test script for Phase 2 Analysis Data API
Tests the new endpoint with sample data.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_phase2_api():
    """Test Phase 2 analysis data API"""
    print("🧪 Testing Phase 2 Analysis Data API...")
    
    try:
        from dashboard_api.services.dashboard_service import DashboardService
        from dashboard_api.services.database_service import DatabaseService
        
        print("✅ Imports successful")
        
        # Test database service fetch_all method
        print("\n📊 Testing DatabaseService.fetch_all()...")
        db_service = DatabaseService()
        
        # Test with a sample query (this is what Phase 2 uses)
        query = """
        SELECT 
            id, profile_id, analysis_date, analysis_type, archetype, 
            previous_analysis_id, behavior_analysis, nutrition_plan, 
            routine_plan, user_preferences, health_goals, dietary_restrictions,
            lifestyle_context, medical_conditions, analysis_insights, 
            health_trends, improvement_areas, success_patterns, 
            engagement_metrics, performance_metrics, extras,
            created_at, updated_at
        FROM analysis_memory 
        WHERE profile_id = $1 AND DATE(analysis_date) = $2
        ORDER BY analysis_date DESC, created_at DESC
        LIMIT $3
        """
        
        params = ["mbzXA48h4ASzre407KoFMepfyGv1", "2025-08-05", 10]
        
        try:
            results = await db_service.fetch_all(query, params)
            print(f"✅ Database query successful - found {len(results)} records")
            
            if results:
                sample = results[0]
                print(f"   Sample record ID: {sample.get('id', 'N/A')}")
                print(f"   Analysis type: {sample.get('analysis_type', 'N/A')}")
                print(f"   Archetype: {sample.get('archetype', 'N/A')}")
                print(f"   Has behavior_analysis: {bool(sample.get('behavior_analysis'))}")
                print(f"   Has nutrition_plan: {bool(sample.get('nutrition_plan'))}")
                print(f"   Has routine_plan: {bool(sample.get('routine_plan'))}")
            else:
                print("   No records found for test user/date")
                
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return False
        
        # Test dashboard service method
        print("\n🎯 Testing DashboardService.get_user_analysis_data()...")
        service = DashboardService()
        
        try:
            result = await service.get_user_analysis_data(
                user_id="mbzXA48h4ASzre407KoFMepfyGv1",
                date="2025-08-05", 
                limit=10
            )
            
            print(f"✅ Service method successful - {result.total_analyses} analyses found")
            print(f"   User ID: {result.user_id}")
            print(f"   Date: {result.date}")
            print(f"   Total analyses: {result.total_analyses}")
            
            if result.analyses:
                sample_analysis = result.analyses[0]
                print(f"   Sample analysis ID: {sample_analysis.analysis_id}")
                print(f"   Analysis type: {sample_analysis.analysis_type}")
                print(f"   Archetype: {sample_analysis.archetype}")
                
        except Exception as e:
            print(f"❌ Service method failed: {e}")
            return False
        
        finally:
            await service.cleanup()
        
        print("\n🎉 All Phase 2 tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Phase 2 Analysis Data API Test")
    print("=" * 40)
    
    # Load environment variables
    from pathlib import Path
    from dotenv import load_dotenv
    
    env_locations = [
        Path.cwd() / ".env",
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env"
    ]
    
    env_loaded = False
    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            env_loaded = True
            print(f"📁 Loaded .env from: {env_path}")
            break
    
    if not env_loaded:
        print("⚠️  No .env file found - using system environment")
    
    # Run tests
    success = asyncio.run(test_phase2_api())
    
    if success:
        print("\n✅ Phase 2 API is ready for use!")
        print("\nTest these endpoints:")
        print("GET /api/v1/users/mbzXA48h4ASzre407KoFMepfyGv1/analysis-data?date=2025-08-05")
        print("GET /api/v1/users/mbzXA48h4ASzre407KoFMepfyGv1/analysis-data?date=2025-08-05&analysis_type=initial")
    else:
        print("\n❌ Phase 2 API tests failed - check error messages above")
        sys.exit(1)