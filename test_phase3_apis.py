"""
Test script for Phase 3 Health Data APIs
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "mbzXA48h4ASzre407KoFMepfyGv1"  # From input_2.txt sample data

# Test date ranges
end_date = datetime.now().strftime("%Y-%m-%d")
start_date_7d = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
start_date_30d = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


async def test_health_scores(session):
    """Test health scores endpoint"""
    print("\n=== Testing Health Scores API ===")
    
    # Test 7-day range
    url = f"{BASE_URL}/dashboard_api/health_scores/{TEST_USER_ID}"
    params = {
        "start_date": start_date_7d,
        "end_date": end_date
    }
    
    print(f"\nTesting 7-day range: {start_date_7d} to {end_date}")
    try:
        async with session.get(url, params=params) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            
            if response.status == 200:
                print(f"User ID: {data['user_id']}")
                print(f"Number of days: {len(data['scores'])}")
                
                # Show first day's scores
                if data['scores']:
                    first_day = data['scores'][0]
                    print(f"\nFirst day ({first_day['date']}) scores:")
                    print(f"  Sleep: {first_day['sleep']}")
                    print(f"  Activity: {first_day['activity']}")
                    print(f"  Nutrition: {first_day['nutrition']}")
                    print(f"  Readiness: {first_day['readiness']}")
                    print(f"  Wellbeing: {first_day['wellbeing']}")
            else:
                print(f"Error: {data}")
                
    except Exception as e:
        print(f"Error testing health scores: {e}")
        

async def test_health_biomarkers(session):
    """Test health biomarkers endpoint"""
    print("\n=== Testing Health Biomarkers API ===")
    
    # Test today's biomarkers
    url = f"{BASE_URL}/dashboard_api/health_biomarkers/{TEST_USER_ID}"
    params = {
        "date": end_date
    }
    
    print(f"\nTesting biomarkers for date: {end_date}")
    try:
        async with session.get(url, params=params) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            
            if response.status == 200:
                print(f"User ID: {data['user_id']}")
                print(f"Date: {data['date']}")
                
                biomarkers = data['biomarkers']
                print("\nActivity Metrics:")
                print(f"  Steps: {biomarkers['activity']['steps']}")
                print(f"  Calories Burned: {biomarkers['activity']['calories_burned']}")
                
                print("\nReadiness Metrics:")
                print(f"  Resting HR: {biomarkers['readiness']['resting_hr']}")
                print(f"  HRV: {biomarkers['readiness']['hrv']}")
                
                print("\nSleep Metrics:")
                print(f"  Sleep Efficiency: {biomarkers['sleep']['sleep_efficiency']}")
                print(f"  Sleep Debt: {biomarkers['sleep']['sleep_debt_hours']}")
                print(f"  Avg Sleep Time: {biomarkers['sleep']['avg_sleep_time']}")
                print(f"  Avg Wake Time: {biomarkers['sleep']['avg_wake_time']}")
                
                print("\nDaily Rating:")
                print(f"  Routine Satisfaction: {biomarkers['daily_rating']['routine_satisfaction']}")
            else:
                print(f"Error: {data}")
                
    except Exception as e:
        print(f"Error testing health biomarkers: {e}")


async def test_error_cases(session):
    """Test error handling"""
    print("\n=== Testing Error Cases ===")
    
    # Test invalid date format
    print("\nTesting invalid date format...")
    url = f"{BASE_URL}/dashboard_api/health_scores/{TEST_USER_ID}"
    params = {
        "start_date": "2024/08/01",  # Wrong format
        "end_date": end_date
    }
    
    try:
        async with session.get(url, params=params) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test start_date > end_date
    print("\nTesting start_date > end_date...")
    params = {
        "start_date": end_date,
        "end_date": start_date_7d
    }
    
    try:
        async with session.get(url, params=params) as response:
            print(f"Status: {response.status}")
            data = await response.json()
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all tests"""
    print("Starting Phase 3 API Tests...")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    
    async with aiohttp.ClientSession() as session:
        # Check if server is running
        try:
            async with session.get(f"{BASE_URL}/api/health") as response:
                if response.status != 200:
                    print("\n❌ Server is not running! Please start the server first.")
                    return
        except:
            print("\n❌ Cannot connect to server! Please start the server first.")
            print("Run: cd health-agent-main && python app.py")
            return
        
        # Run tests
        await test_health_scores(session)
        await test_health_biomarkers(session)
        await test_error_cases(session)
        
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())