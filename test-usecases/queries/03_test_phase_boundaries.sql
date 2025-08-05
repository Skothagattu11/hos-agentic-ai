-- ==================================================================
-- TEST PHASE BOUNDARIES CALCULATION
-- Purpose: Identify the exact 5 dates for progressive testing phases
-- ==================================================================

-- Replace 'USER_ID_HERE' with actual user ID before running

-- 5. GET THE LAST 5 DISTINCT DATES WITH DATA (FOR TEST PHASES)
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

-- 6. VALIDATE DATA CONSISTENCY ACROSS TABLES FOR THESE DATES
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