-- ==================================================================
-- USER DATE RANGE DISCOVERY
-- Purpose: Find the complete date range and data availability for a user
-- ==================================================================

-- Replace 'USER_ID_HERE' with actual user ID before running
-- Example: 'mbzXA48h4ASzre407KoFMepfyGv1'

-- 1. GET COMPLETE DATE RANGE FOR USER
-- This shows the earliest and latest dates, plus total days with data
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