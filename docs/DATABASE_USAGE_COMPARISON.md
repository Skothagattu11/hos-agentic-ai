# Database Usage Comparison: Health Agent Projects

This document outlines the database architecture and table usage differences between the two health-related projects in this repository.

## Project Overview

### 1. **health-agent-main/** - AI Health Analysis System
- **Database**: PostgreSQL (standalone instance)
- **Purpose**: AI-powered health analysis with memory management
- **Architecture**: Agent-based system with persistent user memory

### 2. **hos-fapi-hm-sahha-main/** - Health Metrics Sync API
- **Database**: Supabase (PostgreSQL as a service)
- **Purpose**: Real-time health data synchronization from Sahha API
- **Architecture**: Data pipeline with caching and incremental sync

---

## Database Systems Comparison

| Aspect | health-agent-main | hos-fapi-hm-sahha-main |
|--------|-------------------|------------------------|
| **Database Type** | PostgreSQL (self-hosted) | Supabase (PostgreSQL SaaS) |
| **Connection Method** | `asyncpg` direct connection | Supabase Python client |
| **Environment Variable** | `DATABASE_URL` | `SUPABASE_URL` + `SUPABASE_KEY` |
| **Purpose** | User memory & AI analysis storage | Health data sync & metrics storage |
| **Data Persistence** | Long-term user preferences & history | Real-time health metrics & sync tracking |

---

## Table Usage Analysis

### health-agent-main Database Tables

The health-agent-main project uses a **custom PostgreSQL database** with the following table:

#### **memory** (Custom table for AI analysis memory)
```sql
-- Table structure (inferred from code)
CREATE TABLE memory (
    profile_id TEXT PRIMARY KEY,
    user_preferences JSONB,
    health_goals JSONB,
    dietary_restrictions JSONB,
    lifestyle_context JSONB,
    medical_conditions JSONB,
    last_analysis_result TEXT,
    analysis_insights JSONB,
    last_nutrition_plan JSONB,
    last_routine_plan JSONB,
    last_behavior_analysis JSONB,
    -- Archetype-specific routine plans
    transformation_seeker_plan JSONB,
    systematic_improver_plan JSONB,
    peak_performer_plan JSONB,
    resilience_rebuilder_plan JSONB,
    connected_explorer_plan JSONB,
    foundation_builder_plan JSONB,
    last_archetype TEXT,
    health_trends JSONB,
    improvement_areas JSONB,
    success_patterns JSONB,
    total_analyses INTEGER DEFAULT 0,
    last_analysis_date TIMESTAMP,
    nutrition_plan_date TIMESTAMP,
    routine_plan_date TIMESTAMP,
    behavior_analysis_date TIMESTAMP
);
```

**Usage Pattern:**
- Stores AI analysis results and user preferences
- Tracks analysis history and patterns
- Manages archetype-specific recommendations
- Supports follow-up analysis by referencing previous results

---

### hos-fapi-hm-sahha-main Database Tables

The hos-fapi-hm-sahha-main project uses **Supabase** with the following tables actively used in the codebase:

#### **Core Health Data Tables**

1. **profiles** - User profile management
   ```sql
   -- Primary user profile table
   - user_id (uuid, FK to users)
   - sahha_external_id (text, unique)
   - sahha_profile_created_at (timestamp)
   - account_id (text)
   - last_webhook_received_at (timestamp)
   - data (jsonb)
   ```

2. **users** - User authentication
   ```sql
   -- Firebase user authentication
   - id (uuid, PK)
   - firebase_uid (text, unique)
   - email (text, unique)
   - display_name (text)
   - photo_url (text)
   ```

3. **biomarkers** - Detailed health metrics
   ```sql
   -- Detailed health biomarkers from Sahha
   - user_id (uuid, FK)
   - profile_id (text, FK)
   - sahha_biomarker_id (text)
   - value (text)
   - unit (text)
   - category (text) -- activity, sleep, body, etc.
   - type (text)
   - data (jsonb)
   - start_date_time (timestamp)
   - end_date_time (timestamp)
   - sync_date (date)
   - is_latest_for_date (boolean)
   ```

4. **scores** - Health scoring metrics
   ```sql
   -- Health scores (readiness, sleep, activity, mental_wellbeing)
   - user_id (uuid, FK)
   - profile_id (text, FK)
   - sahha_score_id (text)
   - type (text) -- readiness, sleep, activity, mental_wellbeing
   - score (double precision)
   - state (text)
   - factors (jsonb)
   - data_sources (array)
   - score_date_time (timestamp)
   - sync_date (date)
   - is_latest_for_date (boolean)
   ```

5. **archetypes** - User personality archetypes
   ```sql
   -- Health archetypes from Sahha
   - user_id (uuid, FK)
   - profile_id (text, FK)
   - sahha_archetype_id (text)
   - name (text)
   - value (text)
   - data (jsonb)
   - sync_date (date)
   - is_latest_for_date (boolean)
   ```

#### **Sync & Management Tables**

6. **sync_jobs** - Data synchronization tracking
   ```sql
   -- Tracks data sync operations
   - profile_id (text, FK)
   - job_type (varchar)
   - status (text)
   - current_message (text)
   - started_at (timestamp)
   - completed_at (timestamp)
   - success (boolean)
   - metadata (jsonb)
   - results (jsonb)
   - sync_date (date)
   ```

7. **webhook_events** - Webhook processing
   ```sql
   -- Sahha webhook event tracking
   - event_type (text)
   - external_id (text)
   - signature (text)
   - payload (jsonb)
   - processed (boolean)
   - processed_at (timestamp)
   - error (text)
   ```

#### **Unused Tables in Codebase**
The following tables exist in the schema but are **NOT actively used** by hos-fapi-hm-sahha-main:
- `analytics_events`
- `kpi_snapshots`
- `notification_log`
- `notification_queue`
- `notification_templates`
- `schedule_items`
- `task_completions`
- `user_context_flags`
- `user_notification_preferences`
- `user_sessions`
- `waitlist`
- `wellness_plans`

---

## Key Differences

### 1. **Database Architecture**
- **health-agent-main**: Single custom table (`memory`) for AI analysis persistence
- **hos-fapi-hm-sahha-main**: Multiple normalized tables for health data management

### 2. **Data Flow**
- **health-agent-main**: Writes analysis results → Reads for follow-up analysis
- **hos-fapi-hm-sahha-main**: Syncs external data → Serves cached metrics

### 3. **Data Relationships**
- **health-agent-main**: No foreign key relationships (single table design)
- **hos-fapi-hm-sahha-main**: Complex relationships with users ↔ profiles ↔ health data

### 4. **Sync Strategy**
- **health-agent-main**: Manual memory updates during analysis
- **hos-fapi-hm-sahha-main**: Automated incremental sync with tracking columns

### 5. **Data Retention**
- **health-agent-main**: Long-term user preferences and analysis history
- **hos-fapi-hm-sahha-main**: Time-series health metrics with date-based tracking

---

## Integration Potential

While these projects use different databases, they could potentially integrate by:

1. **Shared User Identification**: Both systems could reference the same `profile_id`
2. **Data Exchange**: health-agent-main could query hos-fapi-hm-sahha-main APIs for current health data
3. **Analysis Enhancement**: AI analysis could incorporate real-time metrics from the sync API
4. **Unified Memory**: health-agent-main could store references to health data rather than duplicating it

---

## Environment Configuration

### health-agent-main
```env
DATABASE_URL=postgresql://username:password@localhost:5432/health_analysis
OPENAI_API_KEY=your_openai_api_key_here
```

### hos-fapi-hm-sahha-main
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anonymous_key
SAHHA_CLIENT_ID=your_client_id
SAHHA_CLIENT_SECRET=your_client_secret
```

This separation allows each system to be developed, deployed, and scaled independently while maintaining the potential for future integration.