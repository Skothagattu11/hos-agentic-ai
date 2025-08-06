# Phase 3 Health Data APIs Documentation

## Overview
This document outlines the design and implementation of health data APIs for displaying scores and biomarkers in the Bio Coach Hub dashboard. These APIs act as a Backend-for-Frontend (BFF) layer, fetching data from hos-fapi-hm-sahha and transforming it for UI consumption.

## API Endpoints

### 1. Health Scores Endpoint

#### Endpoint
```
GET /dashboard_api/health_scores/{user_id}
```

#### Query Parameters
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format

#### Response Format
```json
{
  "user_id": "string",
  "scores": [
    {
      "date": "2024-08-06",
      "sleep": 85,        // 0-100 scale (from Sahha sleep score * 100)
      "activity": 78,     // 0-100 scale (from Sahha activity score * 100)
      "nutrition": "--",  // Not available from Sahha, show as "--"
      "readiness": 90,    // 0-100 scale (from Sahha readiness score * 100)
      "wellbeing": 88     // 0-100 scale (from Sahha mental_wellbeing score * 100)
    }
  ]
}
```

#### Data Source Mapping
- **sleep**: Sahha `sleep` score × 100
- **activity**: Sahha `activity` score × 100
- **nutrition**: Not available, always return "--"
- **readiness**: Sahha `readiness` score × 100
- **wellbeing**: Sahha `mental_wellbeing` score × 100

### 2. Health Biomarkers Endpoint

#### Endpoint
```
GET /dashboard_api/health_biomarkers/{user_id}
```

#### Query Parameters
- `date` (required): Specific date in YYYY-MM-DD format

#### Response Format
```json
{
  "user_id": "string",
  "date": "2024-08-06",
  "biomarkers": {
    "activity": {
      "steps": 12450,           // From biomarkers type: "steps"
      "calories_burned": 680    // From biomarkers type: "active_energy_burned"
    },
    "readiness": {
      "resting_hr": 58,        // From biomarkers type: "heart_rate_resting"
      "hrv": "--"              // Not available in Sahha data
    },
    "sleep": {
      "sleep_efficiency": 89,   // From sleep metrics or calculate from data
      "sleep_debt_hours": 0.5,  // Calculate: max(0, 8 - sleep_duration_hours)
      "avg_sleep_time": "22:45", // Calculate 7-day average
      "avg_wake_time": "06:30"   // Calculate 7-day average
    },
    "daily_rating": {
      "routine_satisfaction": "--" // Not available from Sahha
    }
  }
}
```

#### Data Source Mapping
- **steps**: From biomarkers where `type = "steps"`
- **calories_burned**: From biomarkers where `type = "active_energy_burned"`
- **resting_hr**: From biomarkers where `type = "heart_rate_resting"`
- **hrv**: Not available in Sahha, return "--"
- **sleep_efficiency**: Calculate from sleep data or use sleep score as proxy
- **sleep_debt_hours**: Calculate as `max(0, 8 - (sleep_duration_minutes / 60))`
- **avg_sleep_time**: Calculate from 7-day sleep data
- **avg_wake_time**: Calculate from 7-day sleep data
- **routine_satisfaction**: Not available, return "--"

## Implementation Details

### Data Fetching Strategy
1. Fetch from hos-fapi-hm-sahha endpoints:
   - `/health-metrics/overview` for scores
   - `/health-metrics/activity` for activity biomarkers
   - `/health-metrics/sleep` for sleep biomarkers
   - `/health-metrics/recovery` for readiness biomarkers

2. Transform Sahha data format to UI format
3. Handle missing data by returning "--"
4. Apply caching for performance (1-hour TTL for scores, 2-hour TTL for biomarkers)

### Error Handling
- If hos-fapi-hm-sahha is unavailable: Return 503 Service Unavailable
- If user not found: Return 404 Not Found
- If date range invalid: Return 400 Bad Request
- Missing data fields: Return "--" instead of null

### Performance Considerations
- Implement caching at BFF layer
- Batch requests to hos-fapi-hm-sahha when possible
- Return partial data if some metrics fail (with "--" for failed fields)

## Testing Strategy

### Unit Tests
1. Test data transformation logic
2. Test date range validation
3. Test missing data handling

### Integration Tests
1. Test with real hos-fapi-hm-sahha endpoints
2. Test error scenarios
3. Test caching behavior

### Example Test Cases
```python
# Test 1: Valid date range returns transformed scores
# Test 2: Missing HRV returns "--"
# Test 3: Sleep debt calculation is correct
# Test 4: Invalid date format returns 400
# Test 5: Caching prevents duplicate API calls
```

## Frontend Integration

### ScoreTrends Component
```typescript
// Replace mock data generation with:
const { data } = await apiService.getHealthScores(
  userId, 
  startDate, 
  endDate
);
```

### HealthMetrics Component
```typescript
// Replace mock metrics with:
const { data } = await apiService.getHealthBiomarkers(
  userId,
  selectedDate
);
```

## Migration Path
1. Deploy new endpoints alongside existing functionality
2. Update frontend to use new endpoints
3. Monitor for issues
4. Remove mock data generation code

## Future Enhancements
- Add HRV data when available from Sahha
- Calculate nutrition scores based on meal logging
- Add routine satisfaction from user input
- Implement real-time data updates via WebSocket