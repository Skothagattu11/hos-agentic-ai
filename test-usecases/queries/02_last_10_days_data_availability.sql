-- ==================================================================
-- LAST 10 DAYS DATA AVAILABILITY CHECK
-- Purpose: Check data availability and density for the last 10 days
-- ==================================================================

-- Replace 'USER_ID_HERE' with actual user ID before running

-- 2. DETAILED LAST 10 DAYS - SCORES TABLE
SELECT 
    'SCORES - Last 10 Days' as analysis_type,
    DATE(score_date_time) as date,
    COUNT(*) as score_records,
    COUNT(DISTINCT type) as unique_score_types,
    MIN(score_date_time) as first_record_time,
    MAX(score_date_time) as last_record_time,
    ARRAY_AGG(DISTINCT type ORDER BY type) as score_types_available
FROM scores 
WHERE profile_id = 'USER_ID_HERE'
  AND score_date_time >= (
    SELECT MAX(score_date_time) - INTERVAL '10 days' 
    FROM scores 
    WHERE profile_id = 'USER_ID_HERE'
  )
GROUP BY DATE(score_date_time)
ORDER BY date DESC;

-- 3. DETAILED LAST 10 DAYS - BIOMARKERS TABLE  
SELECT 
    'BIOMARKERS - Last 10 Days' as analysis_type,
    DATE(created_at) as date,
    COUNT(*) as biomarker_records,
    COUNT(DISTINCT category) as unique_categories,
    MIN(created_at) as first_record_time,
    MAX(created_at) as last_record_time,
    ARRAY_AGG(DISTINCT category ORDER BY category) as categories_available
FROM biomarkers 
WHERE profile_id = 'USER_ID_HERE'
  AND created_at >= (
    SELECT MAX(created_at) - INTERVAL '10 days' 
    FROM biomarkers 
    WHERE profile_id = 'USER_ID_HERE'
  )
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 4. DETAILED LAST 10 DAYS - ARCHETYPES TABLE
SELECT 
    'ARCHETYPES - Last 10 Days' as analysis_type,
    DATE(created_at) as date,
    COUNT(*) as archetype_records,
    COUNT(DISTINCT name) as unique_archetype_names,
    MIN(created_at) as first_record_time,
    MAX(created_at) as last_record_time,
    STRING_AGG(DISTINCT name, ', ' ORDER BY name) as archetype_names_available
FROM archetypes 
WHERE profile_id = 'USER_ID_HERE'
  AND created_at >= (
    SELECT MAX(created_at) - INTERVAL '10 days' 
    FROM archetypes 
    WHERE profile_id = 'USER_ID_HERE'
  )
GROUP BY DATE(created_at)
ORDER BY date DESC;