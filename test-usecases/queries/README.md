# Test Use Cases - Database Queries

This folder contains SQL queries for discovering and validating user data before running adaptability tests.

## Query Files

### 1. `01_user_date_range_discovery.sql`
**Purpose**: Find the complete date range and data availability for a user across all tables.

**What it does**:
- Shows earliest and latest dates for scores, biomarkers, and archetypes
- Counts total days with data and total records
- Calculates date span in days

**Usage**:
1. Replace `'USER_ID_HERE'` with actual user ID
2. Run in Supabase SQL editor or database client
3. Review results to understand data availability

### 2. `02_last_10_days_data_availability.sql`
**Purpose**: Check data availability and density for the last 10 days.

**What it does**:
- Shows day-by-day breakdown of data for last 10 days
- Counts records per day for each table
- Lists available data types per day
- Identifies data gaps

**Usage**:
1. Replace `'USER_ID_HERE'` with actual user ID
2. Run to see recent data patterns
3. Use to verify sufficient data for testing

### 3. `03_test_phase_boundaries.sql`
**Purpose**: Identify the exact 5 dates for progressive testing phases.

**What it does**:
- Finds last 5 distinct dates with data
- Maps dates to test phases (Phase 1-5)
- Validates data consistency across tables
- Shows expected analysis types and data increments

**Usage**:
1. Replace `'USER_ID_HERE'` with actual user ID
2. Run to get exact test phase dates
3. Use results to configure test scripts

### 4. `04_existing_analysis_memory_check.sql`
**Purpose**: Check if user already has analysis records that might interfere with testing.

**What it does**:
- Counts existing analysis memory records
- Shows memory chain integrity
- Checks profile existence
- Identifies potential conflicts

**Usage**:
1. Replace `'USER_ID_HERE'` with actual user ID
2. Run before testing to check current state
3. Use to decide if cleanup is needed

## How to Use These Queries

### Step 1: Replace User ID
In each query file, replace `'USER_ID_HERE'` with the actual user ID:
```sql
-- Replace this
WHERE profile_id = 'USER_ID_HERE'

-- With actual user ID
WHERE profile_id = 'mbzXA48h4ASzre407KoFMepfyGv1'
```

### Step 2: Run Queries in Order
1. **Date Range Discovery** - Understand overall data availability
2. **Last 10 Days Check** - Confirm recent data density
3. **Test Phase Boundaries** - Get exact test dates
4. **Memory Check** - Verify clean state for testing

### Step 3: Document Results
Save query results in the `results/` folder for reference during test script development.

## Expected Results Format

### Date Range Discovery
```
table_name | earliest_date | latest_date | total_days_with_data | total_records
scores     | 2025-07-20   | 2025-08-05  | 16                  | 480
biomarkers | 2025-07-20   | 2025-08-05  | 16                  | 320
archetypes | 2025-07-20   | 2025-08-05  | 16                  | 28
```

### Test Phase Boundaries
```
available_date | test_phase_description    | expected_analysis_type | expected_data_increment
2025-08-01    | Phase 1: Baseline        | initial               | 7+ days
2025-08-02    | Phase 2: +1 Day Addition | follow_up             | 1 day
2025-08-03    | Phase 3: +1 Day Addition | follow_up             | 1 day
2025-08-04    | Phase 4: +2 Days Addition| follow_up             | 2 days
2025-08-05    | Phase 5: Complete Dataset| follow_up             | 1 day
```

## Next Steps

After running these queries successfully:
1. Document the discovered dates in `results/`
2. Use the phase boundaries to configure test scripts
3. Plan the phased implementation based on data availability
4. Proceed with test script development

## Notes

- All queries use proper date handling for PostgreSQL/Supabase
- Queries include data validation and integrity checks
- Results should be reviewed for data quality before testing
- Queries are read-only and safe to run on production data