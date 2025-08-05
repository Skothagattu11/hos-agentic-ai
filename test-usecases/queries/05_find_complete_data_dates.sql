-- ==================================================================
-- FIND DATES WITH COMPLETE DATA ACROSS ALL TABLES
-- Purpose: Find dates where scores, biomarkers, AND archetypes all have data
-- ==================================================================

-- Replace 'USER_ID_HERE' with actual user ID before running

-- 1. FIND OVERLAPPING DATE RANGES
WITH date_ranges AS (
  SELECT 
    'scores' as table_name,
    MIN(DATE(score_date_time)) as min_date,
    MAX(DATE(score_date_time)) as max_date
  FROM scores 
  WHERE profile_id = 'USER_ID_HERE'
  
  UNION ALL
  
  SELECT 
    'biomarkers' as table_name,
    MIN(DATE(created_at)) as min_date,
    MAX(DATE(created_at)) as max_date
  FROM biomarkers 
  WHERE profile_id = 'USER_ID_HERE'
  
  UNION ALL
  
  SELECT 
    'archetypes' as table_name,
    MIN(DATE(created_at)) as min_date,
    MAX(DATE(created_at)) as max_date
  FROM archetypes 
  WHERE profile_id = 'USER_ID_HERE'
)
SELECT 
  MAX(min_date) as overlap_start_date,
  MIN(max_date) as overlap_end_date,
  MIN(max_date) - MAX(min_date) + 1 as potential_overlap_days
FROM date_ranges;

-- 2. FIND ALL DATES WITH COMPLETE DATA (ALL THREE TABLES)
WITH all_dates AS (
  -- Get all distinct dates from scores
  SELECT DISTINCT DATE(score_date_time) as date
  FROM scores 
  WHERE profile_id = 'USER_ID_HERE'
),
data_availability AS (
  SELECT 
    ad.date,
    COALESCE(s.score_count, 0) as scores_count,
    COALESCE(b.biomarker_count, 0) as biomarkers_count,
    COALESCE(a.archetype_count, 0) as archetypes_count,
    CASE 
      WHEN COALESCE(s.score_count, 0) > 0 
       AND COALESCE(b.biomarker_count, 0) > 0 
       AND COALESCE(a.archetype_count, 0) > 0 
      THEN TRUE
      ELSE FALSE
    END as has_complete_data
  FROM all_dates ad
  LEFT JOIN (
    SELECT DATE(score_date_time) as date, COUNT(*) as score_count
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(score_date_time)
  ) s ON ad.date = s.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as biomarker_count
    FROM biomarkers 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) b ON ad.date = b.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as archetype_count
    FROM archetypes 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) a ON ad.date = a.date
)
SELECT 
  date,
  scores_count,
  biomarkers_count,
  archetypes_count,
  CASE 
    WHEN has_complete_data THEN '✅ Complete'
    ELSE '❌ Incomplete'
  END as data_status
FROM data_availability
WHERE has_complete_data = TRUE
ORDER BY date DESC
LIMIT 20;

-- 3. FIND THE MOST RECENT 5 CONSECUTIVE DATES WITH COMPLETE DATA
WITH complete_dates AS (
  SELECT 
    ad.date,
    CASE 
      WHEN COALESCE(s.score_count, 0) > 0 
       AND COALESCE(b.biomarker_count, 0) > 0 
       AND COALESCE(a.archetype_count, 0) > 0 
      THEN TRUE
      ELSE FALSE
    END as has_complete_data
  FROM (
    SELECT DISTINCT DATE(score_date_time) as date
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
  ) ad
  LEFT JOIN (
    SELECT DATE(score_date_time) as date, COUNT(*) as score_count
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(score_date_time)
  ) s ON ad.date = s.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as biomarker_count
    FROM biomarkers 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) b ON ad.date = b.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as archetype_count
    FROM archetypes 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) a ON ad.date = a.date
),
date_sequences AS (
  SELECT 
    date,
    has_complete_data,
    date - (ROW_NUMBER() OVER (PARTITION BY has_complete_data ORDER BY date))::int as grp
  FROM complete_dates
  WHERE has_complete_data = TRUE
),
consecutive_groups AS (
  SELECT 
    MIN(date) as start_date,
    MAX(date) as end_date,
    COUNT(*) as consecutive_days,
    ARRAY_AGG(date ORDER BY date DESC) as dates_in_sequence
  FROM date_sequences
  GROUP BY grp
  HAVING COUNT(*) >= 5
)
SELECT 
  start_date,
  end_date,
  consecutive_days,
  dates_in_sequence[1:5] as last_5_dates_for_testing
FROM consecutive_groups
ORDER BY end_date DESC
LIMIT 1;

-- 4. SUMMARY STATISTICS
SELECT 
  COUNT(CASE WHEN has_complete_data THEN 1 END) as total_complete_days,
  COUNT(*) as total_days_with_any_data,
  ROUND(COUNT(CASE WHEN has_complete_data THEN 1 END)::numeric / COUNT(*)::numeric * 100, 2) as complete_data_percentage,
  MIN(CASE WHEN has_complete_data THEN date END) as earliest_complete_date,
  MAX(CASE WHEN has_complete_data THEN date END) as latest_complete_date
FROM (
  SELECT 
    ad.date,
    CASE 
      WHEN COALESCE(s.score_count, 0) > 0 
       AND COALESCE(b.biomarker_count, 0) > 0 
       AND COALESCE(a.archetype_count, 0) > 0 
      THEN TRUE
      ELSE FALSE
    END as has_complete_data
  FROM (
    SELECT DISTINCT DATE(score_date_time) as date
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
  ) ad
  LEFT JOIN (
    SELECT DATE(score_date_time) as date, COUNT(*) as score_count
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(score_date_time)
  ) s ON ad.date = s.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as biomarker_count
    FROM biomarkers 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) b ON ad.date = b.date
  LEFT JOIN (
    SELECT DATE(created_at) as date, COUNT(*) as archetype_count
    FROM archetypes 
    WHERE profile_id = 'USER_ID_HERE'
    GROUP BY DATE(created_at)
  ) a ON ad.date = a.date
) data_check;