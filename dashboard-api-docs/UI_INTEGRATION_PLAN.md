# UI Integration Plan: Bio-Coach-Hub Frontend

## Current Status Summary

### ✅ Available APIs (Phase 1 & 2)
**Phase 1 APIs:**
- `GET /api/v1/users` - List all users with pagination
- `GET /api/v1/users/{user_id}` - Get detailed user profile  
- `GET /api/v1/health` - System health check
- `GET /api/v1/info` - Service information

**Phase 2 APIs:**
- `GET /api/v1/users/{user_id}/analysis-data?date={date}` - Complete analysis data for date

### 🎯 Current Frontend Structure (bio-coach-hub)
```
src/
├── components/
│   ├── BehaviorAnalysis.tsx     # Needs Phase 2 API integration
│   ├── EngagementAnalysis.tsx   # Needs Phase 2 API integration  
│   ├── NutritionPlan.tsx        # Needs Phase 2 API integration
│   ├── RoutinePlan.tsx          # Needs Phase 2 API integration
│   ├── MetricCards.tsx          # Uses mock data currently
│   ├── DateNavigation.tsx       # Triggers data fetching
│   └── MetricsTrends.tsx        # Uses mock data currently
├── pages/
│   ├── Index.tsx               # User listing page
│   └── UserProfile.tsx         # Individual user analysis view
└── lib/
    └── mockData.ts             # To be replaced with API calls
```

## Integration Plan Overview

### Phase A: API Configuration & Services
**Goal**: Set up API communication layer and replace mock data

### Phase B: User Listing Integration  
**Goal**: Connect Index.tsx to Phase 1 user APIs

### Phase C: Analysis Data Integration
**Goal**: Connect UserProfile.tsx to Phase 2 analysis APIs

### Phase D: Real-time Date Navigation
**Goal**: Implement seamless date switching with API calls

## Detailed Integration Steps

### Phase A: API Configuration & Services (2-3 hours)

#### A1. API Configuration Setup
```typescript
// src/lib/api.ts - New file
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',  // Health agent API
  ENDPOINTS: {
    // Phase 1
    USERS_LIST: '/api/v1/users',
    USER_PROFILE: '/api/v1/users/{id}', 
    HEALTH_CHECK: '/api/v1/health',
    
    // Phase 2  
    ANALYSIS_DATA: '/api/v1/users/{id}/analysis-data'
  }
};
```

#### A2. API Service Layer
```typescript
// src/services/apiService.ts - New file
class ApiService {
  // Phase 1 methods
  async getUsers(limit?: number, offset?: number): Promise<UserListResponse>
  async getUserProfile(userId: string): Promise<UserProfile>
  async getHealthCheck(): Promise<HealthCheckResponse>
  
  // Phase 2 methods
  async getAnalysisData(userId: string, date: string, options?: AnalysisOptions): Promise<AnalysisDataResponse>
  
  // Error handling
  private async handleRequest<T>(request: Promise<Response>): Promise<T>
}
```

#### A3. TypeScript Interfaces  
```typescript
// src/types/api.ts - New file
// Mirror the Pydantic models from Phase 1 & 2 APIs
export interface UserSummary { ... }
export interface UserProfile { ... }
export interface AnalysisDataResponse { ... }
export interface AnalysisRecord { ... }
```

#### A4. Replace Mock Data Gradually
- Keep `mockData.ts` as fallback during development
- Add feature flag to switch between mock/real data
- Implement error boundaries for API failures

### Phase B: User Listing Integration (1-2 hours)

#### B1. Update Index.tsx Component
**Current**: Uses `getAllUsers()` from mockData
**New**: Uses API service with loading states and error handling

```typescript
// Key changes to Index.tsx
const [users, setUsers] = useState<UserSummary[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetchUsers();
}, []);

const fetchUsers = async () => {
  try {
    setLoading(true);
    const response = await apiService.getUsers();
    setUsers(response.users);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

#### B2. Add Loading & Error States
- Loading skeleton for user cards
- Error message with retry button  
- Empty state when no users found
- Pagination controls (if needed)

#### B3. Update User Card Display
- Map API response fields to existing UI components
- Handle missing data gracefully (optional fields)
- Maintain existing styling and interactions

### Phase C: Analysis Data Integration (3-4 hours)

#### C1. UserProfile.tsx Core Updates
**Current**: Uses `getUserData()` and mock data
**New**: Single API call to get all analysis data for date

```typescript
// Key changes to UserProfile.tsx
const [analysisData, setAnalysisData] = useState<AnalysisDataResponse | null>(null);
const [selectedDate, setSelectedDate] = useState(getCurrentDate());
const [loading, setLoading] = useState(false);

const fetchAnalysisData = async (date: string) => {
  setLoading(true);
  try {
    const data = await apiService.getAnalysisData(userId, date);
    setAnalysisData(data);
  } catch (error) {
    handleError(error);
  } finally {
    setLoading(false);
  }
};

useEffect(() => {
  fetchAnalysisData(selectedDate);
}, [selectedDate, userId]);
```

#### C2. Component-Specific Integrations

##### BehaviorAnalysis.tsx
- **Input**: `analysisData.analyses[].behavior_analysis` JSON
- **Display**: Parse JSON and show key insights
- **Handle**: Multiple analyses per day, empty data

```typescript
// Example component update
const BehaviorAnalysis = ({ analysisData }) => {
  const behaviorData = analysisData?.analyses?.map(a => a.behavior_analysis) || [];
  
  return (
    <div>
      {behaviorData.map((behavior, index) => (
        <BehaviorCard key={index} data={behavior} />
      ))}
      {behaviorData.length === 0 && <EmptyState />}
    </div>
  );
};
```

##### NutritionPlan.tsx  
- **Input**: `analysisData.analyses[].nutrition_plan` JSON
- **Display**: Calories, macros, meal plans
- **Handle**: Date mismatches, missing nutrition data

##### RoutinePlan.tsx
- **Input**: `analysisData.analyses[].routine_plan` JSON  
- **Display**: Schedule blocks, daily summary
- **Handle**: Different date formats, empty schedules

##### EngagementAnalysis.tsx
- **Input**: `analysisData.analyses[].engagement_metrics` JSON
- **Display**: Metrics or "No data available" message
- **Handle**: Mostly empty engagement data currently

#### C3. Data Display Strategy
- **Plain Text/JSON View**: For Phase 2, show raw JSON data in readable format
- **Progressive Enhancement**: Start simple, add formatting later
- **Multiple Analyses**: Show all analyses for a date with timestamps
- **Error Handling**: Graceful degradation when JSON parsing fails

### Phase D: Real-time Date Navigation (1-2 hours)

#### D1. DateNavigation Component Enhancement
**Current**: Updates selectedDate state
**New**: Triggers API calls and shows loading states

```typescript
// Enhanced DateNavigation
const DateNavigation = ({ selectedDate, onDateChange, loading }) => {
  const handleDateChange = async (newDate: string) => {
    onDateChange(newDate);  // This will trigger API call in parent
  };
  
  return (
    <div>
      <DatePicker 
        value={selectedDate}
        onChange={handleDateChange}
        disabled={loading}
      />
      {loading && <LoadingSpinner />}
    </div>
  );
};
```

#### D2. Performance Optimizations
- **Debouncing**: Prevent rapid API calls during date navigation
- **Caching**: Implement client-side cache for recently viewed dates  
- **Preloading**: Prefetch data for adjacent dates
- **Loading States**: Show skeleton UI during data fetching

## API Response Mapping Strategy

### Phase 1 API → Frontend Components

#### User Listing (Index.tsx)
```typescript
// API Response: UserListResponse
{
  users: UserSummary[],
  total_count: number,
  has_more: boolean
}

// Maps to existing user card display:
- UserSummary.name → User card title
- UserSummary.age → User details  
- UserSummary.latest_archetype → Badge
- UserSummary.overall_score → Health score display
- UserSummary.total_analyses → Analysis count
```

#### User Profile Header
```typescript
// API Response: UserProfile  
{
  id, name, age, analysis_summary, current_health_scores, data_availability
}

// Maps to profile header:
- UserProfile.name → Header title
- UserProfile.age → User info
- UserProfile.current_health_scores → Score cards
- UserProfile.analysis_summary → Analysis stats
```

### Phase 2 API → Tab Components

#### Single API Call Strategy
```typescript
// Single API call provides data for ALL tabs:
const analysisData = await getAnalysisData(userId, date);

// Tab 1: Behavior Analysis
analysisData.analyses[].behavior_analysis → BehaviorAnalysis component

// Tab 2: Engagement  
analysisData.analyses[].engagement_metrics → EngagementAnalysis component

// Tab 3: Routine Plan
analysisData.analyses[].routine_plan → RoutinePlan component

// Tab 4: Nutrition Plan
analysisData.analyses[].nutrition_plan → NutritionPlan component
```

## Error Handling Strategy

### API Error Categories
1. **Network Errors**: Connection timeout, server down
2. **Authentication Errors**: Invalid credentials (future)
3. **Data Errors**: Malformed JSON, missing required fields
4. **Business Logic Errors**: No data for date, invalid user ID

### UI Error Handling
1. **Loading States**: Skeleton UI during API calls
2. **Error Messages**: User-friendly error descriptions
3. **Retry Mechanisms**: Retry buttons for failed requests
4. **Fallback Content**: Show partial data when possible
5. **Error Boundaries**: Prevent app crashes from component errors

## Development Phases Timeline

### Week 1: Foundation (Phase A + B)
- **Day 1-2**: API service layer, TypeScript interfaces
- **Day 3-4**: User listing integration with Phase 1 APIs
- **Day 5**: Testing, error handling, loading states

### Week 2: Analysis Integration (Phase C)  
- **Day 1-2**: UserProfile.tsx core API integration
- **Day 3-4**: Component-specific integrations (4 tab components)
- **Day 5**: Multiple analyses handling, error states

### Week 3: Polish (Phase D + Testing)
- **Day 1-2**: Date navigation optimization, caching
- **Day 3-4**: Performance improvements, loading optimizations  
- **Day 5**: End-to-end testing, bug fixes

## Testing Strategy

### Unit Testing
- API service methods with mock responses
- Component rendering with different data states
- Error handling scenarios

### Integration Testing  
- Full user flow: Index → UserProfile → Date navigation
- API error scenarios and recovery
- Multiple analyses per day handling

### Manual Testing Scenarios
1. **Happy Path**: User browses profiles, switches dates, views analysis data
2. **Error Scenarios**: Network failures, empty data, malformed responses
3. **Edge Cases**: Users with no analyses, dates with no data, multiple analyses per day

## Future Enhancements (Phase 3+ Preparation)

### Data Features Ready for Phase 3
- **Trends Analysis**: Frontend components ready for trends API integration
- **Real-time Updates**: WebSocket infrastructure for live data  
- **Advanced Filtering**: Analysis type filters, date ranges
- **Data Export**: CSV/PDF export of analysis data

### UI Improvements
- **Enhanced Visualizations**: Charts for behavior trends
- **Better JSON Display**: Formatted, searchable JSON viewers
- **Mobile Responsiveness**: Touch-friendly date navigation
- **Accessibility**: Screen reader support, keyboard navigation

## Success Criteria

### Phase A Success Metrics
- ✅ API service layer implemented and tested
- ✅ TypeScript interfaces match API responses
- ✅ Error handling and loading states working

### Phase B Success Metrics  
- ✅ User listing loads from Phase 1 API
- ✅ Search and pagination working (if implemented)
- ✅ User cards display real data correctly

### Phase C Success Metrics
- ✅ Analysis data loads from Phase 2 API
- ✅ All 4 tab components show real JSON data
- ✅ Date switching triggers new API calls
- ✅ Multiple analyses per day handled correctly

### Phase D Success Metrics
- ✅ Date navigation is smooth and responsive
- ✅ Loading states provide good user experience
- ✅ Error handling allows graceful recovery
- ✅ Caching improves performance

This plan provides a structured approach to integrate the working APIs with the existing frontend, setting up a solid foundation for Phase 3 features while maintaining a good user experience throughout the development process.