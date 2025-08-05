-- ==================================================================
-- RUN ALL DISCOVERY QUERIES FOR USER
-- Purpose: Complete database discovery for adaptability testing
-- ==================================================================

-- IMPORTANT: Replace 'USER_ID_HERE' with actual user ID before running
-- Example: 'mbzXA48h4ASzre407KoFMepfyGv1'

\echo '=== STARTING DATABASE DISCOVERY FOR USER ==='
\echo 'User ID: USER_ID_HERE'
\echo ''

-- ==================================================================
-- 1. USER DATE RANGE DISCOVERY
-- ==================================================================
\echo '1. DATE RANGE DISCOVERY ACROSS ALL TABLES'
\echo '----------------------------------------'

SELECT 
    'scores' as table_name,
    profile_id,
    MIN(score_date_time) as earliest_date,
    MAX(score_date_time) as latest_date,
    COUNT(DISTINCT DATE(score_date_time)) as total_days_with_data,
    COUNT(*) as total_records,
    EXTRACT(DAYS FROM (MAX(score_date_time) - MIN(score_date_time))) as date_span_days
FROM scores 
WHERE profile_id = 'USER_ID_HERE'
GROUP BY profile_id

UNION ALL

SELECT 
    'biomarkers' as table_name,
    profile_id,
    MIN(created_at) as earliest_date,
    MAX(created_at) as latest_date,
    COUNT(DISTINCT DATE(created_at)) as total_days_with_data,
    COUNT(*) as total_records,
    EXTRACT(DAYS FROM (MAX(created_at) - MIN(created_at))) as date_span_days
FROM biomarkers 
WHERE profile_id = 'USER_ID_HERE'
GROUP BY profile_id

UNION ALL

SELECT 
    'archetypes' as table_name,
    profile_id,
    MIN(created_at) as earliest_date,
    MAX(created_at) as latest_date,
    COUNT(DISTINCT DATE(created_at)) as total_days_with_data,
    COUNT(*) as total_records,
    EXTRACT(DAYS FROM (MAX(created_at) - MIN(created_at))) as date_span_days
FROM archetypes 
WHERE profile_id = 'USER_ID_HERE'
GROUP BY profile_id

ORDER BY table_name;

\echo ''
\echo '=== TEST PHASE BOUNDARIES ==='
\echo ''


[
  {
    "table_name": "archetypes",
    "profile_id": "mbzXA48h4ASzre407KoFMepfyGv1",
    "earliest_date": "2025-06-27 03:18:06.03369+00",
    "latest_date": "2025-08-04 03:14:32.909378+00",
    "total_days_with_data": 8,
    "total_records": 866,
    "date_span_days": "37"
  },
  {
    "table_name": "biomarkers",
    "profile_id": "mbzXA48h4ASzre407KoFMepfyGv1",
    "earliest_date": "2025-06-27 03:17:37.939904+00",
    "latest_date": "2025-08-04 03:13:56.254752+00",
    "total_days_with_data": 11,
    "total_records": 964,
    "date_span_days": "37"
  },
  {
    "table_name": "scores",
    "profile_id": "mbzXA48h4ASzre407KoFMepfyGv1",
    "earliest_date": "2025-05-29 04:00:00+00",
    "latest_date": "2025-08-03 04:00:00+00",
    "total_days_with_data": 67,
    "total_records": 322,
    "date_span_days": "66"
  }
]

-- ==================================================================
-- 2. GET THE LAST 5 DISTINCT DATES FOR TEST PHASES
-- ==================================================================
WITH last_dates AS (
  SELECT DISTINCT DATE(score_date_time) as available_date
  FROM scores 
  WHERE profile_id = 'USER_ID_HERE'
    AND score_date_time IS NOT NULL
  ORDER BY available_date DESC
  LIMIT 5
),
numbered_dates AS (
  SELECT 
    available_date,
    ROW_NUMBER() OVER (ORDER BY available_date DESC) as days_from_latest
  FROM last_dates
)
SELECT 
  available_date,
  days_from_latest,
  available_date::text as date_string_format,
  CASE days_from_latest
    WHEN 5 THEN 'Phase 1: Baseline Analysis'
    WHEN 4 THEN 'Phase 2: +1 Day Addition'
    WHEN 3 THEN 'Phase 3: +1 Day Addition' 
    WHEN 2 THEN 'Phase 4: +2 Days Addition'
    WHEN 1 THEN 'Phase 5: Complete Dataset'
  END as test_phase_description,
  CASE days_from_latest
    WHEN 5 THEN 'initial'
    ELSE 'follow_up'
  END as expected_analysis_type,
  CASE days_from_latest
    WHEN 5 THEN '7+ days'
    WHEN 4 THEN '1 day'
    WHEN 3 THEN '1 day'
    WHEN 2 THEN '2 days'
    WHEN 1 THEN '1 day'
  END as expected_data_increment
FROM numbered_dates
ORDER BY available_date;

\echo ''
\echo '=== DATA CONSISTENCY CHECK ==='
\echo ''


[
  {
    "available_date": "2025-07-30",
    "days_from_latest": 5,
    "date_string_format": "2025-07-30",
    "test_phase_description": "Phase 1: Baseline Analysis",
    "expected_analysis_type": "initial",
    "expected_data_increment": "7+ days"
  },
  {
    "available_date": "2025-07-31",
    "days_from_latest": 4,
    "date_string_format": "2025-07-31",
    "test_phase_description": "Phase 2: +1 Day Addition",
    "expected_analysis_type": "follow_up",
    "expected_data_increment": "1 day"
  },
  {
    "available_date": "2025-08-01",
    "days_from_latest": 3,
    "date_string_format": "2025-08-01",
    "test_phase_description": "Phase 3: +1 Day Addition",
    "expected_analysis_type": "follow_up",
    "expected_data_increment": "1 day"
  },
  {
    "available_date": "2025-08-02",
    "days_from_latest": 2,
    "date_string_format": "2025-08-02",
    "test_phase_description": "Phase 4: +2 Days Addition",
    "expected_analysis_type": "follow_up",
    "expected_data_increment": "2 days"
  },
  {
    "available_date": "2025-08-03",
    "days_from_latest": 1,
    "date_string_format": "2025-08-03",
    "test_phase_description": "Phase 5: Complete Dataset",
    "expected_analysis_type": "follow_up",
    "expected_data_increment": "1 day"
  }
]

-- ==================================================================
-- 3. VALIDATE DATA CONSISTENCY ACROSS TABLES
-- ==================================================================
WITH test_dates AS (
  SELECT DISTINCT DATE(score_date_time) as test_date
  FROM scores 
  WHERE profile_id = 'USER_ID_HERE'
  ORDER BY test_date DESC
  LIMIT 5
)
SELECT 
  td.test_date,
  COALESCE(s.score_count, 0) as scores_available,
  COALESCE(b.biomarker_count, 0) as biomarkers_available,
  COALESCE(a.archetype_count, 0) as archetypes_available,
  CASE 
    WHEN COALESCE(s.score_count, 0) > 0 
     AND COALESCE(b.biomarker_count, 0) > 0 
     AND COALESCE(a.archetype_count, 0) > 0 
    THEN '✅ Complete'
    WHEN COALESCE(s.score_count, 0) > 0 
    THEN '⚠️ Partial (Missing bio/arch)'
    ELSE '❌ No Data'
  END as data_completeness
FROM test_dates td
LEFT JOIN (
  SELECT DATE(score_date_time) as date, COUNT(*) as score_count
  FROM scores 
  WHERE profile_id = 'USER_ID_HERE'
  GROUP BY DATE(score_date_time)
) s ON td.test_date = s.date
LEFT JOIN (
  SELECT DATE(created_at) as date, COUNT(*) as biomarker_count
  FROM biomarkers 
  WHERE profile_id = 'USER_ID_HERE'
  GROUP BY DATE(created_at)
) b ON td.test_date = b.date
LEFT JOIN (
  SELECT DATE(created_at) as date, COUNT(*) as archetype_count
  FROM archetypes 
  WHERE profile_id = 'USER_ID_HERE'
  GROUP BY DATE(created_at)
) a ON td.test_date = a.date
ORDER BY td.test_date DESC;

\echo ''
\echo '=== EXISTING ANALYSIS MEMORY CHECK ==='
\echo ''



[
  {
    "test_date": "2025-08-03",
    "scores_available": 5,
    "biomarkers_available": 0,
    "archetypes_available": 0,
    "data_completeness": "⚠️ Partial (Missing bio/arch)"
  },
  {
    "test_date": "2025-08-02",
    "scores_available": 5,
    "biomarkers_available": 0,
    "archetypes_available": 0,
    "data_completeness": "⚠️ Partial (Missing bio/arch)"
  },
  {
    "test_date": "2025-08-01",
    "scores_available": 5,
    "biomarkers_available": 0,
    "archetypes_available": 0,
    "data_completeness": "⚠️ Partial (Missing bio/arch)"
  },
  {
    "test_date": "2025-07-31",
    "scores_available": 5,
    "biomarkers_available": 0,
    "archetypes_available": 0,
    "data_completeness": "⚠️ Partial (Missing bio/arch)"
  },
  {
    "test_date": "2025-07-30",
    "scores_available": 5,
    "biomarkers_available": 0,
    "archetypes_available": 0,
    "data_completeness": "⚠️ Partial (Missing bio/arch)"
  }
]
-- ==================================================================
-- 4. CHECK EXISTING ANALYSIS MEMORY STATE
-- ==================================================================
SELECT 
    'Current Analysis Memory State' as check_type,
    COUNT(*) as total_analyses,
    COUNT(CASE WHEN analysis_type = 'initial' THEN 1 END) as initial_analyses,
    COUNT(CASE WHEN analysis_type = 'follow_up' THEN 1 END) as followup_analyses,
    MIN(analysis_date) as earliest_analysis,
    MAX(analysis_date) as latest_analysis,
    STRING_AGG(DISTINCT archetype, ', ' ORDER BY archetype) as archetypes_used
FROM analysis_memory 
WHERE profile_id = 'USER_ID_HERE';

\echo ''
\echo '=== PROFILE EXISTENCE CHECK ==='
\echo ''



[
  {
    "check_type": "Current Analysis Memory State",
    "total_analyses": 2,
    "initial_analyses": 1,
    "followup_analyses": 1,
    "earliest_analysis": "2025-08-05 14:48:03.963349+00",
    "latest_analysis": "2025-08-05 15:04:56.411194+00",
    "archetypes_used": "Peak Performer"
  }
]
-- ==================================================================
-- 5. PROFILE EXISTENCE CHECK
-- ==================================================================
SELECT 
    'Profile Check' as check_type,
    CASE WHEN EXISTS (SELECT 1 FROM profiles WHERE id = 'USER_ID_HERE') 
         THEN '✅ Profile Exists' 
         ELSE '❌ Profile Missing' 
    END as profile_status,
    (SELECT created_at FROM profiles WHERE id = 'USER_ID_HERE') as profile_created_date;


    [
  {
    "check_type": "Profile Check",
    "profile_status": "✅ Profile Exists",
    "profile_created_date": "2025-08-05 11:02:51.32285+00"
  }
]

\echo ''
\echo '=== DATABASE DISCOVERY COMPLETE ==='
\echo 'Review results above to plan test phases'
\echo ''