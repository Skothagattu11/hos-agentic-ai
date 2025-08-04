# SQL Database Migration Plan: health-agent-main → Supabase PostgreSQL

This document outlines the strategy for migrating health-agent-main to use the same PostgreSQL database as hos-fapi-hm-sahha-main while **keeping the existing SQL implementation** with `asyncpg`.

## Migration Overview

### What We're Doing
- **Keep**: All existing SQL queries and `asyncpg` implementation
- **Change**: Database URL to point to Supabase PostgreSQL database
- **Add**: Create `ai_memory` table in the existing Supabase database
- **Gain**: Access to all health data tables used by hos-fapi-hm-sahha-main

### What We're NOT Doing
- ❌ Converting to Supabase client library
- ❌ Rewriting SQL queries
- ❌ Changing authentication methods
- ❌ Modifying existing code patterns

---

## 🎯 **Simplified Migration Strategy**

This is essentially a **"change database URL + add table"** migration with minimal code changes.

### Current Architecture
```
health-agent-main → PostgreSQL DB (standalone) → memory table
```

### Target Architecture  
```
health-agent-main → Supabase PostgreSQL DB → ai_memory + all health tables
hos-fapi-hm-sahha-main → Same Supabase PostgreSQL DB → health tables
```

---

## 📋 **Step-by-Step Migration Plan**

### Phase 1: **Database Setup** (30 minutes)

#### 1.1 Create AI Memory Table in Supabase Database
```sql
-- Connect to Supabase PostgreSQL database and run:
CREATE TABLE IF NOT EXISTS public.ai_memory (
    profile_id text PRIMARY KEY,
    user_preferences jsonb DEFAULT '{}',
    health_goals jsonb DEFAULT '{}',
    dietary_restrictions jsonb DEFAULT '{}',
    lifestyle_context jsonb DEFAULT '{}',
    medical_conditions jsonb DEFAULT '{}',
    last_analysis_result text,
    analysis_insights jsonb DEFAULT '{}',
    last_nutrition_plan jsonb,
    last_routine_plan jsonb,
    last_behavior_analysis jsonb,
    
    -- Archetype-specific routine plans
    transformation_seeker_plan jsonb,
    systematic_improver_plan jsonb,
    peak_performer_plan jsonb,
    resilience_rebuilder_plan jsonb,
    connected_explorer_plan jsonb,
    foundation_builder_plan jsonb,
    last_archetype text,
    
    -- Trends and insights
    health_trends jsonb DEFAULT '{}',
    improvement_areas jsonb DEFAULT '{}',
    success_patterns jsonb DEFAULT '{}',
    
    -- Tracking counters
    total_analyses integer DEFAULT 0,
    last_analysis_date timestamp with time zone,
    nutrition_plan_date timestamp with time zone,
    routine_plan_date timestamp with time zone,
    behavior_analysis_date timestamp with time zone,
    
    -- Standard timestamps (following Supabase pattern)
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_memory_profile_id ON public.ai_memory(profile_id);
CREATE INDEX IF NOT EXISTS idx_ai_memory_last_analysis_date ON public.ai_memory(last_analysis_date);

-- Add trigger for updated_at (following Supabase pattern)
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER handle_ai_memory_updated_at
    BEFORE UPDATE ON public.ai_memory
    FOR EACH ROW
    EXECUTE PROCEDURE public.handle_updated_at();
```

#### 1.2 Get Supabase Database Connection Details
You'll need the direct PostgreSQL connection string from Supabase:
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

### Phase 2: **Code Changes** (15 minutes)

#### 2.1 Update Environment Variables
```env
# OLD - Remove this
# DATABASE_URL=postgresql://username:password@localhost:5432/health_analysis

# NEW - Add Supabase PostgreSQL URL
DATABASE_URL=postgresql://postgres:[your-password]@db.[your-project-ref].supabase.co:5432/postgres
```

#### 2.2 Update Table Name in Memory Manager
```python
# File: health_agents/memory_manager.py

# Change all occurrences of "memory" table to "ai_memory"
# Example changes:

# OLD
query = """
    SELECT profile_id, user_preferences, health_goals...
    FROM memory 
    WHERE profile_id = $1
"""

# NEW  
query = """
    SELECT profile_id, user_preferences, health_goals...
    FROM ai_memory 
    WHERE profile_id = $1
"""

# Apply this change to all queries:
# - get_user_memory()
# - create_user_memory() 
# - update_analysis_result()
# - update_nutrition_plan()
# - update_routine_plan()
# - update_behavior_analysis()
# - update_archetype_routine_plan()
# - update_analysis_results()
```

### Phase 3: **Data Migration** (30 minutes)

#### 3.1 Export Existing Data
```python
# Create migration script: migrate_memory_data.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def migrate_data():
    load_dotenv()
    
    # Connect to OLD database
    old_db_url = "postgresql://username:password@localhost:5432/health_analysis"
    old_conn = await asyncpg.connect(old_db_url)
    
    # Connect to NEW database (Supabase)
    new_db_url = os.getenv("DATABASE_URL")  # Supabase URL
    new_conn = await asyncpg.connect(new_db_url)
    
    try:
        # Export all memory records
        print("Exporting data from old database...")
        rows = await old_conn.fetch("SELECT * FROM memory")
        print(f"Found {len(rows)} memory records")
        
        # Import to new database
        print("Importing data to Supabase database...")
        for row in rows:
            await new_conn.execute("""
                INSERT INTO ai_memory (
                    profile_id, user_preferences, health_goals, dietary_restrictions,
                    lifestyle_context, medical_conditions, last_analysis_result,
                    analysis_insights, last_nutrition_plan, last_routine_plan,
                    last_behavior_analysis, transformation_seeker_plan, 
                    systematic_improver_plan, peak_performer_plan, 
                    resilience_rebuilder_plan, connected_explorer_plan,
                    foundation_builder_plan, last_archetype, health_trends,
                    improvement_areas, success_patterns, total_analyses,
                    last_analysis_date, nutrition_plan_date, routine_plan_date,
                    behavior_analysis_date
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 
                    $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26
                )
                ON CONFLICT (profile_id) DO UPDATE SET
                    user_preferences = EXCLUDED.user_preferences,
                    health_goals = EXCLUDED.health_goals,
                    -- ... update all fields
                    updated_at = now()
            """, 
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
            row[8], row[9], row[10], row[11], row[12], row[13], row[14], 
            row[15], row[16], row[17], row[18], row[19], row[20], row[21],
            row[22], row[23], row[24], row[25])
        
        print(f"Successfully migrated {len(rows)} records!")
        
        # Verify migration
        count = await new_conn.fetchval("SELECT COUNT(*) FROM ai_memory")
        print(f"Verification: {count} records in ai_memory table")
        
    finally:
        await old_conn.close()
        await new_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
```

### Phase 4: **Testing & Validation** (20 minutes)

#### 4.1 Test Database Connection
```python
# Create test script: test_connection.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    try:
        conn = await asyncpg.connect(database_url)
        
        # Test ai_memory table
        count = await conn.fetchval("SELECT COUNT(*) FROM ai_memory")
        print(f"✅ Connected to Supabase PostgreSQL")
        print(f"✅ ai_memory table has {count} records")
        
        # Test access to health tables
        profiles_count = await conn.fetchval("SELECT COUNT(*) FROM profiles")
        scores_count = await conn.fetchval("SELECT COUNT(*) FROM scores")
        biomarkers_count = await conn.fetchval("SELECT COUNT(*) FROM biomarkers")
        
        print(f"✅ Access to health tables confirmed:")
        print(f"   - profiles: {profiles_count} records")
        print(f"   - scores: {scores_count} records") 
        print(f"   - biomarkers: {biomarkers_count} records")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

#### 4.2 Test Memory Operations
```python
# Test existing memory manager functionality
from health_agents.memory_manager import MemoryManager

async def test_memory_operations():
    # Test with a sample profile_id
    profile_id = "test_profile_123"
    
    manager = MemoryManager()
    await manager.connect()
    
    # Test create
    success = await manager.create_user_memory(
        profile_id,
        user_preferences={"test": "data"},
        health_goals={"goal": "fitness"}
    )
    print(f"✅ Create memory: {success}")
    
    # Test retrieve
    memory = await manager.get_user_memory(profile_id)
    print(f"✅ Retrieve memory: {memory is not None}")
    
    # Test update
    success = await manager.update_analysis_result(
        profile_id, 
        "Test analysis result",
        {"insight": "test insight"}
    )
    print(f"✅ Update analysis: {success}")
    
    await manager.disconnect()
```

---

## 🔧 **Required Code Changes Summary**

### 1. **Environment Variable** (1 change)
```env
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

### 2. **Memory Manager Table Name** (~10 changes)
Replace all `"memory"` with `"ai_memory"` in:
- `health_agents/memory_manager.py` (all SQL queries)

### 3. **Optional: Enhanced Integration**
Add methods to access health data:
```python
# Add to memory_manager.py
async def get_user_health_data(self, profile_id: str, days: int = 7):
    """Get health data from the same database"""
    query = """
        SELECT * FROM scores 
        WHERE profile_id = $1 
        AND score_date_time >= NOW() - INTERVAL '%s days'
        ORDER BY score_date_time DESC
    """
    return await self.connection.fetch(query, profile_id, days)

async def get_user_biomarkers(self, profile_id: str, category: str = None):
    """Get biomarkers from the same database"""
    if category:
        query = "SELECT * FROM biomarkers WHERE profile_id = $1 AND category = $2"
        return await self.connection.fetch(query, profile_id, category)
    else:
        query = "SELECT * FROM biomarkers WHERE profile_id = $1"
        return await self.connection.fetch(query, profile_id)
```

---

## ⚠️ **Potential Issues & Solutions**

### 1. **Connection Limits**
**Issue**: Both systems connecting to same database might hit connection limits
**Solution**: 
```python
# Add connection pooling
import asyncpg

async def create_connection_pool():
    return await asyncpg.create_pool(
        database_url,
        min_size=5,
        max_size=20,
        statement_cache_size=0
    )
```

### 2. **Profile ID Compatibility**  
**Issue**: health-agent-main uses string profile IDs, health tables expect specific format
**Solution**: No changes needed - string profile IDs will work fine

### 3. **Concurrent Access**
**Issue**: Both systems writing to database simultaneously
**Solution**: Use proper transaction isolation and avoid long-running transactions

### 4. **Authentication**
**Issue**: Supabase might require authentication even for direct PostgreSQL access
**Solution**: Use the direct PostgreSQL connection (bypasses Supabase auth layer)

---

## 🚀 **Migration Timeline**

| Task | Duration | Description |
|------|----------|-------------|
| **Setup Database** | 30 min | Create ai_memory table, get connection string |
| **Update Code** | 15 min | Change table name and environment variable |
| **Data Migration** | 30 min | Export/import existing memory data |
| **Testing** | 20 min | Verify connection and functionality |
| **Deployment** | 10 min | Update production environment |
| **Total** | **~2 hours** | Complete migration |

---

## 📋 **Migration Checklist**

- [ ] **Get Supabase PostgreSQL connection string**
- [ ] **Create ai_memory table in Supabase database**
- [ ] **Add indexes and triggers**
- [ ] **Update DATABASE_URL environment variable**
- [ ] **Change table name from "memory" to "ai_memory" in code**
- [ ] **Test database connection**
- [ ] **Run data migration script**
- [ ] **Verify data integrity**
- [ ] **Test all memory operations**
- [ ] **Test health data access (optional)**
- [ ] **Deploy to production**
- [ ] **Monitor for issues**

---

## 🎉 **Benefits After Migration**

### 1. **Immediate Access to Health Data**
```python
# Now possible in health-agent-main:
async def enhanced_analysis(self, profile_id):
    # Get AI memory
    memory = await self.get_user_memory(profile_id)
    
    # Get current health scores (same database!)
    recent_scores = await self.connection.fetch("""
        SELECT * FROM scores 
        WHERE profile_id = $1 
        AND score_date_time >= NOW() - INTERVAL '7 days'
    """, profile_id)
    
    # Get biomarkers (same database!)
    biomarkers = await self.connection.fetch("""
        SELECT * FROM biomarkers 
        WHERE profile_id = $1 
        AND category = 'activity'
    """, profile_id)
    
    # Enhanced AI analysis with real-time data!
    return await self.analyze_with_health_data(memory, recent_scores, biomarkers)
```

### 2. **Unified Data Platform**
- Single database for all health-related data
- Consistent backup and monitoring
- Simplified infrastructure

### 3. **Enhanced Analysis Capabilities**
- AI can use real-time biomarkers in analysis
- Better personalization with current health state
- Historical trend analysis across all data types

---

**🎯 Bottom Line**: This is a **low-risk, high-reward migration** that requires minimal code changes but provides access to the entire health data ecosystem. The existing SQL code continues to work with just table name changes and a new database URL.