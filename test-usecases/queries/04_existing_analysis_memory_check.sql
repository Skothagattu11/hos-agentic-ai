-- ==================================================================
-- EXISTING ANALYSIS MEMORY CHECK
-- Purpose: Check if user already has analysis records that might interfere with testing
-- ==================================================================

-- Replace 'USER_ID_HERE' with actual user ID before running

-- 7. CHECK EXISTING ANALYSIS MEMORY RECORDS
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

-- 8. DETAILED ANALYSIS MEMORY RECORDS (IF ANY EXIST)
SELECT 
    id,
    analysis_date,
    analysis_type,
    archetype,
    previous_analysis_id,
    CASE WHEN behavior_analysis IS NOT NULL THEN '✅' ELSE '❌' END as has_behavior_analysis,
    CASE WHEN nutrition_plan IS NOT NULL THEN '✅' ELSE '❌' END as has_nutrition_plan,
    CASE WHEN routine_plan IS NOT NULL THEN '✅' ELSE '❌' END as has_routine_plan,
    CASE WHEN engagement_metrics IS NOT NULL THEN '✅' ELSE '❌' END as has_engagement_metrics
FROM analysis_memory 
WHERE profile_id = 'USER_ID_HERE'
ORDER BY analysis_date DESC;

-- 9. MEMORY CHAIN INTEGRITY CHECK (IF RECORDS EXIST)
WITH memory_chain AS (
  SELECT 
    id,
    analysis_date,
    analysis_type,
    previous_analysis_id,
    LAG(id) OVER (ORDER BY analysis_date) as expected_previous_id
  FROM analysis_memory 
  WHERE profile_id = 'USER_ID_HERE'
  ORDER BY analysis_date
)
SELECT 
    id,
    analysis_date,
    analysis_type,
    previous_analysis_id,
    expected_previous_id,
    CASE 
      WHEN previous_analysis_id IS NULL AND expected_previous_id IS NULL THEN '✅ Correct (First)'
      WHEN previous_analysis_id = expected_previous_id THEN '✅ Correct Chain'
      ELSE '❌ Broken Chain'
    END as chain_status
FROM memory_chain
ORDER BY analysis_date;

-- 10. PROFILE EXISTENCE CHECK
SELECT 
    'Profile Check' as check_type,
    CASE WHEN EXISTS (SELECT 1 FROM profiles WHERE id = 'USER_ID_HERE') 
         THEN '✅ Profile Exists' 
         ELSE '❌ Profile Missing' 
    END as profile_status,
    (SELECT created_at FROM profiles WHERE id = 'USER_ID_HERE') as profile_created_date;